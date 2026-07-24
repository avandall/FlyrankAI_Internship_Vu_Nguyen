from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from app.core.supabase_client import get_supabase_client

router = APIRouter(prefix="/auth", tags=["Auth"])

class SignUpRequest(BaseModel):
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
