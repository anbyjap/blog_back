from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    posts = relationship("Post", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    emoji = Column(String, index=True)
    title = Column(String, index=True)
    meta_title = Column(String, index=True)
    slug = Column(String, index=True)
    content = Column(String, index=True)
    summary = Column(String, index=True)
    category = Column(String, index=True)
    is_published = Column(Boolean, default=True)
    like = Column(Integer, index=True)
    dislike = Column(Integer, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    published_at = Column(TIMESTAMP)

    __table_args__ = (UniqueConstraint("slug", "user_id", name="uix_slug_user_id"),)

    user = relationship("User", back_populates="posts")
    post_tags = relationship(
        "PostTag", back_populates="post"
    )  # Corrected attribute name


class PostTag(Base):
    __tablename__ = "post_tag"

    post_tag_id = Column(
        String, primary_key=True, index=True
    )  # Define a primary key column
    post_id = Column(String, ForeignKey("posts.post_id"))
    tag_id = Column(String, ForeignKey("tag.id"))

    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")


class Tag(Base):
    __tablename__ = "tag"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    meta_title = Column(String, index=True)
    icon_image_url = Column(String(500))  # new column for the S3 URL

    post_tags = relationship("PostTag", back_populates="tag")
