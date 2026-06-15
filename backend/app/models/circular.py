"""Circular model"""

from sqlalchemy import Column, String, DateTime, Boolean, Date, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..database import Base


class Circular(Base):
    """Circular table for regulatory documents"""
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
