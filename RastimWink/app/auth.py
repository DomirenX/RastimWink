from datetime import datetime, timedelta
import os
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.user import get_user_by_email, get_user_by_id

SECRET_KEY = os.getenv("SECRET_KEY", "krasnodiplomshik")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)
        user_id = int(sub)
    except (JWTError, ValueError):
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED)
    return user