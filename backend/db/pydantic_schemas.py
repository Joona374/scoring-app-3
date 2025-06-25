from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

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

class UserLogin(BaseModel):
    user: str
    password: str

class LoginResponse(BaseModel):
    username: str
    is_admin: bool
    jwt_token: str

class UserData(BaseModel):
    id: int
    username: str
    email: str