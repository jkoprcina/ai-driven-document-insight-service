"""
Security service for JWT authentication, authorization, and input validation.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import re
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    """Token payload data."""
    sub: str  # Subject (user ID)
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    scopes: list = []

class Credentials(BaseModel):
    """User credentials."""
    username: str
    password: str

class SecurityManager:
    """Manage authentication, authorization, and input validation."""
    
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        """
        Initialize security manager.
        
        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Get bcrypt hash of password."""
        return self.pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.secret_key,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return payload.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize user input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        # Remove null bytes
        text = text.replace('\0', '')
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove dangerous characters (SQL injection prevention)
        dangerous_patterns = [
            r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\b)",
            r"(--|;|'|\"|\*)",
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        
        return text.strip()
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format (UUID).
        
        Args:
            session_id: Session ID
            
        Returns:
            Validation result
        """
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, session_id.lower()))
    
    @staticmethod
    def validate_question(question: str, min_length: int = 3) -> bool:
        """
        Validate question format.
        
        Args:
            question: Question text
            min_length: Minimum length
            
        Returns:
            Validation result
        """
        return len(question.strip()) >= min_length
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Validate uploaded filename.
        
        Args:
            filename: Filename
            
        Returns:
            Validation result
        """
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # Check allowed extensions
        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
        file_ext = "." + filename.split(".")[-1].lower()
        
        return file_ext in allowed_extensions
