from pydantic import BaseModel, Field, SecretStr, HttpUrl, field_validator
from beanie import Document
from pydantic.types import Base64Str
from datetime import timedelta, datetime
from jose import jwt
from typing import List
import nh3
import os
import re
from passlib.context import CryptContext
PW_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserForm(BaseModel):
    username: str = Field(..., min_length=4)
    password: str = Field(..., min_length=6)
    match_password: str = Field(..., min_length=6)

    @classmethod
    def hash_password(cls, password: str):
        return PW_CONTEXT.hash(password)

    @field_validator('username')
    @classmethod
    def validate_username(cls, username: str):
        value = nh3.clean(username)

        if value[0].isnumeric():
            raise ValueError("username must not start with a number")

        if " " in value:
            raise ValueError("username must not contain spaces")

        regex = "^[a-z][a-z0-9*_-]+$"
        if not re.search(regex, value):
            raise ValueError("invalid username")
    
        return value.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        value = nh3.clean(password)
        return value


class Token(BaseModel):
    access_token: str
    
    def get_current_user(self):
        payload = jwt.decode(
            self.access_token, 
            os.getenv("SECRET_KEY"), 
            algorithms=[os.getenv("ALGORITHM")]
        )
        user_id = payload.get("user_id")
        return user_id

    @classmethod
    def create_access_token(cls, user):
        expire = datetime.now() + timedelta(int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
        encoded_jwt = jwt.encode(
            dict(user_id=str(user.id), exp=expire),
            os.getenv("SECRET_KEY"),
            algorithm=os.getenv("ALGORITHM")
        )
        return encoded_jwt
    
    @classmethod
    def authorize_user(cls, token, user_id):
        current_user = cls(access_token=token).get_current_user()
        return current_user == user_id

class User(Document):
    username: str
    password: SecretStr = Field(..., exclude=True)
    bio: str | None = None
    avatar: Base64Str | None = None
    highlight: str | None = None
    dark_mode: bool = False
    is_active: bool = Field(True, exclude=True)

    class Settings:
        name = "users"
    
    @classmethod
    async def query_item(cls, user_id: str, query_list: bool):
        user = await User.get(user_id)
        if user.is_active:
            return user
        elif not user.is_active:
            return None

    @classmethod
    async def find_by_username(cls, username: str):
        user = await User.find_one(User.username == username)
        return user
    
    def verify_password(self, password):
        return PW_CONTEXT.verify(password, self.password.get_secret_value())

class RecListConfig(BaseModel):
    fandom: bool = False
    ship: bool = False
    warnings: bool = False
    tags: bool = False
    chapters: bool = False    

class RecList(Document):
    user_id: str = Field(..., frozen=True)
    name: str
    about: str | None = None
    config: RecListConfig = Field(None, exclude=True)
    private: bool = False
    created: str = Field(datetime.today().strftime("%d-%m-%Y"), exclude=True, frozen=True)
    deleted: bool = Field(False, exclude=True)

    class Settings:
        name = "reclist"

    @field_validator('name')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('about')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)

    @classmethod
    async def query(cls, user_id: str, public: bool = False):
        if not public:
            return await cls.find(cls.user_id == user_id, cls.deleted == False).to_list()
        if public:
            return await cls.find(cls.user_id == user_id, cls.private == False, cls.deleted == False).to_list()
    
    @classmethod
    async def query_item(cls, reclist_id: str, public: bool = False):
        reclist = await cls.get(reclist_id)
        if reclist.private and public:
            return None
        elif reclist.deleted:
            return None
        else:
            return reclist

class Rec(Document):
    user_id: str = Field(..., frozen=True)
    reclist_id: str = Field(..., frozen=True)
    title: str
    author: str
    summary: str | None = None
    notes: str | None = None
    words: int
    warnings: str
    rating: str
    fandom: List[str]
    ship: List[str] = []
    tags: List[str] = []
    language: str
    chapters: str
    created: str = Field(datetime.today().strftime("%d-%m-%Y"), exclude=True, frozen=True)
    url: HttpUrl
    deleted: bool = Field(False, exclude=True)

    class Settings:
        name = "recs"
        
    @classmethod
    async def query(cls, reclist_id: str, query_list: bool, public: bool = False):
        return await Rec.find(Rec.reclist_id == reclist_id, Rec.deleted == False).to_list()
    
    @field_validator('title')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('summary')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('notes')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('words')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('warnings')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('rating')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('language')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
    
    @field_validator('chapters')
    @classmethod
    def validate_password(cls, value: str):
        return nh3.clean(value)
