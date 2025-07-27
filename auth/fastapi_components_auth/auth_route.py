from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from fastapi_components_auth.auth_service import AuthService, Token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

def create_auth_router(auth_service: AuthService) -> APIRouter:
    router = APIRouter()
    ACCESS_TOKEN_EXPIRE_MINUTES = auth_service.ACCESS_TOKEN_EXPIRE_MINUTES

    @router.post("/token", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        access_token = auth_service.create_access_token(
            user_object=user,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.get("/me")
    async def read_users_me(current_user = Depends(auth_service.get_current_user)):
        return current_user

    return router