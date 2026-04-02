"""
Authentication and Authorization for DECOYABLE API

Provides API key and JWT-based authentication for securing API endpoints.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from decoyable.core.logging import get_logger

logger = get_logger("api.auth")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_HOURS", "24")) * 60


class User(BaseModel):
    """User model for authentication."""
    username: str
    email: Optional[str] = None
    disabled: bool = False
    roles: list[str] = []


class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    roles: list[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    if not SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable must be set")
    
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET_KEY not configured"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        roles: list = payload.get("roles", [])
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, roles=roles)
    
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify API key authentication.
    
    Args:
        api_key: API key from header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Get valid API keys from environment (comma-separated)
    valid_api_keys = os.getenv("VALID_API_KEYS", "").split(",")
    valid_api_keys = [key.strip() for key in valid_api_keys if key.strip()]
    
    if not valid_api_keys:
        logger.error("No valid API keys configured in VALID_API_KEYS environment variable")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key authentication not configured"
        )
    
    if api_key not in valid_api_keys:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    logger.info(f"API key authentication successful")
    return api_key


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
) -> TokenData:
    """
    Verify JWT bearer token authentication.
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return decode_access_token(credentials.credentials)


async def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> User:
    """
    Get current authenticated user from either API key or JWT token.
    
    Supports both authentication methods:
    - X-API-Key header
    - Authorization: Bearer <token> header
    
    Args:
        api_key: Optional API key from header
        credentials: Optional JWT bearer token
        
    Returns:
        Authenticated User object
        
    Raises:
        HTTPException: If authentication fails
    """
    # Try API key first
    if api_key:
        try:
            await verify_api_key(api_key)
            # For API key auth, return a system user
            return User(
                username="api_key_user",
                roles=["user", "scanner"]
            )
        except HTTPException:
            pass  # Try JWT next
    
    # Try JWT token
    if credentials:
        token_data = decode_access_token(credentials.credentials)
        return User(
            username=token_data.username,
            roles=token_data.roles
        )
    
    # No valid authentication provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide either X-API-Key or Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(required_role: str):
    """
    Dependency to require a specific role.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    
    Args:
        required_role: Role required to access the endpoint
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if required_role not in current_user.roles:
            logger.warning(
                f"User {current_user.username} attempted to access "
                f"endpoint requiring role '{required_role}'"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    
    return role_checker


# Optional: For public endpoints that don't require auth
async def get_optional_user(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None.
    
    For endpoints that have optional authentication.
    """
    try:
        return await get_current_user(api_key, credentials)
    except HTTPException:
        return None
