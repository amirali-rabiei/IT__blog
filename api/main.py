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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "site_data.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------------------------
# Database Models
# ---------------------------

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)
    language = Column(String(2), nullable=False, default="fa")  # fa, ar, en

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
    language = Column(String(2), nullable=False, default="fa")  # fa, ar, en

class About(Base):
    __tablename__ = "about"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    language = Column(String(2), nullable=False, default="fa")  # fa, ar, en

Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic Schemas
# ---------------------------

class ProductRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    image: Optional[str]
    language: str
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
    language: str
    class Config:
        orm_mode = True

class AboutRead(BaseModel):
    id: int
    content: Optional[str]
    class Config:
        orm_mode = True

class ActivityRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content: Optional[str]
    image: Optional[str]
    created_at: Optional[datetime]
    language: str
    class Config:
        orm_mode = True

# ---------------------------
# App Config
# ---------------------------

app = FastAPI(title="Company Single-File Backend")

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

# ---------------------------
# Utilities
# ---------------------------

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

# ---------------------------
# Public Endpoints
# ---------------------------

@app.get("/products", response_model=List[ProductRead])
def list_products(language: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Product)
    if language:
        query = query.filter(Product.language == language)
    return query.all()

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return p

@app.get("/blog", response_model=List[BlogRead])
def list_blog(language: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(BlogPost)
    if language:
        query = query.filter(BlogPost.language == language)
    return query.all()

@app.get("/blog/{post_id}", response_model=BlogRead)
def get_blog(post_id: int, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Blog post not found")
    return post

@app.get("/activities", response_model=List[ActivityRead])
def list_activities(language: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Activity)
    if language:
        query = query.filter(Activity.language == language)
    return query.all()

@app.get("/activities/{activity_id}", response_model=ActivityRead)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    return act

@app.get("/about", response_model=Optional[AboutRead])
def get_about(db: Session = Depends(get_db)):
    return db.query(About).first()

# ---------------------------
# Admin Endpoints
# ---------------------------

@app.post("/admin/products", response_model=ProductRead)
def create_product(title: str = Form(...), description: str = Form(None), image: UploadFile = File(None), language: str = Form("fa"), db: Session = Depends(get_db)):
    img_path = save_upload(image) if image else None
    p = Product(title=title, description=description, image=img_path, language=language)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.put("/admin/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, title: str = Form(...), description: str = Form(None), image: UploadFile = File(None), language: str = Form("fa"), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    p.title = title
    p.description = description
    p.language = language
    if image:
        p.image = save_upload(image)
    db.commit()
    db.refresh(p)
    return p

@app.post("/admin/blog", response_model=BlogRead)
def create_blog(title: str = Form(...), content: str = Form(None), description: str = Form(None), image: UploadFile = File(None), language: str = Form("fa"), db: Session = Depends(get_db)):
    img_path = save_upload(image) if image else None
    b = BlogPost(title=title, description=description, content=content, image=img_path, language=language)
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
    language: str = Form("fa"),
    db: Session = Depends(get_db)
):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog post not found")
    b.title = title
    b.description = description
    b.content = content
    b.language = language
    if image:
        b.image = save_upload(image)
    elif image_path:
        b.image = image_path
    db.commit()
    db.refresh(b)
    return b

@app.post("/admin/activity", response_model=ActivityRead)
def create_activity(title: str = Form(...), description: str = Form(None), content: str = Form(None), image: UploadFile = File(None), language: str = Form("fa"), db: Session = Depends(get_db)):
    img_path = save_upload(image) if image else None
    act = Activity(title=title, description=description, content=content, image=img_path, language=language)
    db.add(act)
    db.commit()
    db.refresh(act)
    return act

@app.put("/admin/activity/{activity_id}", response_model=ActivityRead)
def update_activity(activity_id: int, title: str = Form(...), description: str = Form(None), content: str = Form(None), image: UploadFile = File(None), image_path: str = Form(None), language: str = Form("fa"), db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    act.title = title
    act.description = description
    act.content = content
    act.language = language
    if image:
        act.image = save_upload(image)
    elif image_path:
        act.image = image_path
    db.commit()
    db.refresh(act)
    return act

# ---------------------------
# Misc
# ---------------------------

@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    db.delete(p)
    db.commit()
    return {"ok": True}

@app.delete("/admin/blog/{post_id}")
def delete_blog(post_id: int, db: Session = Depends(get_db)):
    b = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not b:
        raise HTTPException(404, "Blog post not found")
    db.delete(b)
    db.commit()
    return {"ok": True}

@app.delete("/admin/activity/{activity_id}")
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    db.delete(act)
    db.commit()
    return {"ok": True}

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

@app.get("/ping")
def ping():
    return {"pong": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
