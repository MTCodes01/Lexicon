"""
Enhanced authentication routes with MFA support.
Handles login, registration, token refresh, MFA setup/verification, and API keys.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from api.database import get_db
from api.core import models, schemas, crud
from api.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    MFAManager,
    field_encryption,
    generate_api_key
)
from api.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_client_ip,
    get_user_agent
)
from api.config import settings


router = APIRouter()
mfa_manager = MFAManager()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: schemas.UserCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Register a new user.
    
    - **email**: User email (must be unique)
    - **password**: User password (min 8 characters)
    - **username**: Optional username
    - **full_name**: Optional full name
    """
    # Check if email already exists
    existing_user = crud.user_crud.get_by_email(db, email=user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if user_create.username:
        existing_username = crud.user_crud.get_by_username(db, username=user_create.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    user = crud.user_crud.create(db, user_create)
    
    # Assign default "user" role
    user_role = crud.role_crud.get_by_name(db, "user")
    if user_role:
        crud.user_crud.add_role(db, user, user_role)
    
    # Log registration
    crud.audit_log_crud.create(
        db,
        user_id=user.id,
        action=models.AuditAction.CREATE,
        resource_type="user",
        resource_id=str(user.id),
        description="User registered",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return user


@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    login_request: schemas.LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Login with email and password.
    
    - **email**: User email
    - **password**: User password
    - **mfa_code**: Optional MFA code (required if MFA is enabled)
    """
    # Get user
    user = crud.user_crud.get_by_email(db, email=login_request.email)
    
    # Verify password
    if not user or not verify_password(login_request.password, user.hashed_password):
        # Log failed login
        crud.audit_log_crud.create(
            db,
            user_id=user.id if user else None,
            action=models.AuditAction.FAILED_LOGIN,
            description="Failed login attempt",
            ip_address=get_client_ip(request) if request else None,
            user_agent=get_user_agent(request) if request else None,
            success=False,
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Check MFA
    if user.mfa_enabled:
        if not login_request.mfa_code:
            return schemas.LoginResponse(
                user=schemas.UserResponse.model_validate(user),
                token=schemas.Token(
                    access_token="",
                    refresh_token="",
                    token_type="bearer",
                    expires_in=0
                ),
                requires_mfa=True
            )
        
        # Verify MFA code
        decrypted_secret = field_encryption.decrypt(user.mfa_secret)
        if not mfa_manager.verify_totp(decrypted_secret, login_request.mfa_code):
            # Check backup codes
            # TODO: Implement backup code verification
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=refresh_token_expires
    )
    
    # Create session
    session_expires = datetime.utcnow() + refresh_token_expires
    crud.session_crud.create(
        db,
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=session_expires,
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    # Update last login
    crud.user_crud.update_last_login(db, user)
    
    # Log successful login
    crud.audit_log_crud.create(
        db,
        user_id=user.id,
        action=models.AuditAction.LOGIN,
        description="User logged in",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return schemas.LoginResponse(
        user=schemas.UserResponse.model_validate(user),
        token=schemas.Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        requires_mfa=False
    )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    token_refresh: schemas.TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode refresh token
        payload = decode_token(token_refresh.refresh_token)
        
        # Verify it's a refresh token
        if not verify_token_type(payload, "refresh"):
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Get user
        user = crud.user_crud.get_by_email(db, email=email)
        if user is None:
            raise credentials_exception
        
        # Verify session exists and is active
        session = crud.session_crud.get_by_refresh_token(db, token_refresh.refresh_token)
        if not session or not session.is_active or session.is_expired():
            raise credentials_exception
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        # Update session with new access token
        session.access_token = new_access_token
        session.last_activity_at = datetime.utcnow()
        db.commit()
        
        return schemas.Token(
            access_token=new_access_token,
            refresh_token=token_refresh.refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise credentials_exception


@router.post("/logout")
async def logout(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Logout current user and revoke all sessions."""
    # Revoke all user sessions
    crud.session_crud.revoke_all_user_sessions(db, current_user.id)
    
    # Log logout
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.LOGOUT,
        description="User logged out",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=schemas.UserWithRoles)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current user information with roles."""
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    updated_user = crud.user_crud.update(db, current_user, user_update)
    
    # Log update
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.UPDATE,
        resource_type="user",
        resource_id=str(current_user.id),
        description="User profile updated",
    )
    
    return updated_user


@router.put("/me/password")
async def update_password(
    password_update: schemas.UserPasswordUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Update current user password."""
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    crud.user_crud.update_password(db, current_user, password_update.new_password)
    
    # Revoke all sessions (force re-login)
    crud.session_crud.revoke_all_user_sessions(db, current_user.id)
    
    # Log password change
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.PASSWORD_CHANGED,
        description="Password changed",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return {"message": "Password updated successfully. Please login again."}


# MFA Routes
@router.post("/mfa/setup", response_model=schemas.MFASetupResponse)
async def setup_mfa(
    mfa_setup: schemas.MFASetupRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup MFA for current user."""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate secret
    secret = mfa_manager.generate_secret()
    
    # Generate QR code
    uri = mfa_manager.get_totp_uri(secret, current_user.email)
    qr_code = mfa_manager.generate_qr_code(uri)
    
    # Generate backup codes
    backup_codes = mfa_manager.generate_backup_codes(settings.MFA_BACKUP_CODES_COUNT)
    
    # Encrypt and save secret (but don't enable yet)
    encrypted_secret = field_encryption.encrypt(secret)
    current_user.mfa_secret = encrypted_secret
    db.commit()
    
    # TODO: Store encrypted backup codes
    
    return schemas.MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify")
async def verify_mfa(
    mfa_verify: schemas.MFAVerifyRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Verify and enable MFA for current user."""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated"
        )
    
    # Decrypt secret
    decrypted_secret = field_encryption.decrypt(current_user.mfa_secret)
    
    # Verify code
    if not mfa_manager.verify_totp(decrypted_secret, mfa_verify.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Enable MFA
    current_user.mfa_enabled = True
    db.commit()
    
    # Log MFA enabled
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.MFA_ENABLED,
        description="MFA enabled",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return {"message": "MFA enabled successfully"}


@router.post("/mfa/disable")
async def disable_mfa(
    mfa_disable: schemas.MFADisableRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Disable MFA for current user."""
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Verify password
    if not verify_password(mfa_disable.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Verify MFA code if provided
    if mfa_disable.code:
        decrypted_secret = field_encryption.decrypt(current_user.mfa_secret)
        if not mfa_manager.verify_totp(decrypted_secret, mfa_disable.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid MFA code"
            )
    
    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    db.commit()
    
    # Log MFA disabled
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.MFA_DISABLED,
        description="MFA disabled",
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )
    
    return {"message": "MFA disabled successfully"}


# API Key Routes
@router.post("/api-keys", response_model=schemas.APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_create: schemas.APIKeyCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for current user."""
    # Generate API key
    key, prefix, hashed_key = generate_api_key()
    
    # Create API key in database
    db_api_key = crud.api_key_crud.create(
        db,
        user_id=current_user.id,
        name=api_key_create.name,
        key=key,
        prefix=prefix,
        hashed_key=hashed_key,
        scopes=api_key_create.scopes,
        expires_in_days=api_key_create.expires_in_days
    )
    
    # Return response with full key (only time it's shown)
    response = schemas.APIKeyCreateResponse.model_validate(db_api_key)
    response.key = key
    
    return response


@router.get("/api-keys", response_model=list[schemas.APIKeyResponse])
async def list_api_keys(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all API keys for current user."""
    api_keys = crud.api_key_crud.get_user_keys(db, current_user.id)
    return api_keys


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    # Get API key
    api_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Verify ownership
    if api_key.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this API key"
        )
    
    # Delete API key
    crud.api_key_crud.delete(db, api_key)
    
    return {"message": "API key deleted successfully"}
