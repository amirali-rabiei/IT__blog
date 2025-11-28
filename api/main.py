from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os, shutil, uuid

# ---------------------------
# Paths
# ---------------------------
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
class BlogPost(Base):
    __tablename__ = "blog_posts"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    translations = relationship("BlogTranslation", back_populates="blog", cascade="all, delete-orphan")

class BlogTranslation(Base):
    __tablename__ = "blog_translations"
    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blog_posts.id"))
    language = Column(String(2), nullable=False)  # fa, en, ar
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    blog = relationship("BlogPost", back_populates="translations")

Base.metadata.create_all(bind=engine)

# ---------------------------
# Pydantic Schemas
# ---------------------------
class BlogTranslationRead(BaseModel):
    language: str
    title: str
    description: Optional[str]
    content: Optional[str]
    class Config:
        orm_mode = True

class BlogRead(BaseModel):
    id: int
    image: Optional[str]
    created_at: datetime
    translations: List[BlogTranslationRead]
    class Config:
        orm_mode = True

# ---------------------------
# App Config
# ---------------------------
app = FastAPI(title="Multi-language Blog Backend")
origins = ["http://localhost:5173", "https://it-blog.vercel.app"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
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
# Endpoints
# ---------------------------
@app.post("/admin/blog", response_model=BlogRead)
def create_blog(
    image: UploadFile = File(None),
    fa_title: str = Form(...),
    fa_description: str = Form(None),
    fa_content: str = Form(None),
    en_title: str = Form(None),
    en_description: str = Form(None),
    en_content: str = Form(None),
    ar_title: str = Form(None),
    ar_description: str = Form(None),
    ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    img_path = save_upload(image) if image else None
    blog = BlogPost(image=img_path)
    db.add(blog)
    db.commit()
    db.refresh(blog)

    translations = [
        {"language": "fa", "title": fa_title, "description": fa_description, "content": fa_content},
        {"language": "en", "title": en_title, "description": en_description, "content": en_content},
        {"language": "ar", "title": ar_title, "description": ar_description, "content": ar_content},
    ]

    for t in translations:
        if t["title"]:  # فقط اگر عنوان داشت اضافه می‌کنیم
            trans = BlogTranslation(blog_id=blog.id, **t)
            db.add(trans)
    db.commit()
    db.refresh(blog)
    return blog

@app.get("/blog/{post_id}", response_model=BlogRead)
def get_blog(post_id: int, language: Optional[str] = None, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Blog post not found")

    if language in ["fa", "en", "ar"]:
        # فقط ترجمه با زبان مورد نظر را نگه می‌داریم
        post.translations = [t for t in post.translations if t.language == language]

    return post



@app.get("/blog", response_model=List[BlogRead])
def list_blog(db: Session = Depends(get_db)):
    return db.query(BlogPost).all()

# ---------------------------
# Image Upload
# ---------------------------
@app.post("/admin/upload")
def upload_image(file: UploadFile = File(...)):
    path = save_upload(file)
    return {"url": path}

# ---------------------------
# Health check
# ---------------------------
@app.get("/ping")
def ping():
    return {"pong": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
