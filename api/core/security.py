"""
Enhanced authentication utilities for Lexicon.
Includes password hashing, JWT tokens, MFA (TOTP), and encryption.
"""
from datetime import datetime, timedelta
from typing import Optional, Any
import secrets
import base64
import io

from jose import jwt, JWTError
from passlib.context import CryptContext
import pyotp
import qrcode
from cryptography.fernet import Fernet

from api.config import settings


# Password hashing context
if settings.PASSWORD_HASH_SCHEME == "argon2":
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
else:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Encryption for sensitive fields
class FieldEncryption:
    """Field-level encryption for sensitive data."""
    
    def __init__(self, key: Optional[str] = None):
        """Initialize with encryption key."""
        if key is None:
            key = settings.SECRET_KEY
        # Ensure key is 32 bytes for Fernet
        key_bytes = key.encode()[:32].ljust(32, b'0')
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        if not data:
            return data
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return ""


# Global encryption instance
field_encryption = FieldEncryption()


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT token utilities
def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise e


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """
    Verify that a token is of the expected type.
    
    Args:
        payload: Decoded token payload
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        True if token type matches
    """
    return payload.get("type") == expected_type


# MFA (TOTP) utilities
class MFAManager:
    """Manager for MFA operations."""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, email: str) -> str:
        """
        Get TOTP provisioning URI for QR code.
        
        Args:
            secret: TOTP secret
            email: User email
            
        Returns:
            TOTP URI string
        """
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=settings.MFA_ISSUER_NAME
        )
    
    @staticmethod
    def generate_qr_code(uri: str) -> str:
        """
        Generate QR code image from TOTP URI.
        
        Args:
            uri: TOTP provisioning URI
            
        Returns:
            Base64 encoded QR code image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_totp(secret: str, code: str, window: int = 1) -> bool:
        """
        Verify a TOTP code.
        
        Args:
            secret: TOTP secret
            code: Code to verify
            window: Number of time windows to check (allows for clock drift)
            
        Returns:
            True if code is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=window)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list[str]:
        """
        Generate backup codes for MFA recovery.
        
        Args:
            count: Number of codes to generate
            
        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8 character hex code
            codes.append(f"{code[:4]}-{code[4:]}")  # Format: XXXX-XXXX
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash a backup code for storage."""
        return get_password_hash(code)
    
    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """Verify a backup code against its hash."""
        return verify_password(code, hashed_code)


# API Key utilities
def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.
    
    Returns:
        Tuple of (full_key, prefix, hashed_key)
    """
    # Generate key with prefix
    key = f"lex_{secrets.token_urlsafe(32)}"
    prefix = key[:12]
    hashed_key = get_password_hash(key)
    
    return key, prefix, hashed_key


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return verify_password(plain_key, hashed_key)


# Session utilities
def generate_session_id() -> str:
    """Generate a unique session ID."""
    return secrets.token_urlsafe(32)


# Utility functions
def generate_verification_token() -> str:
    """Generate a verification token for email verification."""
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """Generate a password reset token."""
    return secrets.token_urlsafe(32)
