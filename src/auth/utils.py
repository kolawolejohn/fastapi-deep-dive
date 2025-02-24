from datetime import datetime, timedelta, timezone
import logging
from typing import Optional
from jwt.exceptions import DecodeError
import uuid
import jwt
from passlib.context import CryptContext
from src.config import Config
from itsdangerous import URLSafeTimedSerializer

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_password_hash(password: str) -> str:
    hashed_password = password_context.hash(password)
    return hashed_password


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)


def create_access_token(
    data: dict,
    expiry: timedelta = None,
    refresh: bool = False,
):

    payload = {
        "user": data,
        "exp": datetime.now(timezone.utc).replace(tzinfo=None)
        + (expiry if expiry else timedelta(seconds=Config.ACCESS_TOKEN_EXPIRY)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM,
    )
    return token


def decode_token(token: str) -> Optional[dict]:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET_KEY, algorithms=Config.JWT_ALGORITHM
        )

        return token_data

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET_KEY, salt="email-configuration"
)


def create_url_safe_token(data: dict):
    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):
    try:
        token_data = serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
