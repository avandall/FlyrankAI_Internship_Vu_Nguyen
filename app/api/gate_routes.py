from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.core.dependencies import get_current_user

public_router = APIRouter(prefix="/public", tags=["Public"])
protected_router = APIRouter(prefix="/protected", tags=["Protected"])

@public_router.get("/info", status_code=status.HTTP_200_OK)
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@protected_router.get("/profile", status_code=status.HTTP_200_OK)
def protected_profile(user: Any = Depends(get_current_user)):
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

@protected_router.get("/dashboard", status_code=status.HTTP_200_OK)
def protected_dashboard(user: Any = Depends(get_current_user)):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Welcome to dashboard",
            "user_id": user.id
        }
    )
