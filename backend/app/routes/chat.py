"""
Chat routes - RAG with streaming support
"""

from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..models.user import User
from ..schemas import ChatRequest, ChatResponse, Citation
from ..services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])
rag_service = RAGService()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Ask a question and get AI-generated answer with citations

    - **question**: Your question in natural language
    - **top_k**: Number of source chunks to retrieve (1-10)

    Returns AI answer with source citations including page numbers
    """
    # Get answer from RAG service
    result = rag_service.answer_question(request.question, request.top_k)

    # Format citations
    citations = [
        Citation(
            circular_title=c['circular_title'],
            source=c['source'],
            page_number=c['page_number'],
            date=c.get('date')
        )
        for c in result['citations']
    ]

    return ChatResponse(
        question=request.question,
        answer=result['answer'],
        citations=citations
    )
