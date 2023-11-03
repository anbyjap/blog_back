from pydantic import BaseModel
from typing import List
import datetime


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    emoji: str
    tags: List[str]
    category: str
    slug: str


class TagURL(BaseModel):
    tag_id: str
    tag_name: str
    url: str


class PostCard(BaseModel):
    emoji: str
    post_id: str | None = None
    slug: str
    title: str | None = None
    username: str
    created_at: datetime.datetime
    updated_at: str | None = None
    published_at: str | None = None
    category: str


class PostShow(PostBase):
    emoji: str
    created_at: datetime.datetime
    username: str
    title: str | None = None
    tag_urls: List[TagURL] | None = None


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
