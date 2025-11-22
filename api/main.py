from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.orm import sessionmaker, Session
import os
import shutil
import uuid

# ------------------------------
# Paths & Database
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site_data.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------------------
# Database Models
# ------------------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)         # 👈 اضافه شد
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)   # 👈 اضافه شد

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
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class About(Base):
    __tablename__ = "about"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)


# ------------------------------
# Pydantic Schemas
# ------------------------------
class ProductRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: Optional[str]
    image: Optional[str]
    created_at: Optional[datetime]
    class Config:
        orm_mode = True

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
    description: Optional[str]
    content: Optional[str]
    image: Optional[str]
    created_at: Optional[datetime]
    class Config:
        orm_mode = True

class AboutRead(BaseModel):
    id: int
    content: Optional[str]
    class Config:
        orm_mode = True


# ------------------------------
# FastAPI App
# ------------------------------
app = FastAPI(title="Company Backend")

origins = [
    "http://localhost:5173",
    "https://it-blog.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ------------------------------
# Utils
# ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_upload(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, new_name)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/uploads/{new_name}"


# ------------------------------
# PUBLIC ENDPOINTS
# ------------------------------

# --- PRODUCT ---
@app.get("/products", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return p


# --- AWARD ---
@app.get("/awards", response_model=List[AwardRead])
def list_awards(db: Session = Depends(get_db)):
    return db.query(Award).all()


# --- BLOG ---
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
    return db.query(About).first()


# ------------------------------
# ADMIN ENDPOINTS
# ------------------------------
@app.post("/admin/login")
def admin_login(username: str = Form(...), password: str = Form(...)):
    return {"ok": True}  # فقط تستی


# --- PRODUCT ADMIN ---
@app.post("/admin/products", response_model=ProductRead)
def create_product(
    title: str = Form(...),
    description: str = Form(None),
    content: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    img_path = save_upload(image) if image else None
    p = Product(title=title, description=description, content=content, image=img_path)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.put("/admin/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    title: str = Form(...),
    description: str = Form(None),
    content: str = Form(None),
    image: UploadFile = File(None),
    image_path: str = Form(None),
    db: Session = Depends(get_db)
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")

    p.title = title
    p.description = description
    p.content = content

    if image:
        p.image = save_upload(image)
    elif image_path:
        p.image = image_path

    db.commit()
    db.refresh(p)
    return p


@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"ok": True}


# --- AWARD ADMIN ---
@app.post("/admin/awards", response_model=AwardRead)
def create_award(title: str = Form(...), description: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db)):
    img_path = save_upload(image) if image else None
    a = Award(title=title, description=description, image=img_path)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# --- BLOG ADMIN ---
@app.post("/admin/blog", response_model=BlogRead)
def create_blog(
    title: str = Form(...),
    description: str = Form(None),
    content: str = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    img_path = save_upload(image) if image else None
    b = BlogPost(title=title, description=description, content=content, image=img_path)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@app.put("/admin/blog/{post_id}", response_model=BlogRead)
def update_blog(
    post_id: int,
    title: str = Form(...),
    description: str = Form(None),
    content: str = Form(None),
    image: UploadFile = File(None),
    image_path: str = Form(None),
    db: Session = Depends(get_db)
):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog not found")

    b.title = title
    b.description = description
    b.content = content

    if image:
        b.image = save_upload(image)
    elif image_path:
        b.image = image_path

    db.commit()
    db.refresh(b)
    return b


@app.delete("/admin/blog/{post_id}")
def delete_blog(post_id: int, db: Session = Depends(get_db)):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog not found")

    db.delete(b)
    db.commit()
    return {"ok": True}


# --- ABOUT ---
@app.post("/admin/about")
def set_about(content: str = Form(...), db: Session = Depends(get_db)):
    about = db.query(About).first()
    if not about:
        about = About(content=content)
        db.add(about)
    else:
        about.content = content
    db.commit()
    return {"ok": True}



@app.post("/admin/upload")
def upload_image(file: UploadFile = File(...)):
    path = save_upload(file)
    return {"url": path}


# ------------------------------
# HEALTH CHECK
# ------------------------------
@app.get("/ping")
def ping():
    return {"pong": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
