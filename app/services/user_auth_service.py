import base64
import hashlib
import hmac
import secrets
from uuid import uuid4

from app.config.database_session_provider import get_provider
from app.db.user.model import User

_ITERATIONS = 120_000


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(digest).decode()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, digest_b64 = stored.split(":", 1)
        salt = base64.b64decode(salt_b64.encode())
        expected = base64.b64decode(digest_b64.encode())
    except Exception:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return hmac.compare_digest(actual, expected)


def create_user(user_name: str, email: str, password: str, role: str = "viewer") -> dict:
    email_normalized = email.strip().lower()
    with get_provider().write_session() as session:
        existing = session.query(User).filter(User.email == email_normalized).first()
        if existing:
            raise ValueError("Email already registered")
        user = User(
            user_name=user_name.strip(),
            email=email_normalized,
            password=_hash_password(password),
            role=role,
        )
        session.add(user)
        session.flush()
        token = f"{user.id}:{uuid4()}"
        return {"token": token, "role": user.role, "user_name": user.user_name}


def authenticate_user(email: str, password: str) -> dict | None:
    email_normalized = email.strip().lower()

    with get_provider().read_session() as session:
        user = (
            session.query(User)
            .filter(User.email == email_normalized, User.archived.is_(False))
            .first()
        )

        if not user or not _verify_password(password, user.password):
            return None
        token = f"{user.id}:{uuid4()}"
        return {"token": token, "role": user.role, "user_name": user.user_name}
