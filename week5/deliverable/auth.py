"""
deliverable/auth.py
=====================
JWT creation and verification for the ride-hailing API.

Read resources/jwt-explainer.md before implementing this file.

Rules:
  - Use python-jose for JWT encode/decode (pip install python-jose[cryptography])
  - Use passlib for password hashing (pip install passlib[bcrypt])
  - NEVER store or compare plaintext passwords
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# ── Configuration ───────────────────────────────────────────────────────────────
# In production, load SECRET_KEY from an environment variable — never hardcode it.
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password hashing ────────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage. Use this when creating users."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── Token creation ──────────────────────────────────────────────────────────────

def create_access_token(user_id: str, role: str) -> str:
    """
    Create a signed JWT containing the user's id and role.

    TODO:
      1. Build a payload dict: {"sub": user_id, "role": role, "exp": <expiry>}
      2. Set expiry using datetime.now(timezone.utc) + timedelta(minutes=...)
      3. Encode with jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
      4. Return the encoded token string
    """
    # --- your code here ---
    pass


# ── Token verification ──────────────────────────────────────────────────────────

def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT. Raises JWTError if invalid or expired.

    TODO:
      Use jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      and return the resulting payload dict.
    """
    # --- your code here ---
    pass


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency — extracts and verifies the JWT from the
    Authorization header. Use this on any route that requires
    ANY authenticated user (rider or driver).

    TODO:
      1. Call decode_token(token)
      2. If it raises JWTError, raise HTTPException(401, "Not authenticated")
      3. Return the decoded payload
    """
    # --- your code here ---
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(required_role: str):
    """
    FastAPI dependency factory — use this on routes that require a SPECIFIC
    role (e.g. only drivers can call POST /drivers/location).

    Usage:
        @app.post("/drivers/location")
        def update_location(current_user: dict = Depends(require_role("driver"))):
            ...

    TODO:
      Return an inner function that:
        1. Calls get_current_user() to get the decoded token payload
        2. Checks payload["role"] == required_role
        3. If not, raise HTTPException(403, "Forbidden")
        4. Otherwise return the payload
    """
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        # --- your code here ---
        return current_user

    return checker
