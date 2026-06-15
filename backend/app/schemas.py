"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional
from uuid import UUID


# Authentication Schemas
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


# Circular Schemas
class CircularBase(BaseModel):
    """Base circular schema"""
    title: str
    source: str
    date: Optional[date] = None


class CircularResponse(CircularBase):
    """Circular response with full details"""
    id: UUID
    pdf_url: str
    summary: Optional[str] = None
    indexed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CircularListResponse(CircularBase):
    """Simplified circular for list views"""
    id: UUID
    date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Search Schemas
class SearchRequest(BaseModel):
    """Search query request"""
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Individual search result"""
    circular_id: UUID
    circular_title: str
    source: str
    page_number: int
    relevance_score: float
    text_preview: str
    date: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results response"""
    query: str
    results: list[SearchResult]
    total_results: int


# Chat Schemas
class ChatRequest(BaseModel):
    """Chat/RAG request"""
    question: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=10)


class Citation(BaseModel):
    """Source citation"""
    circular_title: str
    source: str
    page_number: int
    date: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response with answer and citations"""
    question: str
    answer: str
    citations: list[Citation]


# Pagination
class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    environment: str
    database: str
    timestamp: datetime
