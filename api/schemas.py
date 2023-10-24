from pydantic import BaseModel
from typing import List
import datetime


class PostBase(BaseModel):
    user_id: str | None = None
    title: str | None = None
    content: str | None = None


class PostCreate(PostBase):
    tags: List[str]
    category: str


class TagURL(BaseModel):
    tag_name: str
    url: str


class PostShow(PostBase):
    post_id: str | None = None
    username: str
    created_at: datetime.datetime
    updated_at: str | None = None
    published_at: str | None = None
    tag_urls: List[TagURL] | None = None
    category: str


class Post(PostBase):
    description: str | None = None
    summary: str | None = None
    is_published: str
    slug: str | None = None
    like: str | None = None
    dislike: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    published_at: str | None = None

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    name: str
    password: str


class User(UserBase):
    user_id: str
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True
