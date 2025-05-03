import hashlib
import secrets
from functools import wraps
from typing import Optional

class SecurityService:
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return (salt, key.hex())

    @staticmethod
    def verify_password(stored_salt: str, stored_key: str, password: str) -> bool:
        """Verify password against stored hash"""
        salt, key = SecurityService.hash_password(password, stored_salt)
        return secrets.compare_digest(key, stored_key)

def authenticate(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, '_authenticated', False):
            raise PermissionError("Authentication required")
        return func(self, *args, **kwargs)
    return wrapper

def authorize(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_role = getattr(self, '_user_role', None)
            if user_role != required_role:
                raise PermissionError(f"Requires {required_role} role")
            return func(self, *args, **kwargs)
        return wrapper
    return decorator