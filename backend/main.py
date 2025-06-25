from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from db.db_manager import get_db_session
from db.models import User
from db.pydantic_schemas import UserCreate, UserLogin, LoginResponse, UserData
from utils import hash_password, verify_password, create_jwt, decode_jwt
from routes import users

load_dotenv()

app = FastAPI()

app.include_router(users.router)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https:\/\/scoring-app-3(-git-[\w-]+)?\.vercel\.app|http:\/\/localhost(:\d+)?",
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Scoring App 3.0 API is live!"}

@app.get("/test")
def test_message():
    return {"message": "This is a test message from the Scoring App 3.0 API!"}

@app.post("/login", response_model=LoginResponse)
def login(login_data: UserLogin, db_session: Session = Depends(get_db_session)):
    print("Received login data:", login_data)
    found_user = db_session.query(User).filter((User.username == login_data.user) | (User.email == login_data.user)).first()
    
    if not found_user:
        print(f"User: {login_data.user} was not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either username or password is incorrect") # We dont want to tell which one for safety, right?

    passwords_match = verify_password(login_data.password, found_user.password_hash)
    if not passwords_match:
        print(f"User: {login_data.user} passwords didnt match")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Either username or password is incorrect") # We dont want to tell which one for safety, right?

    user_data = {"sub": str(found_user.id)}
    access_token = create_jwt(user_data, 60)
    return LoginResponse(
        username=found_user.username,
        is_admin=found_user.is_admin,
        jwt_token=access_token
    )



@app.post("/register")
def register(user_data: UserCreate, db_session: Session = Depends(get_db_session)):
    print("Received user data:", user_data)
    existing_user = db_session.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
    
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


