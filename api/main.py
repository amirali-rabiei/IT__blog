from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import os, shutil, uuid

# ---------------------------
# Paths and DB
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

# Products
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")

class ProductTranslation(Base):
    __tablename__ = "product_translations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    language = Column(String(2), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    product = relationship("Product", back_populates="translations")

# Blog
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
    language = Column(String(2), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    blog = relationship("BlogPost", back_populates="translations")

# Activity
class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    translations = relationship("ActivityTranslation", back_populates="activity", cascade="all, delete-orphan")

class ActivityTranslation(Base):
    __tablename__ = "activity_translations"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    language = Column(String(2), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    activity = relationship("Activity", back_populates="translations")

# About
class About(Base):
    __tablename__ = "about"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)

# Parent Companies
class ParentCompany(Base):
    __tablename__ = "parent_companies"
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(512), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---------------------------
# Schemas
# ---------------------------
class TranslationRead(BaseModel):
    language: str
    title: str
    description: Optional[str]
    content: Optional[str]
    class Config:
        orm_mode = True

class ProductRead(BaseModel):
    id: int
    image: Optional[str]
    created_at: datetime
    translations: List[TranslationRead]
    class Config:
        orm_mode = True

class BlogRead(ProductRead):
    pass

class ActivityRead(ProductRead):
    pass

class AboutRead(BaseModel):
    id: int
    content: Optional[str]
    class Config:
        orm_mode = True

class ParentCompanyRead(BaseModel):
    id: int
    image: Optional[str]
    title: str
    description: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

# ---------------------------
# App Config
# ---------------------------
app = FastAPI(title="Company Backend with Parent Companies")
origins = ["*"]
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
    path = os.path.join(UPLOAD_DIR, new_name)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/uploads/{new_name}"

def update_translations(db: Session, item, translations_data: dict, model_translation):
    for lang in ["fa", "en", "ar"]:
        t_data = translations_data.get(lang)
        if t_data and t_data.get("title"):
            trans = db.query(model_translation).filter_by(**{
                f"{model_translation.__tablename__.split('_')[0]}_id": item.id,
                "language": lang
            }).first()
            if trans:
                trans.title = t_data.get("title")
                trans.description = t_data.get("description")
                trans.content = t_data.get("content")
            else:
                db.add(model_translation(
                    **{f"{model_translation.__tablename__.split('_')[0]}_id": item.id,
                       "language": lang,
                       "title": t_data.get("title"),
                       "description": t_data.get("description"),
                       "content": t_data.get("content")}
                ))
    db.commit()
    db.refresh(item)

# ---------------------------
# CRUD Endpoints
# ---------------------------

# Products CRUD
@app.post("/admin/products", response_model=ProductRead)
def create_product(
    image: UploadFile = File(None),
    fa_title: str = Form(...), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    product = Product(image=save_upload(image) if image else None)
    db.add(product)
    db.commit()
    db.refresh(product)
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, product, translations, ProductTranslation)
    return product

@app.put("/admin/products/{product_id}", response_model=ProductRead)
def update_product_endpoint(
    product_id: int,
    image: UploadFile = File(None),
    fa_title: str = Form(None), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    if image:
        product.image = save_upload(image)
        db.commit()
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, product, translations, ProductTranslation)
    return product

@app.delete("/admin/products/{product_id}")
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    db.delete(product)
    db.commit()
    return {"ok": True}

@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, language: Optional[str] = None, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if language in ["fa", "en", "ar"]:
        product.translations = [t for t in product.translations if t.language == language]
    return product

@app.get("/products", response_model=List[ProductRead])
def list_products(language: Optional[str] = None, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if language in ["fa","en","ar"]:
        for p in products:
            p.translations = [t for t in p.translations if t.language == language]
    return products

# Blog CRUD
@app.post("/admin/blog", response_model=BlogRead)
def create_blog(
    image: UploadFile = File(None),
    fa_title: str = Form(...), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    blog = BlogPost(image=save_upload(image) if image else None)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, blog, translations, BlogTranslation)
    return blog

@app.put("/admin/blog/{post_id}", response_model=BlogRead)
def update_blog_endpoint(
    post_id: int,
    image: UploadFile = File(None),
    fa_title: str = Form(None), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    blog = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not blog:
        raise HTTPException(404, "Blog post not found")
    if image:
        blog.image = save_upload(image)
        db.commit()
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, blog, translations, BlogTranslation)
    return blog

@app.delete("/admin/blog/{post_id}")
def delete_blog_endpoint(post_id: int, db: Session = Depends(get_db)):
    blog = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not blog:
        raise HTTPException(404, "Blog post not found")
    db.delete(blog)
    db.commit()
    return {"ok": True}

@app.get("/blog/{post_id}", response_model=BlogRead)
def get_blog(post_id: int, language: Optional[str] = None, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if language in ["fa", "en", "ar"]:
        post.translations = [t for t in post.translations if t.language == language]
    return post

@app.get("/blog", response_model=List[BlogRead])
def list_blog(language: Optional[str] = None, db: Session = Depends(get_db)):
    blogs = db.query(BlogPost).all()
    if language in ["fa","en","ar"]:
        for b in blogs:
            b.translations = [t for t in b.translations if t.language == language]
    return blogs

# Activity CRUD
@app.post("/admin/activity", response_model=ActivityRead)
def create_activity(
    image: UploadFile = File(None),
    fa_title: str = Form(...), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    act = Activity(image=save_upload(image) if image else None)
    db.add(act)
    db.commit()
    db.refresh(act)
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, act, translations, ActivityTranslation)
    return act

@app.put("/admin/activity/{activity_id}", response_model=ActivityRead)
def update_activity_endpoint(
    activity_id: int,
    image: UploadFile = File(None),
    fa_title: str = Form(None), fa_description: str = Form(None), fa_content: str = Form(None),
    en_title: str = Form(None), en_description: str = Form(None), en_content: str = Form(None),
    ar_title: str = Form(None), ar_description: str = Form(None), ar_content: str = Form(None),
    db: Session = Depends(get_db)
):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    if image:
        act.image = save_upload(image)
        db.commit()
    translations = {
        "fa": {"title": fa_title, "description": fa_description, "content": fa_content},
        "en": {"title": en_title, "description": en_description, "content": en_content},
        "ar": {"title": ar_title, "description": ar_description, "content": ar_content},
    }
    update_translations(db, act, translations, ActivityTranslation)
    return act

@app.delete("/admin/activity/{activity_id}")
def delete_activity_endpoint(activity_id: int, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    db.delete(act)
    db.commit()
    return {"ok": True}

@app.get("/activities/{activity_id}", response_model=ActivityRead)
def get_activity(activity_id: int, language: Optional[str] = None, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
    if language in ["fa", "en", "ar"]:
        act.translations = [t for t in act.translations if t.language == language]
    return act

@app.get("/activities", response_model=List[ActivityRead])
def list_activities(language: Optional[str] = None, db: Session = Depends(get_db)):
    acts = db.query(Activity).all()
    if language in ["fa","en","ar"]:
        for a in acts:
            a.translations = [t for t in a.translations if t.language == language]
    return acts

# Parent Companies CRUD
@app.post("/admin/parent-companies", response_model=ParentCompanyRead)
def create_parent_company(
    image: UploadFile = File(None),
    title: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    company = ParentCompany(
        image=save_upload(image) if image else None,
        title=title,
        description=description
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@app.put("/admin/parent-companies/{company_id}", response_model=ParentCompanyRead)
def update_parent_company(
    company_id: int,
    image: UploadFile = File(None),
    title: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    company = db.query(ParentCompany).filter(ParentCompany.id == company_id).first()
    if not company:
        raise HTTPException(404, "Parent company not found")
    if image:
        company.image = save_upload(image)
    if title:
        company.title = title
    if description:
        company.description = description
    db.commit()
    db.refresh(company)
    return company

@app.delete("/admin/parent-companies/{company_id}")
def delete_parent_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(ParentCompany).filter(ParentCompany.id == company_id).first()
    if not company:
        raise HTTPException(404, "Parent company not found")
    db.delete(company)
    db.commit()
    return {"ok": True}

@app.get("/parent-companies", response_model=List[ParentCompanyRead])
def list_parent_companies(db: Session = Depends(get_db)):
    return db.query(ParentCompany).all()

@app.get("/parent-companies/{company_id}", response_model=ParentCompanyRead)
def get_parent_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(ParentCompany).filter(ParentCompany.id == company_id).first()
    if not company:
        raise HTTPException(404, "Parent company not found")
    return company


# About
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

# Upload Image
@app.post("/admin/upload")
def upload_image(file: UploadFile = File(...)):
    return {"url": save_upload(file)}

# Health Check
@app.get("/ping")
def ping():
    return {"pong": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
