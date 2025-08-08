# utils.py
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

from typing import Optional, Iterable, List, Union
from enum import Enum

from db.models import (
    RegCode,
    ShotResultTypes,
    ShotTypeTypes,
)

# =========================
# Analysis / enum utilities
# =========================

def to_label(v: Optional[Union[Enum, str]]) -> Optional[str]:
    """Return the display string for enums; pass through strings/None."""
    if v is None:
        return None
    return v.value if isinstance(v, Enum) else v

# Build classification sets dynamically so it works
# even before you add Laukaus ± to ShotResultTypes.
FOR_SET = {ShotResultTypes.GOAL_FOR, ShotResultTypes.CHANCE_FOR}
AGAINST_SET = {ShotResultTypes.GOAL_AGAINST, ShotResultTypes.CHANCE_AGAINST}
GOAL_SET = {ShotResultTypes.GOAL_FOR, ShotResultTypes.GOAL_AGAINST}

# Optional enums (will exist once you extend ShotResultTypes)
SHOT_FOR = getattr(ShotResultTypes, "SHOT_FOR", None)          # "Laukaus +"
SHOT_AGAINST = getattr(ShotResultTypes, "SHOT_AGAINST", None)  # "Laukaus -"

if SHOT_FOR:
    FOR_SET.add(SHOT_FOR)
if SHOT_AGAINST:
    AGAINST_SET.add(SHOT_AGAINST)
# GOAL_SET intentionally remains goals only

def side_of_enum(res: ShotResultTypes) -> str:
    """'FOR' if result is for your team, else 'AGAINST'."""
    return "FOR" if res in FOR_SET else "AGAINST"

def is_goal_enum(res: ShotResultTypes) -> bool:
    return res in GOAL_SET

def allow_result_enum(
    res: ShotResultTypes,
    show_gf: bool,
    show_ga: bool,
    show_cf: bool,
    show_ca: bool,
    show_sf: bool = True,  # shots for (Laukaus +)
    show_sa: bool = True,  # shots against (Laukaus -)
) -> bool:
    """Gate a result by the UI toggles. Defaults keep legacy calls working."""
    if res == ShotResultTypes.GOAL_FOR:
        return show_gf
    if res == ShotResultTypes.GOAL_AGAINST:
        return show_ga
    if res == ShotResultTypes.CHANCE_FOR:
        return show_cf
    if res == ShotResultTypes.CHANCE_AGAINST:
        return show_ca
    # Only check these if the enums exist in your codebase
    if SHOT_FOR and res == SHOT_FOR:
        return show_sf
    if SHOT_AGAINST and res == SHOT_AGAINST:
        return show_sa
    return False

def is_chance_enum(res: ShotResultTypes) -> bool:
    return res in {ShotResultTypes.CHANCE_FOR, ShotResultTypes.CHANCE_AGAINST}

def is_shot_enum(res: ShotResultTypes) -> bool:
    # works even before you add Laukaus ± to the Enum
    return (SHOT_FOR and res == SHOT_FOR) or (SHOT_AGAINST and res == SHOT_AGAINST)

def parse_shot_type_values(values: Optional[Iterable[str]]) -> List[ShotTypeTypes]:
    """Convert list of strings to ShotTypeTypes, skipping unknowns."""
    out: List[ShotTypeTypes] = []
    if not values:
        return out
    for s in values:
        try:
            out.append(ShotTypeTypes.from_string(s))
        except Exception:
            # silently skip unrecognized strings
            pass
    return out


# =========================
# Auth / infra utilities
# =========================

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt(data: dict, expires_delta: int = None):
    data_to_encode = data.copy()
    if expires_delta:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    data_to_encode.update({"exp": expires})
    return jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        print("Error decoding JWT")
        raise e

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user_id
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

def generate_random_code() -> str:
    return "".join(random.choice(string.ascii_uppercase + string.digits + string.digits) for _ in range(6))

def add_creator_code(admin: bool = False, identifier: str = None) -> RegCode:
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
        admin_code=admin,
    )

    session.add(new_code)
    session.commit()
    session.refresh(new_code)
    session.close()

    print(f"Seeded creator code: {random_code}")
    return new_code
