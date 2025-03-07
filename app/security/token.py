from jose import jwt
from app.security.config import settings
from datetime import timedelta, UTC, datetime

def create_access_token(user_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(int(settings.ACCESS_TOKEN_EXPIRE))
    encoded_jwt = jwt.encode(
        dict(sub=str(user_id), exp=expire),
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
    
def get_current_user(access_token: str) -> str:
    payload = jwt.decode(
        access_token, 
        settings.SECRET_KEY, 
        algorithms=[settings.ALGORITHM]
    )
    user_id = payload.get("sub")
    return user_id
    
def authorize_user(access_token: str, user_id: str) -> bool:
    current_user = get_current_user(access_token)
    return current_user == user_id