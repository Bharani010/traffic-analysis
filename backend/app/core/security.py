"""
Security utilities — placeholder for Phase 2+.

Will include JWT token handling, password hashing, and
role-based access control.
"""

from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    secret_key: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token. Full implementation in Phase 2."""
    _ = data, secret_key, expires_delta  # noqa: F841
    # Placeholder — will use python-jose in Phase 2
    return "placeholder-token"
