import os
from typing import Union, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import EmailStr
from jose import JWTError, jwt

from oauth_app.app import crud
from oauth_app.app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def fake_decode_token(db: Session, token: str) -> Union[models.User, None]:
    """Decoding the token will give us a user."""
    return crud.get_user_by_email(db, token)


def fake_hash_password(password: str) -> str:
    return "fakehashed" + password


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: EmailStr, password: str):
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    secret_key = os.environ["SECRET_KEY"]
    algorithm = os.environ["ALGORITHM"]
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt
