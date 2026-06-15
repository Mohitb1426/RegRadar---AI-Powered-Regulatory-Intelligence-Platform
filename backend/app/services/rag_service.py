"""
RAG Service - Retrieval Augmented Generation
Integrates embeddings, vector search, and Claude for Q&A
"""

import sys
import os

# Add parent directories to path to import from pipeline
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from pipeline.chunker import EmbeddingService, VectorStore
from pipeline.summarizer import BedrockSummarizer
from typing import List, Dict


class RAGService:
    """RAG service for question answering with citations"""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.summarizer = BedrockSummarizer()

    def search_circulars(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Vector search for relevant circular chunks

        Returns list of results with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_single(query)

        if not query_embedding:
            return []

        # Search Pinecone
        results = self.vector_store.query(query_embedding, top_k=top_k)

        if not results or not results.matches:
            return []

        # Format results
        formatted_results = []
        for match in results.matches:
            metadata = match.metadata
            formatted_results.append({
                'circular_id': metadata.get('circular_id'),
                'circular_title': metadata.get('circular_title'),
                'source': metadata.get('source'),
                'page_number': metadata.get('page_number'),
                'text': metadata.get('text'),
                'date': metadata.get('date'),
                'score': match.score
            })

        return formatted_results

    def answer_question(self, question: str, top_k: int = 5) -> Dict:
        """
        Answer question using RAG pipeline

        Returns dict with answer and citations
        """
        # Search for relevant chunks
        results = self.search_circulars(question, top_k=top_k)

        if not results:
            return {
                'answer': "I couldn't find any relevant information to answer your question.",
                'citations': []
            }

        # Prepare context chunks
        context_chunks = [
            {
                'metadata': {
                    'circular_title': r['circular_title'],
                    'source': r['source'],
                    'page_number': r['page_number'],
                    'text': r['text'],
                    'date': r.get('date')
                },
                'score': r['score']
            }
            for r in results
        ]

        # Generate answer using Claude
        answer = self.summarizer.answer_question(question, context_chunks)

        if not answer:
            return {
                'answer': "I encountered an error generating the answer. Please try again.",
                'citations': []
            }

        # Format citations
        citations = [
            {
                'circular_title': r['circular_title'],
                'source': r['source'],
                'page_number': r['page_number'],
                'date': r.get('date')
            }
            for r in results
        ]

        return {
            'answer': answer,
            'citations': citations
        }
