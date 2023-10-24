from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional


import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Define allowed origins (domains) that are allowed to access your API
# origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Create the FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # You can restrict this to specific HTTP methods if needed
    allow_headers=["*"],  # You can restrict this to specific headers if needed
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    skip = 0
    limit = 100
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/post/")
def create_item_for_user(
    item: schemas.PostCreate, db: Session = Depends(get_db)
):
    if item.category not in ["tech", "idea"]:
        raise HTTPException(status_code=400, detail="specify category")
    return crud.create_user_post(db=db, item=item)


@app.get("/posts/", response_model=list[schemas.PostShow])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    posts = crud.get_posts(db, skip=skip, limit=limit, category=category, keyword=keyword)
    result_posts = []
    for post in posts:
        result = {
            "username": post.user.name,
            "user_id": post.user_id,
            "post_id": post.post_id,
            "title": post.title,
            "content": post.content,
            "created_at": post.created_at,
            "tag_urls": [{"tag_name": post_tag.tag.meta_title, "url": post_tag.tag.icon_image_url} for post_tag in post.post_tags],
            "category": post.category
        }
        result_posts.append(result)
    return result_posts


@app.delete("/posts/{post_id}/")
def delete_post(post_id: str, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"status": "success", "message": "Post deleted successfully"}
