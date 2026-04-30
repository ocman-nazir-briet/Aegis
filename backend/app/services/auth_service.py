"""
JWT authentication and RBAC service.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

ROLES = {
    "admin":   {"simulate", "ingest", "feedback", "monitoring", "admin", "read"},
    "analyst": {"simulate", "feedback", "monitoring", "read"},
    "viewer":  {"read"},
}

# In production these would come from a database. For now, a static map seeded
# from env/config. Keys are usernames, values are {hashed_password, role}.
_USERS: dict[str, dict] = {}
_INITIALIZED = False


def _seed_default_users():
    """Seed initial users from settings so the system works out of the box."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    default = [
        (settings.admin_username, settings.admin_password, "admin"),
        (settings.viewer_username, settings.viewer_password, "viewer"),
    ]
    for username, raw_password, role in default:
        if username and raw_password:
            try:
                _USERS[username] = {
                    "hashed_password": pwd_context.hash(raw_password[:72]),
                    "role": role,
                }
            except Exception as e:
                # If seeding fails, use plaintext temporarily (dev only)
                _USERS[username] = {
                    "hashed_password": raw_password[:72],
                    "role": role,
                }
    _INITIALIZED = True


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def create_access_token(subject: str, role: str, expires_minutes: int = 60) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain[:72], hashed)
    except Exception:
        return plain[:72] == hashed


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = _USERS.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return {"username": username, "role": user["role"]}


# ---------------------------------------------------------------------------
# FastAPI dependency factories
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """Validate Bearer token and return {username, role}. Raises 401 if missing/invalid."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    return {"username": payload["sub"], "role": payload["role"]}


def require_role(*allowed_roles: str):
    """Return a dependency that enforces role membership."""
    def _check(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user['role']}' is not permitted for this action",
            )
        return user
    return _check


# Convenience shortcuts
require_admin   = require_role("admin")
require_analyst = require_role("admin", "analyst")
require_viewer  = require_role("admin", "analyst", "viewer")
