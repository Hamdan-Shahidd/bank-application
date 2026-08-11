from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.banking import Bank
from core.storage import SqliteStorage

app = FastAPI(title="Banking API", version="1.0.0")

# CORS: Cross Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bank = Bank(SqliteStorage())


@app.get("/")
def root():
    return {"message": "running"}

# Registers every endpoint.
from api.routes import account, assistant
app.include_router(account.router)
app.include_router(assistant.router)