from fastapi import APIRouter, Depends, HTTPException
from api.schemas import AssistantRequest, ConfirmRequest, AssistantResponse, MessageResponse , DepositConfirmRequest , WithdrawConfirmRequest
from api.auth import current_user
from api.main import bank
from ai.agent import interpret , summarize_results
from core.market import get_crypto_prices as fetch_crypto_prices
from core.weather import get_weather as fetch_weather
from ai.agent import compose_email_body , answer_gmail_query
from core.web_search import web_search as run_web_search
router = APIRouter()
from core.imagegen import generate_image as run_image_gen
from core.user_calendar_service import add_event as add_calendar_event
from core.gmail_reader_service import search_inbox , build_gmail_query
from core.user_calendar_service import (
    add_event as add_calendar_event,
    find_events_matching, delete_event as delete_calendar_event,
    update_event as update_calendar_event,
)
from logging_config import logger

def _resolve_one_event(refresh_token, date, title_keyword):
    """Shared helper: search, and return either one match, an ambiguity
    message, or a not-found message."""
    result = find_events_matching(refresh_token, date or None, title_keyword)
    if result["error"]:
        return None, result["error"]
    matches = result["events"]
    if not matches:
        return None, "I couldn't find a matching event."
    if len(matches) > 1:
        listing = "\n".join(f"- {m['title']} at {m['start']}" for m in matches)
        return None, f"I found more than one matching event — which did you mean?\n{listing}"
    return matches[0], None

# Formatter for agent's memory. Takes the result of agent interaction and turns it into piece of text that
# can be stored in conversational memory.
def _summarize_for_memory(kind, payload, response):
    if response.text:
        return response.text
    if kind.startswith("propose_"):
        return f"[{kind}] {payload}"
    return f"[{kind}] {response.details}"



