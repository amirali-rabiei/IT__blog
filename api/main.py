# from fastapi import Depends, FastAPI, HTTPException, Query
# from sqlmodel import Field, Session, SQLModel, create_engine, select
# # from pydantic import BaseModel
# from enum import Enum
# from datetime import datetime
# from typing import Annotated
# from fastapi.middleware.cors import CORSMiddleware


# # database -------
# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# def get_session():
#     with Session(engine) as session:
#         yield session


# SessionDep = Annotated[Session, Depends(get_session)]


# # enums -----------------
# # class blog_state(str,Enum):
# #     published = "published"
# #     unpublished = "unpublished"

# class blog_lan(str, Enum):
#     english = "english"
#     arabic = "arabic"
#     persion = "persion"


# # models -----------------
# class Blog(SQLModel, table=True):
#     blog_id: int | None = Field(default=None, primary_key=True)
#     title: str = Field(default="no title", index=True)
#     content: str = "defoult content"
#     publisher: str = "admin"
#     img: str | None = None
#     created_at: str | None = None
#     language: str


# class admin(SQLModel):

#     admin_id: int | None = Field(default=None, primary_key=True)
#     admin_name: str = Field(default="admin", index=True)


# # api s -----------
# app = FastAPI()

# # cors
# origins = [
#     "http://localhost:5173",
#     "https://it-blog.vercel.app"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


# @app.get("/")
# def index():
#     return {'data': "index"}


# @app.get("/api/blogs")
# def all_blog(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100
# ) -> list[Blog]:
#     get_blogs = session.exec(select(Blog).offset(offset).limit(limit)).all()
#     return get_blogs


# @app.get("/api/blogs/{blog_id}")
# def show_with_id(
#     session: SessionDep,
#     blog_id: int
# ) -> Blog:
#     get_blog = session.get(Blog, blog_id)
#     if not get_blog:
#         raise HTTPException(
#             status_code=404, detail=f"blog not found with id : {blog_id}")
#     return get_blog


# @app.post('/api/blog')
# def create_blog(blog: Blog, session: SessionDep) -> Blog:
#     session.add(blog)
#     session.commit()
#     session.refresh(blog)
#     return {'data': blog}


# @app.delete("/api/blogs/{blog_id}")
# async def delete_blog(
#     session: SessionDep,
#     blog_id: int
# ):
#     get_blog = session.get(Blog, blog_id)
#     if not get_blog:
#         raise HTTPException(
#             status_code=404, detail=f"blog not found with id : {blog_id}")
#     session.delete(get_blog)
#     session.commit()
#     return {"ok": True}


# @app.patch("/api/blogs/{blog_id}")
# async def update_blog(
#     session: SessionDep,
#     update_blog: Blog,
#     blog_id: int
# ):
#     get_blog = session.get(Blog, blog_id)
#     if not get_blog:
#         raise HTTPException(
#             status_code=404, detail=f"blog not found with id : {blog_id}")
#     get_blog.sqlmodel_update(update_blog)
#     session.add(get_blog)
#     session.commit()
#     session.refresh(get_blog)
#     return get_blog


# from fastapi import Depends, FastAPI, HTTPException, Query
# from sqlmodel import Field, Session, SQLModel, create_engine, select
# # from pydantic import BaseModel
# from enum import Enum
# from datetime import datetime
# from typing import Annotated


# # database -------
# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# def get_session():
#     with Session(engine) as session:
#         yield session


# SessionDep = Annotated[Session, Depends(get_session)]


# # enums -----------------
# # class blog_state(str,Enum):
# #     published = "published"
# #     unpublished = "unpublished"

# class blog_lan(str, Enum):
#     english = "english"
#     arabic = "arabic"
#     persion = "persion"


# # models -----------------
# class Blog(SQLModel, table=True):
#     blog_id: int | None = Field(default=None, primary_key=True)
#     title: str = Field(default="no title", index=True)
#     content: str = "defoult content"
#     publisher: str = "admin"
#     img: str | None = None
#     created_at: str | None = None
#     language: str


# class admin(SQLModel):
#     admin_id: int | None = Field(default=None, primary_key=True)
#     admin_name: str = Field(default="admin", index=True)


# app = FastAPI()


# # api s -----------


# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()


