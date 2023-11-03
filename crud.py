from sqlalchemy.orm import Session, joinedload
from typing import Optional
from sqlalchemy import or_

import models
import schemas
import uuid
import datetime


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        user_id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        hashed_password=fake_hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    tag_id: Optional[str] = None,
):
    # Starting the query
    query = db.query(models.Post).options(
        joinedload(models.Post.user),
        joinedload(models.Post.post_tags).joinedload(models.PostTag.tag),
    )

    # Filtering based on category
    if category:
        query = query.filter(models.Post.category == category)

    # Filtering based on keyword (searching within title or content)
    if keyword:
        query = query.filter(
            or_(
                models.Post.title.contains(keyword),
                models.Post.content.contains(keyword),
            )
        )

    # Filtering based on tag_id
    if tag_id:
        query = query.join(models.Post.post_tags).filter(
            models.PostTag.tag_id == tag_id
        )

    # Applying offset and limit
    posts = query.offset(skip).limit(limit).all()

    print(posts[0].slug)

    return posts


def create_user_post(db: Session, user_id: str, item: schemas.PostCreate):
    db_post = models.Post(
        post_id=str(uuid.uuid4()),
        user_id=user_id,
        title=item.title,
        content=item.content,
        created_at=datetime.datetime.now(),
        category=item.category,
        slug=item.slug,
    )
    db.add(db_post)
    db.flush()

    for tag_name in item.tags:
        # Check if the tag's name matches any title in the Tag table
        tag_instance = db.query(models.Tag).filter_by(meta_title=tag_name).first()

        if tag_instance:
            # If it does, add a record in the post_tag table associating the post with the tag
            post_tag_instance = models.PostTag(
                post_tag_id=str(uuid.uuid4()),
                post_id=db_post.post_id,
                tag_id=tag_instance.id,
            )
            db.add(post_tag_instance)

    db.commit()
    db.refresh(db_post)

    return db_post


def get_post(db: Session, username: str, slug: str):
    """Retrieve a specific post by username and slug."""
    return (
        db.query(models.Post)
        .join(models.User)
        .filter(models.User.name == username, models.Post.slug == slug)
        .first()
    )


def get_tag(db: Session, tag_id: int):
    """Retrieve a specific post by its ID."""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def get_all_tag(db: Session):
    """Get all tags"""
    return db.query(models.Tag).all()