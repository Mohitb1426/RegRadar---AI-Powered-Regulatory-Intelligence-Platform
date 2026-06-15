"""
Text chunking, embedding, and vector indexing
Uses LangChain for chunking, Voyage AI for embeddings, Pinecone for storage
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
import voyageai
from pinecone import Pinecone, ServerlessSpec
import uuid

load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "regradar")


class EmbeddingService:
    """Voyage AI embedding service"""

    def __init__(self):
        if not VOYAGE_API_KEY:
            raise ValueError("VOYAGE_API_KEY not set in environment")

        self.client = voyageai.Client(api_key=VOYAGE_API_KEY)
        self.model = "voyage-2"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        Returns list of embedding vectors
        """
        try:
            result = self.client.embed(texts, model=self.model)
            return result.embeddings
        except Exception as e:
            print(f"  [ERROR] Embedding error: {e}")
            return []

    def embed_single(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else None


class VectorStore:
    """Pinecone vector database operations"""

    def __init__(self):
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set in environment")

        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Check if index exists, create if not
        existing_indexes = pc.list_indexes()
        index_names = [idx['name'] for idx in existing_indexes]

        if PINECONE_INDEX not in index_names:
            print(f"  --> Creating Pinecone index: {PINECONE_INDEX}")
            pc.create_index(
                name=PINECONE_INDEX,
                dimension=1024,  # Voyage-2 embedding dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            print(f"  [OK] Index created: {PINECONE_INDEX}")

        self.index = pc.Index(PINECONE_INDEX)

    def upsert_chunks(self, chunks_data: List[Dict]) -> int:
        """
        Upsert chunks into Pinecone

        Args:
            chunks_data: List of dicts with keys: id, embedding, metadata

        Returns:
            Number of chunks upserted
        """
        try:
            # Prepare vectors for upsert
            vectors = [
                (chunk['id'], chunk['embedding'], chunk['metadata'])
                for chunk in chunks_data
            ]

            # Upsert in batches of 100
            batch_size = 100
            upserted = 0

            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                upserted += len(batch)

            return upserted

        except Exception as e:
            print(f"  [ERROR] Pinecone upsert error: {e}")
            return 0

    def query(self, embedding: List[float], top_k: int = 5, filter: Dict = None):
        """
        Query vector store for similar chunks

        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            Query results from Pinecone
        """
        try:
            return self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
        except Exception as e:
            print(f"  [ERROR] Pinecone query error: {e}")
            return None


class CircularChunker:
    """Chunk circulars and index in vector store"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def chunk_pages(self, pages_data: List[Dict]) -> List[Dict]:
        """
        Chunk pages into smaller segments while preserving page numbers

        Args:
            pages_data: List of dicts with keys: page_number, text

        Returns:
            List of chunk dicts with: text, page_number, chunk_index
        """
        all_chunks = []

        for page in pages_data:
            page_num = page['page_number']
            text = page['text']

            # Split page into chunks
            chunks = self.text_splitter.split_text(text)

            # Add metadata to each chunk
            for i, chunk_text in enumerate(chunks):
                chunk = {
                    'text': chunk_text,
                    'page_number': page_num,
                    'chunk_index': i,
                    'char_count': len(chunk_text)
                }
                all_chunks.append(chunk)

        return all_chunks

    def embed_and_index(self, circular: Dict) -> bool:
        """
        Chunk, embed, and index a circular

        Args:
            circular: Dict with keys: id, parsed_data, title, source, date

        Returns:
            True if successful
        """
        try:
            circular_id = str(circular['id'])
            parsed_data = circular['parsed_data']
            pages = parsed_data['pages']

            print(f"\n[PROCESS] Processing: {circular['title'][:60]}...")

            # Chunk pages
            chunks = self.chunk_pages(pages)
            print(f"  --> Created {len(chunks)} chunks")

            # Prepare texts for embedding
            chunk_texts = [chunk['text'] for chunk in chunks]

            # Generate embeddings (batch)
            print(f"  --> Generating embeddings...")
            embeddings = self.embedding_service.embed_texts(chunk_texts)

            if not embeddings or len(embeddings) != len(chunks):
                print(f"  [ERROR] Embedding generation failed")
                return False

            print(f"  [OK] Generated {len(embeddings)} embeddings")

            # Prepare data for Pinecone
            chunks_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{circular_id}_{i}"

                metadata = {
                    'circular_id': circular_id,
                    'circular_title': circular['title'][:500],
                    'source': circular['source'],
                    'page_number': chunk['page_number'],
                    'chunk_index': chunk['chunk_index'],
                    'text': chunk['text'][:1000],  # Store truncated text in metadata
                }

                # Add date if available
                if circular.get('date'):
                    metadata['date'] = str(circular['date'])

                chunks_data.append({
                    'id': chunk_id,
                    'embedding': embedding,
                    'metadata': metadata
                })

            # Upsert to Pinecone
            print(f"  --> Indexing in Pinecone...")
            upserted = self.vector_store.upsert_chunks(chunks_data)

            if upserted > 0:
                print(f"  [OK] Indexed {upserted} chunks in Pinecone")
                return True
            else:
                print(f"  [ERROR] Indexing failed")
                return False

        except Exception as e:
            print(f"  [ERROR] Error processing circular: {e}")
            return False


def chunk_and_index_circulars(circulars_list: list) -> list:
    """
    Chunk and index all parsed circulars

    Returns:
        List of successfully indexed circulars
    """
    print("\n" + "=" * 60)
    print("Starting chunking and indexing...")
    print("=" * 60)

    chunker = CircularChunker()
    indexed_circulars = []

    for circular in circulars_list:
        if 'parsed_data' not in circular:
            print(f"  [SKIP] Skipping (not parsed): {circular['title'][:60]}...")
            continue

        success = chunker.embed_and_index(circular)

        if success:
            indexed_circulars.append(circular)

    print("\n" + "=" * 60)
    print(f"Successfully indexed: {len(indexed_circulars)}/{len(circulars_list)}")
    print("=" * 60)

    return indexed_circulars


if __name__ == "__main__":
    # Test embedding service
    print("Testing Voyage AI embeddings...")
    service = EmbeddingService()

    test_text = "Reserve Bank of India issues new KYC guidelines for banks."
    embedding = service.embed_single(test_text)

    if embedding:
        print(f"[OK] Embedding dimension: {len(embedding)}")
        print(f"[OK] Sample values: {embedding[:5]}")

    # Test Pinecone connection
    print("\nTesting Pinecone connection...")
    store = VectorStore()
    print(f"[OK] Connected to index: {PINECONE_INDEX}")
