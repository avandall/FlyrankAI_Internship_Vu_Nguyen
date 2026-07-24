from fastapi import Header, status
from fastapi.responses import JSONResponse
from app.core.supabase_client import get_supabase_client

class AuthException(Exception):
    def __init__(self, message: str):
        self.message = message

def get_current_user(authorization: str | None = Header(None)):
    if not authorization:
        raise AuthException("Access token required")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise AuthException("Access token required")
    
    token = parts[1].strip()

    try:
        supabase = get_supabase_client()
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            raise AuthException("Invalid or expired token")
        return res.user
    except AuthException:
        raise
    except Exception:
        raise AuthException("Invalid or expired token")
