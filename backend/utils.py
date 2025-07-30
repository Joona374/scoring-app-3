from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from db.models import RegCode

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """
    Hashes a given password using a secure hashing algorithm.
    Args:
        password (str): The plain text password to be hashed.
    Returns:
        str: The hashed password as a string.
    """

    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify whether a plain text password matches its hashed counterpart.
    Args:
        plain_password (str): The plain text password to be verified.
        hashed_password (str): The hashed password to compare against.
    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """

    return pwd_context.verify(plain_password, hashed_password)

def create_jwt(data: dict, expires_delta: int = None):
    """
    Generates a JSON Web Token (JWT) with the provided data and expiration time.
    Args:
        data (dict): The payload data to include in the JWT.
        expires_delta (int, optional): The number of minutes until the token expires. 
            If not provided, the expiration time is determined by the environment variable `JWT_EXPIRATION_MINUTES`.
    Returns:
        str: The encoded JWT as a string.
    Environment Variables:
        JWT_SECRET_KEY (str): The secret key used to sign the JWT.
        JWT_ALGORITHM (str): The algorithm used for encoding the JWT.
        JWT_EXPIRATION_MINUTES (int): Default expiration time in minutes if `expires_delta` is not provided.
    Raises:
        ValueError: If any required environment variable is missing or invalid.
    """

    data_to_encode = data.copy()

    if expires_delta:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)

    data_to_encode.update({"exp": expires})

    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt(token: str) -> dict:
    """
    Decodes a JSON Web Token (JWT) and returns its payload.
    Args:
        token (str): The JWT string to decode.
    Returns:
        dict: The decoded payload from the JWT.
    Raises:
        jwt.JWTError: If the token is invalid or cannot be decoded.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError as e:
        print(f"Error decoding JWT")
        raise e
    

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Retrieves the current user's ID from a JWT token.
    Args:
        token (str): The JWT token provided by the OAuth2 scheme.
    Returns:
        int: The user ID extracted from the token.
    Raises:
        HTTPException: If the token is invalid or the user ID cannot be retrieved.
    """

    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        if user_id is None:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return user_id
    except jwt.JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def generate_random_code() -> str:
    """
    Generates a random 6-character code consisting of uppercase letters and digits.
    Returns:
        str: A randomly generated 6-character string.
    """

    random_code = ""
    for _ in range(6):
        random_code += random.choice(string.ascii_uppercase + string.digits + string.digits)
    return random_code

def add_creator_code(admin: bool = False, identifier: str =  None) -> RegCode:
    """
    Generates a random 6-character creator code, adds it to the database, and returns the code.
    Args:
        admin (bool, optional): Indicates if the code is for an admin. Defaults to False.
        identifier (str, optional): An optional identifier to associate with the code. Defaults to None.
    Returns:
        str: The generated creator code.
    Side Effects:
        - Adds a new RegCode entry to the database.
        - Prints the seeded creator code to the console.
    """

    engine = create_engine(DATABASE_URL)

    Session = sessionmaker(bind=engine)
    session = Session()
    
    random_code = generate_random_code()

    new_code = RegCode(
        code=random_code,
        creation_code=True,
        join_code=False,
        team_related_id=None,
        identifier=identifier,
        admin_code=admin
    )
    
    session.add(new_code)
    session.commit()
    session.refresh(new_code)
    session.close()

    print(f"Seeded creator code: {random_code}")
    return new_code