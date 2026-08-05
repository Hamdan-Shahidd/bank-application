import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
BASE_DIR = Path(__file__).parent
PDF_FILE = str(BASE_DIR / "HBL_Conditions.pdf")
CHROMA_DIR = str(BASE_DIR / "chroma_db")

embeddings = HuggingFaceEmbeddings(
    model_name = "all-MiniLM-L6-v2"
)
# Knowledge base in a RAG: 

def build_knowledge_base():
    """
    Run once. Loads the PDF, splits into chunks,
    embeds each chunk, stores in chroma_db/.
    Re-run if you update the PDF.
    """
    print("Loading PDF...")
    loader = PyPDFLoader(PDF_FILE)
    pages = loader.load() # Loads the content on each page in the pdf along with the page number.
    print(f"Loaded {len(pages)} pages") # Prints the number of pages.

    # Chunking: Overlap means the consecutive chunks share the last 50 words to prevent context.
    #           It splits the characters into chunks.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=30,
    )
    # Split the pages: First pdf is covnverted into Document Object (metadata:page number) and then these are 
    # chunked using recursovecharactertextsplitter. 
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks") # Print number of chunks
    print("Building vector store (this takes a minute)...")
    # Create embeddings and store them. It do three things; Take a chunk -> convert each chunk into an embedding -> Store
    Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_DIR,
    )
    print(f"Done. Knowledge base stored in chroma_db/")

# Workflow till now is: 
# PDF -> PyPdf loads pages -> RecursiveCharacterTextSplitter converts each page into chunks -> Embedding models converts each chunk into embedding -> Stored in chroma vector database

def retrieve_policy(question, k=3):
    """
    Returns the k(in our case 3) most relevant chunks from the PDF
    as a plain string, ready to inject into a prompt.
    Returns empty string if nothing found or on error.
    """
    try:
        # Load the vector database into memory
        db = Chroma(
            persist_directory = CHROMA_DIR,
            embedding_function = embeddings, # Question must also be converted into embedding. Otherwise the vectors won't be comparable.
        )

        # Similarity Search: Suppose our database contain 4 chunks. User asks the question, which is converted into embedding
        #                    This embedding is compared against every other vector. This then returns the best matches(returned int he format of document)
        #                    If k=2 above then two nearest matches will be returned.
        results = db.similarity_search(question, k=k)

        if not results:
            return ""
        # The documents are then converted into text using the following. The matches are then inserted into LLM's prompt.
        return "\n\n".join(r.page_content for r in results)
    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""