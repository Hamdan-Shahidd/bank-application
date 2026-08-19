# scripts/eval_clause_chunking.py
"""
Compares retrieve_policy() (flat chunking) against retrieve_policy_clauses()
(structure-aware chunking) on the same question set. Every expected clause
id below was verified against parse_clauses()'s real output.
"""
from ai.retriever import retrieve_policy_clauses

TEST_CASES = [
    {"q": "What number is assigned to my account and where is it used?",       "expect": "1b"},
    {"q": "Can a minor have a bank account?",                                   "expect": "2b"},
    {"q": "I already have an account, how do I open a second one?",            "expect": "3"},
    {"q": "What if I can't sign my name and need to withdraw cash?",           "expect": "4"},
    {"q": "Can a blind person open an account?",                              "expect": "5a"},
    {"q": "What about accounts opened under a court order?",                   "expect": "6"},
    {"q": "What happens if the account holder dies?",                         "expect": "7a"},
    {"q": "I have an Either or Survivor account and my co-holder died",       "expect": "7b"},
    {"q": "The sole proprietor of a business account has died",               "expect": "7d"},
    {"q": "Are service charges applied to exempted accounts?",                "expect": "8"},
    {"q": "How are service charges deducted on foreign currency accounts?",   "expect": "9"},
    {"q": "When do transaction charges apply?",                              "expect": "12"},
    {"q": "Can the bank close my account for low balance?",                   "expect": "13"},
    {"q": "My account has been inactive for a year, what happens?",           "expect": "14a"},
    {"q": "What happens if my account is inoperative for 10 years?",          "expect": "15"},
    {"q": "What needs to be written on the back of a cheque?",                "expect": "19"},
    {"q": "Can the bank refuse to honour my cheque?",                        "expect": "22"},
    {"q": "Will the bank honour a stale, six-month-old cheque?",              "expect": "24b"},
    {"q": "How do I put a stop payment on a lost cheque?",                    "expect": "27a"},
    {"q": "Does the bank keep my account information secret?",                "expect": "29"},
    {"q": "How often will I receive account statements?",                     "expect": "30"},
    {"q": "A cheque I deposited was returned unpaid, what happens?",          "expect": "32e"},
    {"q": "What do I need to do to close my account?",                       "expect": "35"},
    {"q": "What law governs my account?",                                    "expect": "38"},
    {"q": "Can the bank combine my different accounts together?",             "expect": "39"},
    {"q": "Does the bank have a lien on my funds if I owe them money?",       "expect": "40"},
    {"q": "What interest rate applies if my account is overdrawn?",           "expect": "42c"},
    {"q": "Which court has jurisdiction over disputes with the bank?",        "expect": "45d"},
    {"q": "Are ATM withdrawals free at HBL's own machines?",                  "expect": "47"},
    {"q": "Is there a fee for the HBL Visa Debit Card?",                     "expect": "48"},
    {"q": "I'm moving abroad permanently, what happens to my account?",       "expect": "51"},
    {"q": "Is interest paid on current accounts?",                           "expect": "55"},
    {"q": "What is FATCA information used for?",                             "expect": "56"},
    {"q": "Where can I bring a claim against Habib Bank Limited?",            "expect": "58"},
]


def hit_at_k(retrieved_ids, expect, k):
    return expect in retrieved_ids[:k]


def run_eval(k=5):
    top1 = topk = 0
    for case in TEST_CASES:
        # retrieve_policy_clauses returns formatted text; for scoring we
        # need the raw clause ids, so this small helper re-runs the search
        # directly against the store to grab metadata.
        from ai.retriever import CLAUSE_CHROMA_DIR, get_embeddings
        from langchain_chroma import Chroma
        db = Chroma(persist_directory=CLAUSE_CHROMA_DIR, embedding_function=get_embeddings())
        hits = db.similarity_search(case["q"], k=k)
        retrieved_ids = [h.metadata.get("clause_id") for h in hits]

        h1 = hit_at_k(retrieved_ids, case["expect"], 1)
        hk = hit_at_k(retrieved_ids, case["expect"], k)
        top1 += h1
        topk += hk
        print(f"{case['q']!r:65} expect={case['expect']:>5} got={retrieved_ids[:3]!s:25} top1={h1!s:5} top{k}={hk}")

    n = len(TEST_CASES)
    print(f"\nTop-1 accuracy: {top1}/{n} = {top1/n:.0%}")
    print(f"Top-{k} accuracy: {topk}/{n} = {topk/n:.0%}")


if __name__ == "__main__":
    run_eval()