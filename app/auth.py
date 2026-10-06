import hashlib
import secrets
from dataclasses import dataclass


@dataclass
class User:
    username: str
    password_hash: str
    role: str
    is_blocked: bool = False
    failed_attempts: int = 0


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


users = {
    "admin": User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="admin",
    ),
    "user": User(
        username="user",
        password_hash=hash_password("user123"),
        role="user",
    ),
}


active_tokens: dict[str, str] = {}


def authenticate_user(username: str, password: str) -> User | None:
    user = users.get(username)

    if user is None:
        return None

    if user.is_blocked:
        return None

    if user.password_hash != hash_password(password):
        return None

    return user


def create_token(username: str) -> str:
    token = secrets.token_urlsafe(32)
    active_tokens[token] = username
    return token


def get_user_by_token(token: str) -> User | None:
    username = active_tokens.get(token)

    if username is None:
        return None

    return users.get(username)