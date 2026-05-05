from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings, get_security_config


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _jwt_config() -> dict:
    return get_security_config().get("jwt", {})


def create_access_token(subject: str, role: str) -> str:
    cfg = _jwt_config()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=cfg.get("access_token_expire_minutes", 15)
    )
    payload = {"sub": subject, "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, get_settings().SECRET_KEY, algorithm=cfg.get("algorithm", "HS256"))


def create_refresh_token(subject: str) -> str:
    cfg = _jwt_config()
    expire = datetime.now(timezone.utc) + timedelta(
        days=cfg.get("refresh_token_expire_days", 7)
    )
    payload = {"sub": subject, "type": "refresh", "exp": expire}
    return jwt.encode(payload, get_settings().REFRESH_TOKEN_SECRET, algorithm=cfg.get("algorithm", "HS256"))


def decode_access_token(token: str) -> dict:
    cfg = _jwt_config()
    return jwt.decode(token, get_settings().SECRET_KEY, algorithms=[cfg.get("algorithm", "HS256")])


def decode_refresh_token(token: str) -> dict:
    cfg = _jwt_config()
    return jwt.decode(token, get_settings().REFRESH_TOKEN_SECRET, algorithms=[cfg.get("algorithm", "HS256")])
