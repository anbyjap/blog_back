from pydantic import BaseModel


class PostBase(BaseModel):
    post_id: str | None = None
    user_id: str | None = None
    title: str | None = None
    description: str | None = None
    summary: str | None = None
    content: str | None = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
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
    password: str


class User(UserBase):
    user_id: int
    is_active: bool
    posts: list[Post] = []

    class Config:
        orm_mode = True