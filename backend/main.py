from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db.db_manager import get_db_session
from db.models import User
from db.pydantic_schemas import UserCreate
from utils import hash_password
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL is None:
    raise ValueError("FRONTEND_URL environment variable is not set.")


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=FRONTEND_URL,  # List of origins that are allowed to make requests
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Scoring App 3.0 API Main Version is live!"}


#TODO Test if this works before merging to dev!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@app.post("/register")
def register(user_data: UserCreate, db_session: Session = Depends(get_db_session)):
    print("Received user data:", user_data)
    existing_user = db_session.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        is_admin=False,
        password_hash=hashed_password
    )

    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    return {"message": "User created successfully", "id": new_user.id}
#TODO Test if this works before merging to dev!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
