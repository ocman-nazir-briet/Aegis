"""
Authentication endpoints: token issuance and current-user info.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import TokenRequest, TokenResponse, APIResponse
from app.services.auth_service import authenticate_user, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def login(request: TokenRequest):
    """Exchange username/password for a JWT access token."""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(
        subject=user["username"],
        role=user["role"],
        expires_minutes=settings.jwt_expire_minutes,
    )
    return TokenResponse(
        access_token=token,
        role=user["role"],
        expires_in=settings.jwt_expire_minutes * 60,
    )


@router.get("/me", response_model=APIResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """Return the authenticated user's identity."""
    return APIResponse(success=True, data=user)
