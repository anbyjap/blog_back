from sqlalchemy.orm import Session, joinedload

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
    db_user = models.User(user_id=uuid.uuid4(), name=user.name, email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Post)
        .options(
            joinedload(models.Post.user),
            joinedload(models.Post.post_tags).joinedload(models.PostTag.tag)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_user_post(db: Session, item: schemas.PostCreate):
    db_post = models.Post(post_id=str(uuid.uuid4()), user_id=item.user_id, title=item.title, content=item.content, created_at=datetime.datetime.now())
    db.add(db_post)
    db.flush()

    for tag_name in item.tags:
        # Check if the tag's name matches any title in the Tag table
        tag_instance = db.query(models.Tag).filter_by(meta_title=tag_name).first()

        if tag_instance:
            # If it does, add a record in the post_tag table associating the post with the tag
            post_tag_instance = models.PostTag(post_tag_id=str(uuid.uuid4()), post_id=db_post.post_id, tag_id=tag_instance.id)
            db.add(post_tag_instance)
            
    db.commit()
    db.refresh(db_post)

    return db_post


def get_post(db: Session, post_id: int):
    """Retrieve a specific post by its ID."""
    return db.query(models.Post).filter(models.Post.post_id == post_id).first()