# @app.get("/")
# def index():
#     return {'data': "index"}


# @app.get("/api/blogs")
# def all_blog(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100
# ) -> list[Blog]:
#     get_blogs = session.exec(select(Blog).offset(offset).limit(limit)).all()
#     return get_blogs


# @app.get("/api/blogs/{blog_id}")
# def show_with_id(
#     session: SessionDep,
#     blog_id: int
# ) -> Blog:
#     get_blog = session.get(Blog, blog_id)
#     if not get_blog:
#         raise HTTPException(
#             status_code=404, detail=f"blog not found with id : {blog_id}")
#     return get_blog


# @app.post('/api/blog')
# def create_blog(blog: Blog, session: SessionDep) -> Blog:
#     session.add(blog)
#     session.commit()
#     session.refresh(blog)
#     return {'data': blog}


# @app.delete("/api/blogs/{blog_id}")
# async def delete_blog(
#     session: SessionDep,
#     blog_id: int
# ):
#     get_blog = session.get(Blog, blog_id)
#     if not get_blog:
#         raise HTTPException(
#             status_code=404, detail=f"blog not found with id : {blog_id}")
#     session.delete(get_blog)
#     session.commit()
#     return {"ok": True}


# @app.patch("/api/blog/{blog_id}")
# def update_blog

