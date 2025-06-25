from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.pydantic_schemas import LoginResponse, UserLogin, UserCreate
from db.models import User
from db.db_manager import get_db_session
from utils import create_jwt, verify_password, hash_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register")
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


@router.post("/login", response_model=LoginResponse)
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
        user_id=found_user.id,
        is_admin=found_user.is_admin,
        jwt_token=access_token
    )