from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse
from app.core.supabase_client import get_supabase_client

public_router = APIRouter(prefix="/public", tags=["Public"])
protected_router = APIRouter(prefix="/protected", tags=["Protected"])

@public_router.get("/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@protected_router.get("/profile", status_code=status.HTTP_200_OK)
def protected_profile(authorization: str | None = Header(None)):
    if not authorization:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"}
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Access token required"}
        )
    
    token = parts[1].strip()

    try:
        supabase = get_supabase_client()
        res = supabase.auth.get_user(token)
        
        if not res or not res.user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or expired token"}
            )
            
        user = res.user
        created_at = str(user.created_at) if hasattr(user, "created_at") and user.created_at else None
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "created_at": created_at
                }
            }
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid or expired token"}
        )
