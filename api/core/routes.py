"""
Enhanced authentication routes with MFA support.
Handles login, registration, token refresh, MFA setup/verification, and API keys.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
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
    
    import logging
    logger = logging.getLogger("uvicorn.error")
    logger.info(f"LOGIN ATTEMPT: {login_request.email} | MFA Code present: {bool(login_request.mfa_code)}")
    
    # Verify password
    if not user or not verify_password(login_request.password, user.hashed_password):
        logger.info("LOGIN FAILED: Invalid password")
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
    
    logger.info("LOGIN: Password verified")

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


@router.post("/forgot-password")
async def request_password_reset(
    request_data: schemas.PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset. Always returns success to prevent user enumeration."""
    import secrets
    from datetime import datetime, timedelta
    from api.core import email as email_utils
    
    # Find user by email
    user = crud.user_crud.get_by_email(db, request_data.email)
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set token and expiration (1 hour from now)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send reset email
        email_utils.send_password_reset_email(user.email, reset_token)
        
        # Log the action
        crud.audit_log_crud.create(
            db,
            user_id=user.id,
            action=models.AuditAction.PASSWORD_CHANGED,
            description="Password reset requested",
        )
    
    # Always return success to prevent user enumeration
    return {"message": "If your email is registered, you will receive a password reset link shortly."}


@router.get("/reset-password/{token}")
async def validate_reset_token(
    token: str,
    db: Session = Depends(get_db)
):
    """Validate password reset token."""
    from datetime import datetime
    
    # Find user with this token
    user = db.query(models.User).filter(
        models.User.reset_token == token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    return {"message": "Token is valid", "email": user.email}


@router.post("/reset-password")
async def confirm_password_reset(
    reset_data: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Confirm password reset with token and new password."""
    from datetime import datetime
    from api.core import email as email_utils
    
    # Find user with this token
    user = db.query(models.User).filter(
        models.User.reset_token == reset_data.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    crud.user_crud.update_password(db, user, reset_data.new_password)
    
    # Clear reset token
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    # Send confirmation email
    email_utils.send_password_changed_email(user.email)
    
    # Log the action
    crud.audit_log_crud.create(
        db,
        user_id=user.id,
        action=models.AuditAction.PASSWORD_CHANGED,
        description="Password reset completed",
    )
    
    return {"message": "Password has been successfully reset"}


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
    
    # Log the action
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.UPDATE,
        resource_type="user",
        resource_id=str(current_user.id),
        description="User profile updated",
    )
    
    return updated_user


@router.get("/me/stats")
async def get_user_statistics(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user statistics including account age, task count, and session info."""
    from datetime import datetime
    
    # Calculate account age in days
    account_age_days = (datetime.utcnow() - current_user.created_at).days
    
    # Get total tasks count
    from api.modules.tasks import models as task_models
    total_tasks = db.query(task_models.Task).filter(
        task_models.Task.user_id == current_user.id
    ).count()
    
    # Get active sessions count
    active_sessions = crud.session_crud.get_active_user_sessions(db, current_user.id)
    active_sessions_count = len(active_sessions) if active_sessions else 0
    
    return {
        "account_age_days": account_age_days,
        "total_tasks": total_tasks,
        "active_sessions": active_sessions_count,
        "last_login": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/me/sessions")
async def get_user_sessions(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get all active sessions for the current user."""
    sessions = crud.session_crud.get_active_user_sessions(db, current_user.id)
    
    # Get current request's session token to mark current session
    current_token = None
    if request and request.headers.get("Authorization"):
        auth_header = request.headers.get("Authorization")
        if auth_header.startswith("Bearer "):
            current_token = auth_header[7:]
    
    result = []
    for session in sessions:
        is_current = session.access_token == current_token
        result.append({
            "id": str(session.id),
            "device_info": session.user_agent or "Unknown",
            "ip_address": session.ip_address or "Unknown",
            "last_activity": session.last_activity_at.isoformat() if session.last_activity_at else None,
            "created_at": session.created_at.isoformat(),
            "is_current": is_current,
        })
    
    return result


@router.delete("/me/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific user session."""
    from uuid import UUID
    
    # Convert session_id to UUID
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )
    
    # Get the session
    session = db.query(models.Session).filter(
        models.Session.id == session_uuid,
        models.Session.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Revoke the session
    crud.session_crud.revoke(db, session)
    
    # Log the action
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.LOGOUT,
        description=f"Session revoked: {session_id[:8]}...",
    )
    
    return {"message": "Session revoked successfully"}


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar image."""
    from api.core.storage import upload_avatar as upload_avatar_file, delete_avatar
    
    # Delete old avatar if exists
    if current_user.avatar_url:
        delete_avatar(current_user.avatar_url)
    
    # Upload new avatar
    avatar_url = await upload_avatar_file(file, str(current_user.id))
    
    # Update user record
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    
    # Log avatar update
    crud.audit_log_crud.create(
        db,
        user_id=current_user.id,
        action=models.AuditAction.UPDATE,
        resource_type="user",
        resource_id=str(current_user.id),
        description="Avatar uploaded",
    )
    
    return {"avatar_url": avatar_url, "message": "Avatar uploaded successfully"}


@router.delete("/me/avatar")
async def delete_user_avatar(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user avatar."""
    from api.core.storage import delete_avatar
    
    if not current_user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No avatar to delete"
        )
    
    # Delete from storage
    delete_avatar(current_user.avatar_url)
    
    # Remove from user record
    current_user.avatar_url = None
    db.commit()
    
    return {"message": "Avatar deleted successfully"}


@router.post("/me/banner", response_model=schemas.UserResponse)
async def upload_banner(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user profile banner."""
    from api.core.storage import upload_banner as upload_banner_file, delete_banner
    
    # Delete existing banner if any
    if current_user.banner_url:
        delete_banner(current_user.banner_url)
    
    # Upload new banner
    banner_url = await upload_banner_file(file, str(current_user.id))
    
    # Update user
    current_user.banner_url = banner_url
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.delete("/me/banner", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user profile banner."""
    from api.core.storage import delete_banner
    
    if current_user.banner_url:
        delete_banner(current_user.banner_url)
        
        current_user.banner_url = None
        db.add(current_user)
        db.commit()


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
