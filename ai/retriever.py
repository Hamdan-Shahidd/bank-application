import os
import re
# os.environ["HF_HUB_OFFLINE"] = "1"
from pathlib import Path
from dotenv import load_dotenv
from logging_config import logger
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
# THe following one is imported for the second RAG approach
from langchain_core.documents import Document

BASE_DIR = Path(__file__).parent.parent  # points to Bank Application root
CHROMA_DIR = str(BASE_DIR / "chroma_db")
PDF_FILE = str(BASE_DIR / "knowledge" / "HBL_Conditions.pdf")

# For People dataset
PEOPLE_PDF = str(BASE_DIR / "knowledge" / "people_data.pdf")
PEOPLE_CHROMA_DIR = str(BASE_DIR / "chroma_db_people")

# For the second approach of RAG
CLAUSE_CHROMA_DIR = str(BASE_DIR / "chroma_db_clauses")

_embeddings = None


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def build_knowledge_base():
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_FILE)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")

    print("Building vector store...")
    Chroma.from_documents(
        chunks,
        get_embeddings(),
        persist_directory=CHROMA_DIR,
    )
    print("Done. Knowledge base stored in chroma_db/")


# For the people data RAG
def build_people_knowledge_base():
    print("Loading PDF")
    loader = PyPDFLoader(PEOPLE_PDF)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 300,
        chunk_overlap = 0 ,
        separators=["=== RECORD SEP ==="]
    )
    chunks = splitter.split_documents(pages)
    print(f" Split into {len(chunks)} chunks")

    print("Building vector store")
    Chroma.from_documents(
        chunks,
        get_embeddings(),
        persist_directory=PEOPLE_CHROMA_DIR
    )
    print(f"Knowledge base stored in {PEOPLE_CHROMA_DIR}")
    


def retrieve_policy(question, k=6):
    try:
        db = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=get_embeddings(),
        )
        results = db.similarity_search(question, k=k)
        if not results:
            return ""

        seen = set()
        unique = []
        for r in results:
            normalised = " ".join(r.page_content.split())
            if normalised not in seen:
                seen.add(normalised)
                unique.append(r.page_content)

        return "\n\n".join(unique)
    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""


# The following one is build for removing LLM in the RAG
def retrieve_policy_debug(question, k=6):
    """Same retrieval as retrieve_policy, but returns per-chunk records with scores."""
    try:
        db = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=get_embeddings(),
        )
        results = db.similarity_search_with_score(question, k=k)
        if not results:
            return []

        seen, unique = set(), []
        for doc, score in results:
            normalised = " ".join(doc.page_content.split())
            if normalised in seen:
                continue
            seen.add(normalised)
            unique.append({
                "score": round(float(score), 4),
                "page": doc.metadata.get("page"),
                "text": doc.page_content,
            })
        return unique
    except Exception as e:
        logger.warning(f"RAG DEBUG RETRIEVAL FAILED | {e}")
        return []

def retrieve_people_debug(question, k=6):
    try:
        db = Chroma(
            persist_directory=PEOPLE_CHROMA_DIR,
            embedding_function=get_embeddings(),
        )
        results = db.similarity_search_with_score(question, k=k)
        return [
            {"score": round(float(s), 4), "page": d.metadata.get("page"), "text": d.page_content}
            for d, s in results
        ]
    except Exception as e:
        logger.warning(f"PEOPLE RAG DEBUG FAILED | {e}")
        return []

# For the second RAG approach
# Take clause numbers and give them human-readable names.
SECTION_MAP = {
    range(1, 4):   "Account Opening",
    range(4, 7):   "Special Customer Categories",
    range(7, 8):   "Death and Succession",
    range(8, 13):  "Service and Transaction Charges",
    range(13, 14): "Account Closure by Bank",
    range(14, 16): "Inoperative and Abandoned Accounts",
    range(16, 28): "Deposits, Cheques and Instruments",
    range(28, 29): "Outsourcing",
    range(29, 30): "Secrecy and Disclosure",
    range(30, 32): "Statements of Account",
    range(32, 33): "Cheque and Instrument Collection",
    range(33, 35): "Errors and Address Changes",
    range(35, 38): "Account Closure and Branch Transfer",
    range(38, 42): "Governing Law and Liability",
    range(42, 47): "Interest and Tax",
    range(47, 49): "ATM and Card Charges",
    range(49, 51): "Access Channels and General Terms",
    range(51, 52): "Non-Resident Accounts",
    range(52, 57): "Amendments and Account Refusal",
    range(57, 61): "Indemnity, Jurisdiction and Card Terms",
}

# Tskes the clause_num and finds which section does it belongs to. Clause 2 belong to account opening
def _section_for(clause_num: int) -> str:
    for rng, name in SECTION_MAP.items():
        if clause_num in rng:
            return name
    return "General"

