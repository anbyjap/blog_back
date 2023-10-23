from pydantic import BaseModel
import datetime


class PostBase(BaseModel):
    post_id: int | None = None
    user_id: int | None = None
    title: str | None = None
    content: str | None = None


class PostCreate(PostBase):
    pass


class PostShow(PostBase):
    username: str
    created_at: datetime.datetime
    updated_at: str | None = None
    published_at: str | None = None


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
    user_id: int
    name: str
    password: str


class User(UserBase):
    user_id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True