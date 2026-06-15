"""
Database operations for RegRadar pipeline
Handles PostgreSQL connections and CRUD operations for circulars
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Date, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Convert asyncpg URL to psycopg2 for sync operations in pipeline
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg2")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Circular(Base):
    """Circular model for storing regulatory circular metadata"""
    __tablename__ = "circulars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    date = Column(Date, nullable=True)
    pdf_url = Column(String(500), unique=True, nullable=False)
    s3_key = Column(String(500), nullable=True)
    source = Column(String(10), nullable=False)  # 'rbi' or 'sebi'
    summary = Column(Text, nullable=True)
    indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Circular {self.source.upper()}: {self.title[:50]}>"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"


def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def circular_exists(pdf_url: str) -> bool:
    """Check if circular already exists in database"""
    db = SessionLocal()
    try:
        exists = db.query(Circular).filter(Circular.pdf_url == pdf_url).first() is not None
        return exists
    finally:
        db.close()


def add_circular(title: str, pdf_url: str, source: str, date=None, s3_key=None) -> Circular:
    """Add new circular to database"""
    db = SessionLocal()
    try:
        circular = Circular(
            title=title,
            pdf_url=pdf_url,
            source=source,
            date=date,
            s3_key=s3_key,
            indexed=False
        )
        db.add(circular)
        db.commit()
        db.refresh(circular)
        print(f"[OK] Added circular to DB: {title[:60]}...")
        return circular
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error adding circular: {e}")
        return None
    finally:
        db.close()


def update_circular_summary(circular_id: uuid.UUID, summary: str):
    """Update circular with AI-generated summary"""
    db = SessionLocal()
    try:
        circular = db.query(Circular).filter(Circular.id == circular_id).first()
        if circular:
            circular.summary = summary
            db.commit()
            print(f"[OK] Updated summary for: {circular.title[:60]}...")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error updating summary: {e}")
    finally:
        db.close()


def mark_circular_indexed(circular_id: uuid.UUID):
    """Mark circular as indexed in vector store"""
    db = SessionLocal()
    try:
        circular = db.query(Circular).filter(Circular.id == circular_id).first()
        if circular:
            circular.indexed = True
            db.commit()
            print(f"[OK] Marked as indexed: {circular.title[:60]}...")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error marking indexed: {e}")
    finally:
        db.close()


def get_unindexed_circulars():
    """Get all circulars that haven't been indexed yet"""
    db = SessionLocal()
    try:
        return db.query(Circular).filter(Circular.indexed == False).all()
    finally:
        db.close()


def get_all_circulars():
    """Get all circulars"""
    db = SessionLocal()
    try:
        return db.query(Circular).order_by(Circular.date.desc()).all()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing RegRadar database...")
    init_db()
    print("Database ready!")
