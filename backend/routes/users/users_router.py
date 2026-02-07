from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from db.pydantic_schemas import UserData
from db.db_manager import get_db_session
from db.models import User
from utils import decode_jwt


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=UserData)
def get_current_user(request: Request, db_session: Session = Depends(get_db_session)):
    auth_header = request.headers.get("authorization")
    if auth_header is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
    token = auth_header.removeprefix("Bearer ").strip()
    
    token_payload = decode_jwt(token)

    user_id = int(token_payload["sub"])
    user = db_session.query(User).filter(User.id==user_id).first()
    if user:
        return UserData(id=user.id, username=user.username, email=user.email)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found in db")