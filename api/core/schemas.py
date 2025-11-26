"""
Pydantic schemas for core models.
Used for request/response validation and serialization.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    """User role types."""
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"
    SERVICE = "service"


class AuditActionEnum(str, Enum):
    """Audit log action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    PASSWORD_CHANGED = "password_changed"


class MFATypeEnum(str, Enum):
    """MFA device types."""
    TOTP = "totp"
    BACKUP_CODES = "backup_codes"


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    is_active: bool = True


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID4
    is_verified: bool
    is_superuser: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None


class UserWithRoles(UserResponse):
    """User response with roles."""
    roles: List['RoleResponse'] = []


# Role schemas
class RoleBase(BaseSchema):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    permission_ids: List[UUID4] = []


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    permission_ids: Optional[List[UUID4]] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: UUID4
    is_system: bool
    created_at: datetime
    updated_at: datetime


class RoleWithPermissions(RoleResponse):
    """Role response with permissions."""
    permissions: List['PermissionResponse'] = []


# Permission schemas
class PermissionBase(BaseSchema):
    """Base permission schema."""
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: UUID4
    is_system: bool
    created_at: datetime


# Authentication schemas
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserResponse
    token: Token
    requires_mfa: bool = False


# MFA schemas
class MFASetupRequest(BaseModel):
    """MFA setup request schema."""
    device_name: str = Field(..., min_length=1, max_length=100)


class MFASetupResponse(BaseModel):
    """MFA setup response schema."""
    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: List[str]


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""
    code: str = Field(..., min_length=6, max_length=6)


class MFADisableRequest(BaseModel):
    """MFA disable request schema."""
    password: str
    code: Optional[str] = None  # TOTP code or backup code


# API Key schemas
class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""
    name: str = Field(..., min_length=1, max_length=100)
    scopes: Optional[List[str]] = None
    expires_in_days: Optional[int] = Field(None, gt=0, le=365)


class APIKeyResponse(BaseSchema):
    """Schema for API key response."""
    id: UUID4
    name: str
    key_prefix: str
    scopes: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class APIKeyCreateResponse(APIKeyResponse):
    """Schema for API key creation response (includes full key)."""
    key: str  # Only returned once during creation


# Session schemas
class SessionResponse(BaseSchema):
    """Schema for session response."""
    id: UUID4
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime
    is_active: bool


# Audit Log schemas
class AuditLogResponse(BaseSchema):
    """Schema for audit log response."""
    id: UUID4
    user_id: Optional[UUID4] = None
    action: AuditActionEnum
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool
    created_at: datetime


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    user_id: Optional[UUID4] = None
    action: Optional[AuditActionEnum] = None
    resource_type: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Setting schemas
class SettingBase(BaseModel):
    """Base setting schema."""
    key: str = Field(..., min_length=1, max_length=100)
    value: dict | str | int | float | bool | None = None
    category: Optional[str] = None
    description: Optional[str] = None


class SettingCreate(SettingBase):
    """Schema for creating a setting."""
    pass


# Pagination schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[BaseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


# Update forward references
UserWithRoles.model_rebuild()
RoleWithPermissions.model_rebuild()
