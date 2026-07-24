from typing import Any
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from supabase_auth.errors import AuthApiError
from app.core.dependencies import get_current_user
from app.core.supabase_client import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Auth"])

class SignUpRequest(BaseModel):
    email: str | None = None
    password: str | None = None

class LoginRequest(BaseModel):
    email: str | None = None
    password: str | None = None

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignUpRequest):
    # Validate missing/empty email or password
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"}
        )
    
    try:
        supabase = get_supabase_client()
        res = supabase.auth.sign_up({
            "email": payload.email.strip(),
            "password": payload.password.strip()
        })
        
        user_data = None
        if res.user:
            user_data = res.user.model_dump(mode="json") if hasattr(res.user, "model_dump") else json.loads(json.dumps(res.user.__dict__, default=str))
            
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"user": user_data}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)}
        )

@router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest):
    # Validate missing/empty email or password
    if not payload.email or not payload.email.strip() or not payload.password or not payload.password.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"}
        )

    try:
        supabase = get_supabase_client()
        res = supabase.auth.sign_in_with_password({
            "email": payload.email.strip(),
            "password": payload.password.strip()
        })

        if not res.session:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid login credentials"}
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token
            }
        )
    except AuthApiError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user: Any = Depends(get_current_user)):
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except Exception:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)
