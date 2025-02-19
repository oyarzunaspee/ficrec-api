from pydantic import BaseModel, Field, SecretStr, HttpUrl, computed_field
from beanie import Document
from pydantic.types import Base64Str
from datetime import timedelta, datetime
from jose import jwt
from typing import List
import nh3
import os
from passlib.context import CryptContext
PW_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    
    def get_current_user(self):
        payload = jwt.decode(self.access_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: str = payload.get("user_id")
        return user_id

    @classmethod
    def create_access_token(cls, user):
        expire = datetime.now() + timedelta(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
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

class RecListConfig(BaseModel):
    fandom: bool = False
    ship: bool = False
    warnings: bool = False
    tags: bool = False
    chapters: bool = False

class User(Document):
    username: str = Field(...)
    password: SecretStr = Field(..., exclude=True)
    bio: str = Field(None)
    avatar: Base64Str = Field(None)
    highlight: str = Field(None)
    dark_mode: bool = False
    is_active: bool = Field(True, exclude=True)

    class Settings:
        name = "users"

    @classmethod
    def hash_password(cls, password: str):
        return PW_CONTEXT.hash(password)

    @classmethod
    def find_by_username(cls, username: str):
        username_exists = User.find_one(User.username == username)
        return username_exists
    
    def verify_password(self, password):
        return PW_CONTEXT.verify(password, self.password.get_secret_value())
    

class RecList(Document):
    user_id: str = Field(..., frozen=True)
    name: str
    about: str = Field(None)
    config: RecListConfig = Field(None, exclude=True)
    private: bool = False
    created: str = Field(datetime.today().strftime("%d-%m-%Y"), exclude=True, frozen=True)
    deleted: bool = Field(False, exclude=True)

    class Settings:
        name = "reclists"

class Rec(Document):
    user_id: str = Field(..., frozen=True)
    reclist_id: str = Field(..., frozen=True)
    title: str
    author: str
    summary: str = Field(None)
    notes: str = Field(None)
    words: int
    warnings: str
    rating: str
    fandom: List[str]
    ship: List[str] = []
    tags: List[str] = []
    language: str
    created: str = Field(datetime.today().strftime("%d-%m-%Y"), exclude=True, frozen=True)
    chapters: str
    url: HttpUrl
    deleted: bool = Field(False, exclude=True)

    class Settings:
        name = "recs"

    @computed_field
    def word_count(self) -> str:
        if self.words >= 1000:
            comma_separated = "{:,}".format(self.words)
            thousand_chars = str(self.words)[:comma_separated.find(",")]
            return f"{thousand_chars}k words"
        else:
            return f"{self.words} words"
    
    def clean_data(self):
        self.title = nh3.clean(self.title)
        self.author = nh3.clean(self.author)
        if self.summary:
            self.summary = nh3.clean(self.summary)
        if self.notes:
            self.notes = nh3.clean(self.notes)
        self.warnings = nh3.clean(self.warnings)
        self.rating = nh3.clean(self.rating)
        self.language = nh3.clean(self.language)
        self.chapters = nh3.clean(self.chapters)
        self.fandom = self.clean_list(self.fandom)
        self.ship = self.clean_list(self.ship)
        self.tags = self.clean_list(self.tags)
    
    def clean_list(self, list_to_clean: list):
        if not list_to_clean:
            return list_to_clean
        new_list = list()
        for item in list_to_clean:
            new_list.append(nh3.clean(item))
        return new_list
