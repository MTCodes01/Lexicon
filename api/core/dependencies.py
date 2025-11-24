"""
FastAPI dependencies for authentication and authorization.
Provides dependency injection for current user, permissions, etc.
"""
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from api.database import get_db
from api.core import models, crud, schemas
from api.core.security import decode_token, verify_token_type, verify_api_key


# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db),
    request: Request = None
) -> models.User:
    """
    Get the current authenticated user from JWT token or API key.
    
    Args:
        token: JWT access token
        api_key: API key
        db: Database session
        request: FastAPI request object
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = None
    
    # Try JWT token first
    if token:
        try:
            payload = decode_token(token)
            
            # Verify it's an access token
            if not verify_token_type(payload, "access"):
                raise credentials_exception
            
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            
            user = crud.user_crud.get_by_email(db, email=email)
            if user is None:
                raise credentials_exception
            
            # Update session activity
            session = crud.session_crud.get_by_access_token(db, token)
            if session:
                crud.session_crud.update_activity(db, session)
                
        except JWTError:
            raise credentials_exception
    
    # Try API key if no token
    elif api_key:
        # Extract prefix from key
        if not api_key.startswith("lex_"):
            raise credentials_exception
        
        prefix = api_key[:12]
        db_api_key = crud.api_key_crud.get_by_prefix(db, prefix)
        
        if not db_api_key:
            raise credentials_exception
        
        # Verify key
        if not verify_api_key(api_key, db_api_key.hashed_key):
            raise credentials_exception
        
        # Check if key is active and not expired
        if not db_api_key.is_active or db_api_key.is_expired():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is inactive or expired"
            )
        
        # Get user
        user = crud.user_crud.get_by_id(db, db_api_key.user_id)
        if not user:
            raise credentials_exception
        
        # Update last used
        crud.api_key_crud.update_last_used(db, db_api_key)
    
    else:
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get current superuser.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class RoleChecker:
    """Dependency class to check if user has required role."""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def __call__(self, current_user: models.User = Depends(get_current_user)) -> models.User:
        """
        Check if user has any of the required roles.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have required role
        """
        user_roles = [role.name for role in current_user.roles]
        
        if not any(role in user_roles for role in self.required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(self.required_roles)}"
            )
        
        return current_user


class PermissionChecker:
    """Dependency class to check if user has required permission."""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    def __call__(self, current_user: models.User = Depends(get_current_user)) -> models.User:
        """
        Check if user has all required permissions.
        
        Args:
            current_user: Current user
            
        Returns:
            Current user if authorized
            
        Raises:
            HTTPException: If user doesn't have required permissions
        """
        for permission in self.required_permissions:
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {permission}"
                )
        
        return current_user


def require_roles(*roles: str):
    """
    Decorator to require specific roles.
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: User = Depends(require_roles("admin", "owner"))):
            ...
    """
    return RoleChecker(list(roles))


def require_permissions(*permissions: str):
    """
    Decorator to require specific permissions.
    
    Usage:
        @app.get("/tasks")
        async def get_tasks(user: User = Depends(require_permissions("tasks.view"))):
            ...
    """
    return PermissionChecker(list(permissions))


# Utility to get client IP
def get_client_ip(request: Request) -> Optional[str]:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request
        
    Returns:
        Client IP address
    """
    # Check for forwarded header (if behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to client host
    if request.client:
        return request.client.host
    
    return None


def get_user_agent(request: Request) -> Optional[str]:
    """
    Get user agent from request.
    
    Args:
        request: FastAPI request
        
    Returns:
        User agent string
    """
    return request.headers.get("User-Agent")
