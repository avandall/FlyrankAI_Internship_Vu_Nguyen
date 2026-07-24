from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse

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
    return {"message": "Protected profile accessed", "token": token}
