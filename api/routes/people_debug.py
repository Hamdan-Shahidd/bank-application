"""
TEMPORARY debug route for testing the RAG pipeline against the synthetic
people dataset. Not part of the banking assistant. Safe to delete this
file (and its one line in main.py) once RAG testing is done.
"""
from fastapi import APIRouter, Depends
from api.schemas import AssistantRequest, AssistantResponse
from api.auth import current_user
from ai.retriever import retrieve_people_debug

router = APIRouter()


@router.post("/debug/people-query", response_model=AssistantResponse)
def people_query(body: AssistantRequest, user=Depends(current_user)):
    chunks = retrieve_people_debug(body.message)
    if not chunks:
        return AssistantResponse(kind="text", text="[PEOPLE DEBUG] No chunks retrieved.")

    blocks = [
        f"--- chunk {i} | score {c['score']} | page {c['page']} ---\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    ]
    text = "[PEOPLE DEBUG] retrieval only\n\n" + "\n\n".join(blocks)
    return AssistantResponse(kind="text", text=text)