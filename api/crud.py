from sqlalchemy.orm import Session, joinedload

import models
import schemas
import datetime


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(user_id=user.user_id, name=user.name, email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).options(joinedload(models.Post.user)).offset(skip).limit(limit).all()


def create_user_post(db: Session, item: schemas.PostCreate):
    db_item = models.Post(**item.dict(), created_at=datetime.datetime.now())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_post(db: Session, post_id: int):
    """Retrieve a specific post by its ID."""
    return db.query(models.Post).filter(models.Post.post_id == post_id).first()
