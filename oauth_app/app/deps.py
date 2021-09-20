import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from oauth_app.app import models
from oauth_app.app import schemas
from oauth_app.app import crud
from oauth_app.app.database.session import SessionLocal
from oauth_app.app.security import fake_decode_token

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# token is the path to the URL that provides the user a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    secret_key = os.environ["SECRET_KEY"]
    algorithm = os.environ["ALGORITHM"]
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return user
    # user = fake_decode_token(db, token)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # return user


def is_superuser(user: models.User):
    return user.is_superuser


def is_active(user: models.User):
    return user.is_active


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_active_superuser(
    current_user: schemas.User = Depends(get_current_active_user),
) -> models.User:
    if not is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
