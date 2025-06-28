from pydantic import BaseModel, EmailStr, field_validator
from db.models import Positions

class UserCreate(BaseModel):
    model_config = {"extra": "forbid"}

    username: str
    email: EmailStr
    password: str
    code: str

    @field_validator("username")
    @classmethod
    def no_at_sign_in_username(cls, v):
        if "@" in v:
            raise ValueError("Username cannot contain '@' symbol")
        return v
    
    @field_validator("password")
    @classmethod
    def minimum_password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password has to be atleast 8 characters")
        return v
    
    @field_validator("code")
    @classmethod
    def code_6_char_len(cls, v):
        if len(v) != 6:
            raise ValueError("Registeration Code must be 6 characters long")
        return v


class UserLogin(BaseModel):
    model_config = {"extra": "forbid"}

    user: str
    password: str

class LoginResponse(BaseModel):
    model_config = {"extra": "forbid"}

    username: str
    user_id: int
    is_admin: bool
    jwt_token: str

class UserData(BaseModel):
    model_config = {"extra": "forbid"}

    id: int
    username: str
    email: str

class TeamCreate(BaseModel):
    model_config = {"extra": "forbid"}

    name: str

class PlayerCreate(BaseModel):
    model_config = {"extra": "forbid"}

    first_name: str
    last_name: str
    position: Positions