@router.post("/assistant", response_model=AssistantResponse)
def assistant(body: AssistantRequest, user=Depends(current_user)):

    """
    Connection between our database memory and ai agent.
    """
    history = bank.storage.recent_messages(user.user_id, limit=10)
    facts = bank.storage.get_memory_facts(user.user_id)
    kind, payload = interpret(body.message, history=history, facts=facts)

    if kind == "propose_transfer":
        response = AssistantResponse(kind="proposal", proposal=payload)

    elif kind == "get_account_details":
        details = {
            "username": user.username,
            "account_number": user.account_number,
            "balance": user.balance,
        }
        response = AssistantResponse(kind="account_details", details=details)

    elif kind == "get_weather_info":
        city = payload.get("city", "")
        result = fetch_weather(city=city)
        response = AssistantResponse(kind="weather_info", details=result)

    elif kind == "get_crypto_prices":
        symbol = payload.get("symbol", "")
        result = fetch_crypto_prices(symbol=symbol)
        response = AssistantResponse(kind="crypto_prices", details=result)

    elif kind == "propose_deposit":
        response = AssistantResponse(kind="proposal_deposit", proposal=payload)

    elif kind == "propose_withdrawal":
        response = AssistantResponse(kind="proposal_withdrawal", proposal=payload)

    elif kind == "compose_email":
        recipient = payload.get("recipient", "")
        purpose = payload.get("purpose", "")
        tone = payload.get("tone", "professional")
        draft = compose_email_body(recipient, purpose, tone)
        response = AssistantResponse(kind="email_draft", details={
            "recipient": recipient,
            "subject": draft["subject"],
            "body": draft["body"],
            "tone": tone,
        })

    elif kind == "web_search_tool":
        query = payload.get("query", "")
        topic = payload.get("topic", "general")
        result = run_web_search(user.user_id, query, topic)
        response = AssistantResponse(kind="web_search", details=result)

    elif kind == "generate_image_tool":
        prompt = payload.get("prompt", "")
        result = run_image_gen(user.user_id, prompt)
        response = AssistantResponse(kind="generated_image", details=result)

    # For SQL Agent
    elif kind == "query_transactions":
        condition = payload.get("condition", "")
        try:
            rows = bank.query_transactions(user, condition)
            answer = summarize_results(body.message, rows)
            response = AssistantResponse(kind="text", text=answer)
        except ValueError:
            response = AssistantResponse(kind="text", text="I can't run that kind of question.")

    elif kind == "add_calendar_event_tool":
        refresh_token = bank.storage.get_google_refresh_token(user.user_id)
        if not refresh_token:
            response = AssistantResponse(kind="text",
                text="Connect your Google account first -- click 'Connect Google' on the Assistant page.")
        else:
            result = add_calendar_event(
                refresh_token, payload.get("date", ""), payload.get("time", ""),
                payload.get("duration_minutes", 30), payload.get("title", "Event"),
            )
            response = AssistantResponse(kind="calendar_event_added", details=result)

    elif kind == "delete_calendar_event_tool":
        refresh_token = bank.storage.get_google_refresh_token(user.user_id)
        if not refresh_token:
            response = AssistantResponse(kind="text", text="Connect your Google account first.")
        else:
            event, err = _resolve_one_event(refresh_token, payload.get("date", ""), payload.get("title_keyword", ""))
            if err:
                response = AssistantResponse(kind="text", text=err)
            else:
                result = delete_calendar_event(refresh_token, event["event_id"])
                response = AssistantResponse(kind="calendar_event_deleted", details=result)

    elif kind == "update_calendar_event_tool":
        refresh_token = bank.storage.get_google_refresh_token(user.user_id)
        if not refresh_token:
            response = AssistantResponse(kind="text", text="Connect your Google account first.")
        else:
            event, err = _resolve_one_event(refresh_token, payload.get("date", ""), payload.get("title_keyword", ""))
            if err:
                response = AssistantResponse(kind="text", text=err)
            else:
                result = update_calendar_event(
                    refresh_token, event["event_id"],
                    date=payload.get("new_date") or None,
                    time=payload.get("new_time") or None,
                    duration_minutes=payload.get("new_duration_minutes") or None,
                    title=payload.get("new_title") or None,
                )
                response = AssistantResponse(kind="calendar_event_updated", details=result)

    elif kind == "read_gmail_tool":
        refresh_token = bank.storage.get_google_refresh_token(user.user_id)
        if not refresh_token:
            response = AssistantResponse(kind="text", text="Connect your Google account first to read your inbox.")
        else:
            logger.info(f"GMAIL TOOL PAYLOAD | {payload}")
            query = build_gmail_query(
                from_person=payload.get("from_person", ""),
                subject_keyword=payload.get("subject_keyword", ""),
                sent_by_user=payload.get("sent_by_user", False),
                days_back=payload.get("days_back", 0),
            )
            max_results = payload.get("max_results", 5)
            result = search_inbox(refresh_token, query, max_results)
            if result["error"]:
                response = AssistantResponse(kind="text", text=result["error"])
            else:
                # Pass the user's ORIGINAL question, not the constructed query --
                # `body.message` is the actual sentence they typed.
                answer = answer_gmail_query(body.message, result["messages"])
                response = AssistantResponse(kind="gmail_answer", details={
                    "answer": answer,
                    "sources": [{"from": m["from"], "subject": m["subject"], "date": m["date"]}
                                for m in result["messages"]],
                })

    elif kind == "remember_fact_tool":
        bank.storage.set_memory_fact(user.user_id, payload.get("key", ""), payload.get("value", ""))
        response = AssistantResponse(kind="text", text="Got it, I'll remember that.")

    else:
        response = AssistantResponse(kind="text", text=payload)

    bank.storage.add_message(user.user_id, "human", body.message)
    bank.storage.add_message(
        user.user_id, "ai",
        _summarize_for_memory(kind, payload, response),
        tool_name=kind,
    )
    return response


@router.post("/assistant/confirm", response_model=MessageResponse)
def assistant_confirm(body: ConfirmRequest, user=Depends(current_user)):
    try:
        bank.transfer(user, body.recipient_account, body.amount)
        return MessageResponse(message="Transfer complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assistant/history")
def assistant_history(user=Depends(current_user)):
    return {"messages": bank.storage.recent_messages(user.user_id, limit=50)}


@router.post("/assistant/confirm_deposit", response_model=MessageResponse)
def assistant_confirm_deposit(body: DepositConfirmRequest, user=Depends(current_user)):
    try:
        bank.deposit(user, body.amount)
        return MessageResponse(message="Deposit complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assistant/confirm_withdraw", response_model=MessageResponse)
def assistant_confirm_withdraw(body: WithdrawConfirmRequest, user=Depends(current_user)):
    try:
        bank.withdraw(user, body.amount)
        return MessageResponse(message="Withdrawal complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))