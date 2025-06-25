from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        print(f"Error handling JWT")
        raise e