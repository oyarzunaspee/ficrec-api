from pydantic import BaseModel, Field, SecretStr, field_validator
from beanie import Document
from pydantic.types import Base64Str
import nh3
import re
from app.security.crypt_context import PW_CONTEXT
from typing import Union

    
class PasswordForm(BaseModel):
    password: str = Field(..., min_length=6)
    match_password: str = Field(..., min_length=6)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return PW_CONTEXT.hash(password)

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        value = nh3.clean(password)
        return value

class UsernameForm(BaseModel):
    username: str = Field(..., min_length=4)

    @field_validator('username')
    @classmethod
    def validate_username(cls, username: str) -> str:
        value = nh3.clean(username)

        if value[0].isnumeric():
            raise ValueError("username must not start with a number")

        if " " in value:
            raise ValueError("username must not contain spaces")

        regex = "^[a-z][a-z0-9*_-]+$"
        if not re.search(regex, value):
            raise ValueError("invalid username")
    
        return value.lower()

class SignUpForm(UsernameForm, PasswordForm):
    pass

class UserProfileForm(BaseModel):
    bio: str = None
    avatar: Base64Str = None
    highlight: str | None = None

class User(Document):
    username: str
    password: SecretStr = Field(..., exclude=True)
    bio: str | None = None
    avatar: Base64Str | None = None
    is_active: bool = Field(True)

    class Settings:
        name = "users"
        
    @classmethod
    async def query_item(cls, user_id: str) -> Union[object, None]:
        user = await User.get(user_id)
        if user.is_active:
            return user
        elif not user.is_active:
            return None

    @classmethod
    async def find_by_username(cls, username: str) -> object:
        user = await User.find_one(User.username == username)
        return user
        
    def verify_password(self, password: str) -> bool:
        return PW_CONTEXT.verify(password, self.password.get_secret_value())