# These are used to find the clause and sub-clauses in the pdf.
CLAUSE_RE = re.compile(r"\n\s*(\d{1,2})\.\s+") # Captures 1 or 2 digit numbers. 
SUBCLAUSE_RE = re.compile(r"\(([a-z])\)\s+") # Capture sub-clauses which are in letter (a) etc.

"""
This is the main function. Its purpose is given below;
PDF -> Extract Text -> Find clauses -> Find sub-clauses -> Assign page -> Assign sub-section -> Create metadata
-> return chunks
"""
def parse_clauses():
    """Parse HBL_Conditions.pdf into clause/sub-clause chunks with metadata."""
    # Loads the pdf. Each page is seperate document. Langchain PyPDFLoader is used. 
    loader = PyPDFLoader(PDF_FILE)
    pages = loader.load()

    # Join pages first, tracking offsets, so a clause spanning a page
    # break (clause 32 -> page 2/3) stays whole. Joining all tha pages as one large text.
    full, page_offsets = "", []
    for i, page in enumerate(pages):
        page_offsets.append((len(full), i + 1))
        full += page.page_content + "\n"

    # Removing page number from the text. They are already stored as the metadata, not in the text.
    full = re.sub(r"\s*Page \d+ of \d+\s*", "\n", full)

    # This takes a character position and determines which page does it belong to. 
    def page_for(offset):
        page = 1
        for start, p in page_offsets:
            if start <= offset:
                page = p
        return page

    # Finding the clause markers in the pdf. This measures the number of clauses in the pdf. 
    matches = list(CLAUSE_RE.finditer(full))
    logger.info(f"CLAUSE PARSER | found {len(matches)} clause markers")

    # Looping thruggh the clauses. 
    chunks = []
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full)
        body = re.sub(r"\s+", " ", full[start:end]).strip()
        page = page_for(m.start())
        section = _section_for(num)

        parts = SUBCLAUSE_RE.split(body)
        if len(parts) > 1 and not parts[0].strip():
            # Looping for sub-clauses
            for j in range(1, len(parts) - 1, 2):
                letter = parts[j]
                text = re.sub(r"\s+", " ", parts[j + 1]).strip()
                if not text:
                    continue
                chunks.append({
                    "clause_id": f"{num}{letter}",
                    "parent_clause": str(num),
                    "page": page,
                    "section": section,
                    "text": f"Clause {num}({letter}): {text}",
                })
        else:
            chunks.append({
                "clause_id": str(num),
                "parent_clause": str(num),
                "page": page,
                "section": section,
                "text": f"Clause {num}: {body}",
            })

    logger.info(f"CLAUSE PARSER | produced {len(chunks)} chunks")
    return chunks

# Bridge between clause parser and vector database.
def build_clause_knowledge_base():
    """Clause-aware build. Replaces flat character chunking for this store."""
    # Provide utilities for manipulating files and directories.
    import shutil

    chunks = parse_clauses()
    # Convert clauses into langchain documents.
    docs = [
        Document(
            page_content=c["text"],
            metadata={
                "clause_id": c["clause_id"],
                "parent_clause": c["parent_clause"],
                "page": c["page"],
                "section": c["section"],
                "document": "HBL_Conditions",
            },
        )
        for c in chunks
    ]   

    # Check if the database already exists. If yes delete the old database.
    if Path(CLAUSE_CHROMA_DIR).exists():
        shutil.rmtree(CLAUSE_CHROMA_DIR)
        logger.info("CLAUSE BUILD | cleared existing vector store")

    print(f"Embedding {len(docs)} clause chunks...")
    # Create embeddings and store them in chroma.
    Chroma.from_documents(
        docs,  # These are the clause documents.
        get_embeddings(), 
        persist_directory=CLAUSE_CHROMA_DIR
    )
    print(f"Done. {len(docs)} chunks stored in {CLAUSE_CHROMA_DIR}")

# Retrive Policy
def retrieve_policy_clauses(question, k=5):
    """
    Vector similarity search over the clause-aware store, with parent/section
    context prepended at query time. Intentionally simple — same retrieval
    strategy as retrieve_policy(), just over better-formed chunks.
    """
    try:
        db = Chroma(persist_directory=CLAUSE_CHROMA_DIR,
                    embedding_function=get_embeddings())
        hits = db.similarity_search_with_score(question, k=k)
        if not hits:
            return ""

        blocks = []
        for doc, score in hits:
            md = doc.metadata
            blocks.append(
                f"[Section: {md.get('section')} | Clause {md.get('parent_clause')} "
                f"| page {md.get('page')}]\n{doc.page_content}"
            )
        logger.info(f"CLAUSE RETRIEVAL | clauses={[d.metadata.get('clause_id') for d,_ in hits]}")
        return "\n\n".join(blocks)
    except Exception as e:
        logger.warning(f"CLAUSE RETRIEVAL FAILED | {e}")
        return ""