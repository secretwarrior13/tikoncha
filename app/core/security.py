from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.database import get_async_db
from app.models.users import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
<<<<<<< HEAD
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",  # <— the endpoint that issues tokens
    scheme_name="Phone/Password",  # title shown in Swagger’s modal
)
=======
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.API_V1_STR}/auth/login")
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    return encoded_jwt, int(expire.timestamp())


async def get_current_user(
    token: str = Depends(oauth2_scheme),  # ← plain token string
    db: AsyncSession = Depends(get_async_db),
) -> User:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise creds_exc
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise creds_exc

<<<<<<< HEAD
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise creds_exc
=======
        try:
            payload = jwt.decode(
                token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
            )
            print(f"Decoded payload: {payload}")

            user_id_str = payload.get("sub")
            user_type_id = payload.get("type")

            if user_id_str is None or user_type_id is None:
                print("Missing user_id or user_type_id in payload")
                raise credentials_exception

            try:
                user_id = int(user_id_str)
                user_type_id = int(user_type_id)
            except (ValueError, TypeError):
                print("Invalid user_id or user_type_id format")
                raise credentials_exception

        except jwt.PyJWTError as e:
            print(f"JWT decode error: {str(e)}")
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"Token content (not verified): {decoded}")
            except Exception as inner_e:
                print(f"Cannot decode token content: {str(inner_e)}")
            raise credentials_exception

    except Exception as e:
        print(f"General exception: {str(e)}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.user_type_id != user_type_id:
        print(f"User not found or user_type_id mismatch: {user_type_id}")
        raise credentials_exception
>>>>>>> 1e6f4b61bd2dc388852b3f1b09697b0a276db0c0

    return user
