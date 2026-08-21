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
from api.routes import account, assistant , people_debug , market , weather , email , imagegen , signup_OTP  , oauth

app.include_router(account.router)
app.include_router(assistant.router)
# Added for the RAG name one's. 
app.include_router(people_debug.router)
# Added for the Crypto Currency data
app.include_router(market.router)
# Added for the weather
app.include_router(weather.router)
# Added the email one
app.include_router(email.router)
# Added for the image generation
app.include_router(imagegen.router)
# For OTP
app.include_router(signup_OTP.router)
# For google auth
app.include_router(oauth.router)
