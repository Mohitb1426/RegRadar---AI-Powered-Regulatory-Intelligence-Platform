"""
Circulars routes - List and get circular details
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from ..database import get_db
from ..auth import get_current_user
from ..models.user import User
from ..models.circular import Circular
from ..schemas import CircularResponse, CircularListResponse, PaginationParams

router = APIRouter(prefix="/circulars", tags=["Circulars"])


@router.get("/", response_model=list[CircularListResponse])
async def list_circulars(
    skip: int = 0,
    limit: int = 20,
    source: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all circulars with pagination

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return (1-100)
    - **source**: Filter by source ('rbi' or 'sebi')
    """
    query = select(Circular).where(Circular.indexed == True)

    if source:
        query = query.where(Circular.source == source.lower())

    query = query.order_by(Circular.date.desc()).offset(skip).limit(min(limit, 100))

    result = await db.execute(query)
    circulars = result.scalars().all()

    return circulars


@router.get("/{circular_id}", response_model=CircularResponse)
async def get_circular(
    circular_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get single circular by ID with full details including summary
    """
    result = await db.execute(
        select(Circular).where(Circular.id == circular_id)
    )
    circular = result.scalar_one_or_none()

    if not circular:
        raise HTTPException(status_code=404, detail="Circular not found")

    return circular
