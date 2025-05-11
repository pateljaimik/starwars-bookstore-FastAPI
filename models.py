from pydantic import BaseModel, HttpUrl
from typing import Optional

class FullUser(BaseModel):
    id: Optional[int] = None  # # we can use UUID for better unique Id's [str]
    username: str
    encrpt_password: str
    author_pseudonym: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    author_pseudonym: str

class Token(BaseModel):
    access_token: str
    token_type: str

class BookCreate(BaseModel):
    title: str
    description: str
    cover_image: Optional[HttpUrl] = None  # URL or path
    price: float

class BookResponse(BookCreate):
    id: int
    author_username: str
    author_pseudonym: str

class BookInternal(BookResponse):
    pass 

class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[HttpUrl] = None  # URL or path
    price: Optional[float] = None
 
