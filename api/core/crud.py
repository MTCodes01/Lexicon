"""
CRUD operations for core models.
Provides database operations for User, Role, Permission, etc.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID

from api.core import models, schemas
from api.core.security import (
    get_password_hash,
    verify_password,
    field_encryption,
    MFAManager
)


# User CRUD
class UserCRUD:
    """CRUD operations for User model."""
    
    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[models.User]:
        """Get user by ID."""
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.User]:
        """Get user by email."""
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[models.User]:
        """Get user by username."""
        return db.query(models.User).filter(models.User.username == username).first()
    
    @staticmethod
    def get_multi(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[models.User]:
        """Get multiple users with pagination."""
        query = db.query(models.User)
        if is_active is not None:
            query = query.filter(models.User.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, user_create: schemas.UserCreate) -> models.User:
        """Create a new user."""
        hashed_password = get_password_hash(user_create.password)
        
        db_user = models.User(
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update(
        db: Session,
        user: models.User,
        user_update: schemas.UserUpdate
    ) -> models.User:
        """Update user information."""
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_password(
        db: Session,
        user: models.User,
        new_password: str
    ) -> models.User:
        """Update user password."""
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_last_login(db: Session, user: models.User) -> models.User:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete(db: Session, user: models.User) -> None:
        """Delete a user."""
        db.delete(user)
        db.commit()
    
    @staticmethod
    def add_role(db: Session, user: models.User, role: models.Role) -> models.User:
        """Add a role to a user."""
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def remove_role(db: Session, user: models.User, role: models.Role) -> models.User:
        """Remove a role from a user."""
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user


# Role CRUD
class RoleCRUD:
    """CRUD operations for Role model."""
    
    @staticmethod
    def get_by_id(db: Session, role_id: UUID) -> Optional[models.Role]:
        """Get role by ID."""
        return db.query(models.Role).filter(models.Role.id == role_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[models.Role]:
        """Get role by name."""
        return db.query(models.Role).filter(models.Role.name == name).first()
    
    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Role]:
        """Get multiple roles."""
        return db.query(models.Role).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, role_create: schemas.RoleCreate) -> models.Role:
        """Create a new role."""
        db_role = models.Role(
            name=role_create.name,
            display_name=role_create.display_name,
            description=role_create.description,
        )
        
        # Add permissions
        if role_create.permission_ids:
            permissions = db.query(models.Permission).filter(
                models.Permission.id.in_(role_create.permission_ids)
            ).all()
            db_role.permissions = permissions
        
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    @staticmethod
    def update(
        db: Session,
        role: models.Role,
        role_update: schemas.RoleUpdate
    ) -> models.Role:
        """Update role information."""
        update_data = role_update.model_dump(exclude_unset=True)
        
        # Handle permissions separately
        permission_ids = update_data.pop('permission_ids', None)
        
        for field, value in update_data.items():
            setattr(role, field, value)
        
        if permission_ids is not None:
            permissions = db.query(models.Permission).filter(
                models.Permission.id.in_(permission_ids)
            ).all()
            role.permissions = permissions
        
        role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(role)
        return db_role
    
    @staticmethod
    def delete(db: Session, role: models.Role) -> None:
        """Delete a role."""
        db.delete(role)
        db.commit()


# Permission CRUD
class PermissionCRUD:
    """CRUD operations for Permission model."""
    
    @staticmethod
    def get_by_id(db: Session, permission_id: UUID) -> Optional[models.Permission]:
        """Get permission by ID."""
        return db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[models.Permission]:
        """Get permission by name."""
        return db.query(models.Permission).filter(models.Permission.name == name).first()
    
    @staticmethod
    def get_by_resource_action(
        db: Session,
        resource: str,
        action: str
    ) -> Optional[models.Permission]:
        """Get permission by resource and action."""
        return db.query(models.Permission).filter(
            and_(
                models.Permission.resource == resource,
                models.Permission.action == action
            )
        ).first()
    
    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[models.Permission]:
        """Get multiple permissions."""
        return db.query(models.Permission).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, permission_create: schemas.PermissionCreate) -> models.Permission:
        """Create a new permission."""
        db_permission = models.Permission(**permission_create.model_dump())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return db_permission


# Session CRUD
class SessionCRUD:
    """CRUD operations for Session model."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: UUID,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> models.Session:
        """Create a new session."""
        db_session = models.Session(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_by_access_token(db: Session, access_token: str) -> Optional[models.Session]:
        """Get session by access token."""
        return db.query(models.Session).filter(
            models.Session.access_token == access_token
        ).first()
    
    @staticmethod
    def get_by_refresh_token(db: Session, refresh_token: str) -> Optional[models.Session]:
        """Get session by refresh token."""
        return db.query(models.Session).filter(
            models.Session.refresh_token == refresh_token
        ).first()
    
    @staticmethod
    def get_user_sessions(
        db: Session,
        user_id: UUID,
        active_only: bool = True
    ) -> List[models.Session]:
        """Get all sessions for a user."""
        query = db.query(models.Session).filter(models.Session.user_id == user_id)
        
        if active_only:
            query = query.filter(
                and_(
                    models.Session.is_active == True,
                    models.Session.expires_at > datetime.utcnow()
                )
            )
        
        return query.all()
    
    @staticmethod
    def update_activity(db: Session, session: models.Session) -> models.Session:
        """Update session last activity timestamp."""
        session.last_activity_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def revoke(db: Session, session: models.Session) -> models.Session:
        """Revoke a session."""
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: UUID) -> None:
        """Revoke all sessions for a user."""
        db.query(models.Session).filter(
            models.Session.user_id == user_id
        ).update({
            "is_active": False,
            "revoked_at": datetime.utcnow()
        })
        db.commit()


