"""Dependencies for API endpoints."""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.db import database, crud
from app.core.security import decode_access_token
from app.db.models import User

# For dev: allow X-ADMIN-KEY header to bypass auth
ADMIN_KEY = "dev-admin-key-change-in-production"


def get_current_user(
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None),
) -> User:
    """Get current authenticated user from JWT token."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    return current_user


def get_optional_current_user(
    db: Session = Depends(database.get_db),
    authorization: Optional[str] = Header(None),
) -> Optional[User]:
    """Get current authenticated user from JWT token if present, otherwise return None."""
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    email: str = payload.get("sub")
    if email is None:
        return None
    
    user = crud.get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        return None
    
    return user


def get_admin_user(
    current_user: User = Depends(get_current_user),
    x_admin_key: Optional[str] = Header(None, alias="X-ADMIN-KEY"),
) -> User:
    """Get current user if admin, or allow X-ADMIN-KEY header in dev."""
    # In dev, allow X-ADMIN-KEY header
    if x_admin_key == ADMIN_KEY:
        # Return a mock admin user for dev
        # In production, remove this and require proper admin user
        return current_user
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return current_user

