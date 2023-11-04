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
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv


models.Base.metadata.create_all(bind=engine)


# .envファイルの内容を読み込見込む
load_dotenv()

API_KEY = os.environ.get("BLOG_API_KEY")
admin_name = os.environ.get("BLOG_ADMIN_NAME")
admin_password = os.environ.get("BLOG_ADMIN_PASSWORD")
swagger_creds = {admin_name: admin_password}

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ.get("BLOG_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserInDB(BaseModel):
    username: str
    hashed_password: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


# Utilities for JWT and password hashing
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, email: str):
    return crud.get_user_by_email(db, email=email)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get the current user
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)  # Use email to fetch the user
    if user is None:
        raise credentials_exception
    return user


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


@app.get("/startup")
def startup_server(
    security_scopes: SecurityScopes,
    api_key: str = Depends(get_api_key),
):
    return "startup completed"


# Login endpoint
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires  # use user.email
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}


@app.get("/validate")
def validate_api_key(
    api_key: str = Depends(get_api_key)
):
    # If the function `get_api_key` doesn't raise an HTTPException, the API key is valid.
    return {"status": "success", "message": "API key is valid."}



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


@app.post("/post/")
def create_item_for_user(
    item: schemas.PostCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    current_user: models.User = Depends(get_current_user)
):
    if item.category not in ["tech", "idea"]:
        raise HTTPException(status_code=400, detail="specify category")
    return crud.create_user_post(db=db, user_id=current_user.user_id, item=item)


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
        "emoji": post.emoji,
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
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    tag_id: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    posts = crud.get_posts(
        db, skip=skip, limit=limit, category=category, keyword=keyword, tag_id=tag_id, user_id=user_id
    )
    result_posts = []
    for post in posts:
        result = {
            "username": post.user.name,
            "emoji": post.emoji,
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


@app.get("/tags/", response_model=list[schemas.TagURL])
def read_all_tag(
    db: Session = Depends(get_db), api_key: str = Depends(get_api_key)
):
    tags = crud.get_all_tag(db)
    all_tags = []
    for tag in tags:
        all_tags.append(
            {
                "tag_id": tag.id,
                "tag_name": tag.meta_title,
                "url": tag.icon_image_url
            }
        )
    return all_tags

@app.delete("/posts/{post_id}/")
def delete_post(
    post_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key), current_user: models.User = Depends(get_current_user)
):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"status": "success", "message": "Post deleted successfully"}
