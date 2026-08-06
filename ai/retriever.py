import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

BASE_DIR = Path(__file__).parent.parent  # points to Bank Application root
CHROMA_DIR = str(BASE_DIR / "chroma_db")
PDF_FILE = str(BASE_DIR / "knowledge" / "HBL_Conditions.pdf")


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
        embeddings,
        persist_directory=CHROMA_DIR,
    )
    print("Done. Knowledge base stored in chroma_db/")


def retrieve_policy(question, k=6):
    try:
        db = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
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