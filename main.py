from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import SecurityScopes
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import base64
import secrets
import os
import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

API_KEY = os.environ.get("BLOG_API_KEY")
admin_name = os.environ.get("BLOG_ADMIN_NAME")
admin_password = os.environ.get("BLOG_ADMIN_PASSWORD")
swagger_creds = {admin_name: admin_password}

app = FastAPI()

# Security
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials) -> bool:
    correct_password = swagger_creds.get(credentials.username)
    if not correct_password or not secrets.compare_digest(
        correct_password, credentials.password
    ):
        return False
    return True


def is_from_swagger_ui(request: Request):
    referrer = request.headers.get("referer")
    return referrer and ("/docs" in referrer or "/redoc" in referrer)


def get_api_key(request: Request, security_scopes: SecurityScopes):
    if is_from_swagger_ui(request):
        return API_KEY
    api_key = request.headers.get("X-API-KEY")
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
    return api_key


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json"]:
            auth = request.headers.get("Authorization")
            if not auth:
                response = Response(
                    headers={"WWW-Authenticate": "Basic"}, status_code=401
                )
                return response

            try:
                # credentials = HTTPBasicCredentials.parse_raw(auth)
                auth_scheme, auth_string = auth.split()
                username, password = (
                    base64.b64decode(auth_string).decode("utf-8").split(":")
                )
                credentials = HTTPBasicCredentials(username=username, password=password)

                if not verify_credentials(credentials):
                    raise HTTPException(status_code=401, detail="Unauthorized")
            except HTTPException:
                response = Response(
                    headers={"WWW-Authenticate": "Basic"}, status_code=401
                )
                return response

        response = await call_next(request)
        return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/startup")
def startup_server(
    security_scopes: SecurityScopes,
    api_key: str = Depends(get_api_key),
):
    return "startup completed"


@app.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/post/{user_id}")
def create_item_for_user(
    user_id: str,
    item: schemas.PostCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    if item.category not in ["tech", "idea"]:
        raise HTTPException(status_code=400, detail="specify category")
    return crud.create_user_post(db=db, user_id=user_id, item=item)


@app.get("/posts/{username}/{slug}/", response_model=schemas.PostShow)
def get_post(
    username: str,
    slug: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    post = crud.get_post(db, username, slug)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    result = {
        "username": post.user.name,
        "content": post.content,
        "post_id": post.post_id,
        "title": post.title,
        "created_at": post.created_at,
        "tag_urls": [
            {
                "tag_id": post_tag.tag.id,
                "tag_name": post_tag.tag.meta_title,
                "url": post_tag.tag.icon_image_url,
            }
            for post_tag in post.post_tags
        ],
    }

    return result


@app.get("/posts/", response_model=list[schemas.PostCard])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    tag_id: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    posts = crud.get_posts(
        db, skip=skip, limit=limit, category=category, keyword=keyword, tag_id=tag_id
    )
    result_posts = []
    for post in posts:
        result = {
            "username": post.user.name,
            "post_id": post.post_id,
            "title": post.title,
            "created_at": post.created_at,
            "category": post.category,
            "slug": post.slug,
        }
        result_posts.append(result)
    return result_posts


@app.get("/tags/{tag_id}", response_model=schemas.TagURL)
def read_tag(
    tag_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)
):
    tag = crud.get_tag(db, tag_id=tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"tag_id": tag.id, "tag_name": tag.meta_title, "url": tag.icon_image_url}


@app.delete("/posts/{post_id}/")
def delete_post(
    post_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"status": "success", "message": "Post deleted successfully"}
