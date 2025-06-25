from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from db.db_manager import get_db_session
from db.models import User
from db.pydantic_schemas import UserCreate, UserLogin, LoginResponse, UserData
from utils import hash_password, verify_password, create_jwt, decode_jwt
from routes import users, auth

# Load the environment variables from the .env file
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

# Include all the routers. REMEMBER TO ADD HERE ANY NEW ROUTERS.
app.include_router(users.router)
app.include_router(auth.router)

# Middleware to handle CORS. TODO: Make sure to update the regex to match your frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https:\/\/scoring-app-3(-git-[\w-]+)?\.vercel\.app|http:\/\/localhost(:\d+)?",
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)

# Root endpoint to check if the API is live
@app.get("/")
def read_root():
    return {"message": "Scoring App 3.0 API is live!"}
