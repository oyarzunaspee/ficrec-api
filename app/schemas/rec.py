from pydantic import BaseModel, Field, HttpUrl, field_validator
from beanie import Document
from datetime import datetime
from typing import List
import nh3

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
    async def query(cls, reclist_id: str, query_list: bool, public: bool = False) -> list:
        return await Rec.find(Rec.reclist_id == reclist_id, Rec.deleted == False).to_list()
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('summary')
    @classmethod
    def validate_summary(cls, value: str) -> str:
        if value:
            value = nh3.clean(value)
        return value
    
    @field_validator('notes')
    @classmethod
    def validate_note(cls, value: str) -> str:
        if value:
            value = nh3.clean(value)
        return value
    
    @field_validator('words')
    @classmethod
    def validate_words(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('warnings')
    @classmethod
    def validate_warnings(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('chapters')
    @classmethod
    def validate_chapters(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('fandom')
    @classmethod
    def validate_fandom(cls, value: list) -> list:
        new_value = []
        for tag in value:
            new_value.append(nh3.clean(tag))
        return new_value
    
    @field_validator('ship')
    @classmethod
    def validate_ship(cls, value: list) -> list:
        new_value = []
        for tag in value:
            new_value.append(nh3.clean(tag))
        return new_value
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, value: list) -> list:
        new_value = []
        for tag in value:
            new_value.append(nh3.clean(tag))
        return new_value
