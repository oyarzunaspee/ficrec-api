from pydantic import BaseModel, Field, field_validator
from beanie import Document
from datetime import datetime
import nh3
from typing import Union

class ReclistForm(BaseModel):
    name: str = None
    about: str = None


class RecListConfig(BaseModel):
    fandom: bool = False
    ship: bool = False
    warnings: bool = False
    tags: bool = False
    chapters: bool = False    

class RecList(Document):
    user_id: str = Field(..., frozen=True, exclude=True)
    name: str
    about: str | None = None
    config: RecListConfig
    private: bool = False
    created: str = Field(datetime.today().strftime("%d-%m-%Y"), exclude=True, frozen=True)
    deleted: bool = Field(False, exclude=True)

    class Settings:
        name = "reclist"

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        return nh3.clean(value)
    
    @field_validator('about')
    @classmethod
    def validate_about(cls, value: str) -> str:
        if value:
            value = nh3.clean(value)
        return value

    @classmethod
    async def query(cls, user_id: str, public: bool = False) -> list:
        if not public:
            return await cls.find(cls.user_id == user_id, cls.deleted == False).to_list()
        if public:
            return await cls.find(cls.user_id == user_id, cls.private == False, cls.deleted == False).to_list()
    
    @classmethod
    async def query_item(cls, reclist_id: str, public: bool = False) -> Union[object, None]:
        try:
            reclist = await cls.get(reclist_id)
            if reclist.private and public:
                return None
            elif reclist.deleted:
                return None
            else:
                return reclist
        except:
            return None