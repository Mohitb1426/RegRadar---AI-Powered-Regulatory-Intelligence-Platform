"""
Search routes - Vector search for circulars
"""

from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..models.user import User
from ..schemas import SearchRequest, SearchResponse, SearchResult
from ..services.rag_service import RAGService
from uuid import UUID

router = APIRouter(prefix="/search", tags=["Search"])
rag_service = RAGService()


@router.post("/", response_model=SearchResponse)
async def search_circulars(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search for relevant circulars using semantic search

    - **query**: Search query in natural language
    - **top_k**: Number of results to return (1-20)

    Returns relevant circular chunks ranked by relevance
    """
    try:
        # Perform vector search
        results = rag_service.search_circulars(request.query, request.top_k)

        # Format response
        search_results = [
            SearchResult(
                circular_id=UUID(r['circular_id']) if r.get('circular_id') else UUID('00000000-0000-0000-0000-000000000000'),
                circular_title=r['circular_title'],
                source=r['source'],
                page_number=r['page_number'],
                relevance_score=r['score'],
                text_preview=r['text'][:300],
                date=r.get('date')
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
