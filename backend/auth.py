"""
auth.py — Authentication & Security Utilities for BGAI
=======================================================
Provides password hashing, JWT creation/validation, and the
FastAPI dependency for extracting the current authenticated user.

Author: Ujjwal Tiwari
Version: 3.0.0
"""

import os
import re
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import database, models, schemas

# Load environment variables from .env (if present)
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration  — SECRET_KEY is read from the environment; a development
# fallback is provided but a warning is printed in production contexts.
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    "BGAI_SECRET_KEY",
    "CHANGE_THIS_IN_PRODUCTION_c6d4e8f1a2b3c4d5e6f7a8b9c0d1e2f3"
)
ALGORITHM                 = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480   # 8 hours

if SECRET_KEY.startswith("CHANGE_THIS"):
    import warnings
    warnings.warn(
        "BGAI_SECRET_KEY is using the insecure default. "
        "Set BGAI_SECRET_KEY in your .env file before deploying.",
        stacklevel=1,
    )

pwd_context   = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ---------------------------------------------------------------------------
# Password Utilities
# ---------------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Return a salted PBKDF2 / bcrypt hash of *password*."""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength against minimum security requirements.

    Rules
    -----
    * At least 8 characters
    * At least one uppercase letter
    * At least one digit
    * At least one special character

    Returns
    -------
    (is_valid : bool, message : str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "Password must contain at least one special character (!@#$%…)."
    return True, "Password is strong."


# ---------------------------------------------------------------------------
# JWT Utilities
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encode a signed JWT with an expiry timestamp.

    Parameters
    ----------
    data : dict
        Payload to encode (typically ``{"sub": user_email}``).
    expires_delta : timedelta, optional
        Override the default expiry window.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------------------------------------------------------------------
# FastAPI Dependency — Current User
# ---------------------------------------------------------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
) -> models.User:
    """
    FastAPI dependency that decodes the Bearer token, validates it,
    and returns the corresponding User ORM object.

    Raises HTTP 401 if the token is invalid or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