# API Key CRUD
class APIKeyCRUD:
    """CRUD operations for API Key model."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: UUID,
        name: str,
        key: str,
        prefix: str,
        hashed_key: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None
    ) -> models.APIKey:
        """Create a new API key."""
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        db_api_key = models.APIKey(
            user_id=user_id,
            name=name,
            key_prefix=prefix,
            hashed_key=hashed_key,
            scopes=scopes,
            expires_at=expires_at,
        )
        
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        return db_api_key
    
    @staticmethod
    def get_by_prefix(db: Session, prefix: str) -> Optional[models.APIKey]:
        """Get API key by prefix."""
        return db.query(models.APIKey).filter(
            models.APIKey.key_prefix == prefix
        ).first()
    
    @staticmethod
    def get_user_keys(db: Session, user_id: UUID) -> List[models.APIKey]:
        """Get all API keys for a user."""
        return db.query(models.APIKey).filter(
            models.APIKey.user_id == user_id
        ).all()
    
    @staticmethod
    def update_last_used(db: Session, api_key: models.APIKey) -> models.APIKey:
        """Update API key last used timestamp."""
        api_key.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(api_key)
        return api_key
    
    @staticmethod
    def revoke(db: Session, api_key: models.APIKey) -> models.APIKey:
        """Revoke an API key."""
        api_key.is_active = False
        db.commit()
        db.refresh(api_key)
        return api_key
    
    @staticmethod
    def delete(db: Session, api_key: models.APIKey) -> None:
        """Delete an API key."""
        db.delete(api_key)
        db.commit()


# Audit Log CRUD
class AuditLogCRUD:
    """CRUD operations for Audit Log model."""
    
    @staticmethod
    def create(
        db: Session,
        user_id: Optional[UUID],
        action: models.AuditAction,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        changes: Optional[dict] = None,
        metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> models.AuditLog:
        """Create an audit log entry."""
        db_audit_log = models.AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            changes=changes,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message,
        )
        
        db.add(db_audit_log)
        db.commit()
        db.refresh(db_audit_log)
        return db_audit_log
    
    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.AuditLog]:
        """Get audit logs for a user."""
        return db.query(models.AuditLog).filter(
            models.AuditLog.user_id == user_id
        ).order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_resource_logs(
        db: Session,
        resource_type: str,
        resource_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.AuditLog]:
        """Get audit logs for a specific resource."""
        return db.query(models.AuditLog).filter(
            and_(
                models.AuditLog.resource_type == resource_type,
                models.AuditLog.resource_id == resource_id
            )
        ).order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit).all()


# Export CRUD classes
user_crud = UserCRUD()
role_crud = RoleCRUD()
permission_crud = PermissionCRUD()
session_crud = SessionCRUD()
api_key_crud = APIKeyCRUD()
audit_log_crud = AuditLogCRUD()
