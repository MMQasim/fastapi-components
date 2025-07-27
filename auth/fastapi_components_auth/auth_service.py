from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta,timezone
from typing import Callable, Any, Optional
import jwt


# === SCHEMAS ===
class Token(BaseModel):
    access_token: str
    token_type: str

# === AUTH SERVICE ===
class AuthService:
    def __init__(
        self,SECRET_KEY:str,
        get_user_by_identity: Callable[[str], Any],
        get_user_by_credentials: Callable[[str, str], Optional[Any]],
        get_identity_from_user: Callable[[Any], str],
        ALGORITHM:str="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES:int=60,
        verify_password_func: Optional[Callable[[str, str], bool]] = None,
        password_hash_func: Optional[Callable[[str], str]] = None,
    ):
        self.get_user_by_identity = get_user_by_identity
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
        self.get_user_by_credentials = get_user_by_credentials
        self.get_identity_from_user = get_identity_from_user
        self.verify_password_func = verify_password_func or self._default_verify_password
        self.password_hash_func = password_hash_func or self._default_hash_password
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

    def _default_verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def _default_hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def get_password_hash(self, password: str) -> str:
        return self.password_hash_func(password)

    def create_access_token(self, user_object: Any, expires_delta: timedelta = None):
        user_id = self.get_identity_from_user(user_object)
        to_encode = {"sub": user_id}
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def authenticate_user(self, username: str, password: str):
        user = self.get_user_by_credentials(username, password)
        return user

    async def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token"))):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        user = self.get_user_by_identity(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user