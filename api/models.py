from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP
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
    title = Column(String, index=True)
    meta_title = Column(String, index=True)
    slug = Column(String, index=True)
    content = Column(String, index=True)
    summary = Column(String, index=True)
    is_published = Column(Boolean, default=True)
    like = Column(Integer, index=True)
    dislike = Column(Integer, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    published_at = Column(TIMESTAMP)

    user = relationship("User", back_populates="posts")
    post_tags = relationship("PostTag", back_populates="post")  # Corrected attribute name
    post_category = relationship("PostCategory", back_populates="posts")


class PostTag(Base):
    __tablename__ = "post_tag"

    post_tag_id = Column(String, primary_key=True, index=True)  # Define a primary key column
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


class PostCategory(Base):
    __tablename__ = "post_category"

    category_id = Column(String, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.post_id"))

    posts = relationship("Post", back_populates="post_category")
    categories = relationship("Category", back_populates="post_category")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("post_category.category_id"), index=True)
    title = Column(String, index=True)
    meta_title = Column(String, index=True)
    context = Column(String, index=True)

    post_category = relationship("PostCategory", back_populates="categories")

