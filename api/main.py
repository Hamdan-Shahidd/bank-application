import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent directory so imports find models, storage, banking
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from banking import Bank
from storage import SqliteStorage

app = FastAPI(title="Banking API", version="1.0.0")

# CORS — allows React (localhost:5173) to call FastAPI (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# One Bank instance shared across all requests
bank = Bank(SqliteStorage())


@app.get("/")
def root():
    return {"message": "running"}


# Import and register routers (added in later phases)
from api.routes import account, assistant
app.include_router(account.router)
app.include_router(assistant.router)