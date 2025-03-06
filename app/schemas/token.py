from pydantic import BaseModel
from jose import jwt
from app.security.config import settings
from datetime import timedelta, datetime

class Token(BaseModel):
    access_token: str
    
    def get_current_user(self) -> str:
        payload = jwt.decode(
            self.access_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("user_id")
        return user_id

    @classmethod
    def create_access_token(cls, user: object) -> str:
        expire = datetime.now() + timedelta(int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        encoded_jwt = jwt.encode(
            dict(user_id=str(user.id), exp=expire),
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @classmethod
    def authorize_user(cls, token: str, user_id: str) -> bool:
        current_user = cls(access_token=token).get_current_user()
        return current_user == user_id