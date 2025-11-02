from datetime import datetime, timedelta
import os
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY", "krasnodiplomshik")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 48

def create_set_password_token(user_id: int):
    expire = datetime.utcnow() + timedelta(hours = TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm = ALGORITHM)

def verify_set_password_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return int(payload.get("sub"))
    except (JWTError, ValueError):
        return None