"""
Single-file FastAPI backend for a company site with a single admin.
Features:
- SQLite database (SQLAlchemy)
- Models: Product, Award, BlogPost, About (single row), Admin (single user)
- Public read endpoints for products, awards, blog, about
- Admin CRUD endpoints protected by a simple API token (header: X-Admin-Token)
- Image upload support: files saved to ./uploads and served as static files
- All code in one Python file. Change ADMIN_USERNAME/ADMIN_PASSWORD/ADMIN_TOKEN before production.

Dependencies:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- python-multipart

Install: pip install fastapi uvicorn sqlalchemy pydantic python-multipart
Run: python fastapi_singlefile_admin_backend.py

Note: This is a compact demo implementation. For production use:
- Use hashed passwords (e.g., passlib)
- Use proper auth (JWT/OAuth2) and HTTPS
- Add validation, rate-limiting, CORS and secure file handling
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import shutil
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site_data.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Simple admin config (change before production) ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"  # CHANGE this to a strong password
ADMIN_TOKEN = "change-me-to-a-strong-random-token"  # change this
# ----------------------------------------------------

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


app = FastAPI(title="Company Single-File Backend")

origins = [
    "http://localhost:5173",
    "https://it-blog.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)  # path relative to uploads


class Award(Base):
    __tablename__ = "awards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)


class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)


class About(Base):
    __tablename__ = "about"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)

# --- Pydantic schemas ---


class ProductRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]

    class Config:
        orm_mode = True


class ProductWrite(BaseModel):
    title: str
    description: Optional[str] = None


class AwardRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]

    class Config:
        orm_mode = True


class BlogRead(BaseModel):
    id: int
    title: str
    content: Optional[str]
    image: Optional[str]

    class Config:
        orm_mode = True


class AboutRead(BaseModel):
    id: int
    content: Optional[str]

    class Config:
        orm_mode = True


# --- App and utilities ---
app = FastAPI(title="Company Single-File Backend")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple admin dependency


def require_admin(x_admin_token: Optional[str] = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(
            status_code=401, detail="Unauthorized: invalid or missing X-Admin-Token header")
    return True

# Helpers for file saving


def save_upload(file: UploadFile) -> str:
    """Save uploaded file to uploads dir and return relative path (to /uploads)."""
    ext = os.path.splitext(file.filename)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, new_name)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/uploads/{new_name}"

# --- Public endpoints ---


@app.get("/products", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return p


@app.get("/awards", response_model=List[AwardRead])
def list_awards(db: Session = Depends(get_db)):
    return db.query(Award).all()


@app.get("/blog", response_model=List[BlogRead])
def list_blog(db: Session = Depends(get_db)):
    return db.query(BlogPost).all()


@app.get("/blog/{post_id}", response_model=BlogRead)
def get_blog(post_id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Blog post not found")
    return post


@app.get("/about", response_model=Optional[AboutRead])
def get_about(db: Session = Depends(get_db)):
    about = db.query(About).first()
    return about

# --- Admin / protected endpoints ---


@app.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...)):
    """Very simple login: returns ADMIN_TOKEN if username/password match constants."""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"token": ADMIN_TOKEN}
    raise HTTPException(401, "Invalid credentials")

# Product CRUD


@app.post("/admin/products", response_model=ProductRead, dependencies=[Depends(require_admin)])
def create_product(
    title: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    img_path = None
    if image:
        img_path = save_upload(image)
    p = Product(title=title, description=description, image=img_path)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/admin/products/{product_id}", response_model=ProductRead, dependencies=[Depends(require_admin)])
def update_product(
    product_id: int,
    title: str = Form(...),
    description: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    p.title = title
    p.description = description
    if image:
        p.image = save_upload(image)
    db.commit()
    db.refresh(p)
    return p


@app.delete("/admin/products/{product_id}", dependencies=[Depends(require_admin)])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"ok": True}

# Awards CRUD


@app.post("/admin/awards", response_model=AwardRead, dependencies=[Depends(require_admin)])
def create_award(title: str = Form(...), description: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    img_path = None
    if image:
        img_path = save_upload(image)
    a = Award(title=title, description=description, image=img_path)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@app.put("/admin/awards/{award_id}", response_model=AwardRead, dependencies=[Depends(require_admin)])
def update_award(award_id: int, title: str = Form(...), description: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    a = db.query(Award).filter(Award.id == award_id).first()
    if not a:
        raise HTTPException(404, "Award not found")
    a.title = title
    a.description = description
    if image:
        a.image = save_upload(image)
    db.commit()
    db.refresh(a)
    return a


@app.delete("/admin/awards/{award_id}", dependencies=[Depends(require_admin)])
def delete_award(award_id: int, db: Session = Depends(get_db)):
    a = db.query(Award).filter(Award.id == award_id).first()
    if not a:
        raise HTTPException(404, "Award not found")
    db.delete(a)
    db.commit()
    return {"ok": True}

# Blog CRUD


@app.post("/admin/blog", response_model=BlogRead, dependencies=[Depends(require_admin)])
def create_blog(title: str = Form(...), content: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    img_path = None
    if image:
        img_path = save_upload(image)
    b = BlogPost(title=title, content=content, image=img_path)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@app.put("/admin/blog/{post_id}", response_model=BlogRead, dependencies=[Depends(require_admin)])
def update_blog(post_id: int, title: str = Form(...), content: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog post not found")
    b.title = title
    b.content = content
    if image:
        b.image = save_upload(image)
    db.commit()
    db.refresh(b)
    return b


@app.delete("/admin/blog/{post_id}", dependencies=[Depends(require_admin)])
def delete_blog(post_id: int, db: Session = Depends(get_db)):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog post not found")
    db.delete(b)
    db.commit()
    return {"ok": True}

# About (single row)


@app.post("/admin/about", dependencies=[Depends(require_admin)])
def set_about(content: str = Form(...), db: Session = Depends(get_db)):
    about = db.query(About).first()
    if not about:
        about = About(content=content)
        db.add(about)
    else:
        about.content = content
    db.commit()
    return {"ok": True}


@app.delete("/admin/about", dependencies=[Depends(require_admin)])
def delete_about(db: Session = Depends(get_db)):
    about = db.query(About).first()
    if about:
        db.delete(about)
        db.commit()
    return {"ok": True}

# Endpoint to upload arbitrary image and get its URL


@app.post("/admin/upload", dependencies=[Depends(require_admin)])
def upload_image(file: UploadFile = File(...)):
    path = save_upload(file)
    return {"url": path}

# Utility: create default admin data if not present (optional)


def ensure_default_about(db: Session):
    if not db.query(About).first():
        db.add(About(content="Write your 'About us' here."))
        db.commit()

# Startup event


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        ensure_default_about(db)
    finally:
        db.close()

# Simple health check


@app.get("/ping")
def ping():
    return {"pong": True}


if __name__ == "__main__":
    import uvicorn
    print("Starting app on http://127.0.0.1:8000 — uploads served at /uploads — change ADMIN_TOKEN and ADMIN_PASSWORD before production")
    uvicorn.run(app, host="0.0.0.0", port=8000)
