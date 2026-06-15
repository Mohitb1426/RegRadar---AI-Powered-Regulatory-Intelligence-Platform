"""
CLI tool for testing vector search and RAG pipeline
Query circulars and get AI-generated answers with citations
"""

import sys
from chunker import EmbeddingService, VectorStore
from summarizer import BedrockSummarizer


def search_circulars(query: str, top_k: int = 5):
    """
    Search for relevant circular chunks based on query

    Args:
        query: Natural language search query
        top_k: Number of results to return

    Returns:
        List of matching chunks with metadata
    """
    print(f"\n[SEARCH] Query: \"{query}\"")
    print("=" * 80)

    try:
        # Initialize services
        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        # Embed query
        print("  --> Generating query embedding...")
        query_embedding = embedding_service.embed_single(query)

        if not query_embedding:
            print("  [ERROR] Failed to generate embedding")
            return []

        # Search Pinecone
        print(f"  --> Searching vector database (top {top_k})...")
        results = vector_store.query(query_embedding, top_k=top_k)

        if not results or not results.matches:
            print("  [ERROR] No results found")
            return []

        print(f"  [OK] Found {len(results.matches)} relevant chunks\n")

        # Display results
        chunks = []
        for i, match in enumerate(results.matches, 1):
            metadata = match.metadata
            score = match.score

            print(f"Result {i} (Relevance: {score:.3f})")
            print("-" * 80)
            print(f"Circular: {metadata.get('circular_title', 'N/A')}")
            print(f"Source: {metadata.get('source', 'N/A').upper()}")
            print(f"Page: {metadata.get('page_number', 'N/A')}")
            if metadata.get('date'):
                print(f"Date: {metadata.get('date')}")
            print(f"\nText Preview:")
            print(metadata.get('text', 'N/A')[:300] + "...")
            print("=" * 80)
            print()

            chunks.append({
                'metadata': metadata,
                'score': score
            })

        return chunks

    except Exception as e:
        print(f"  [ERROR] Search error: {e}")
        return []


def answer_question(question: str, top_k: int = 5):
    """
    Answer question using RAG pipeline

    Args:
        question: User's question
        top_k: Number of context chunks to retrieve
    """
    print(f"\n[CHAT] Question: \"{question}\"")
    print("=" * 80)

    try:
        # Initialize services
        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        summarizer = BedrockSummarizer()

        # Search for relevant chunks
        print("  --> Searching for relevant circulars...")
        query_embedding = embedding_service.embed_single(question)

        if not query_embedding:
            print("  [ERROR] Failed to generate embedding")
            return

        results = vector_store.query(query_embedding, top_k=top_k)

        if not results or not results.matches:
            print("  [ERROR] No relevant circulars found")
            return

        print(f"  [OK] Found {len(results.matches)} relevant chunks")

        # Prepare context
        context_chunks = [
            {
                'metadata': match.metadata,
                'score': match.score
            }
            for match in results.matches
        ]

        # Generate answer using Claude
        print("  --> Generating answer with Claude Sonnet 4...")
        answer = summarizer.answer_question(question, context_chunks)

        if not answer:
            print("  [ERROR] Failed to generate answer")
            return

        # Display answer
        print("\n" + "=" * 80)
        print("[ANSWER] ANSWER:")
        print("=" * 80)
        print(answer)
        print("\n" + "=" * 80)

        # Display citations
        print("\n[SOURCES] SOURCES:")
        print("=" * 80)
        for i, chunk in enumerate(context_chunks, 1):
            meta = chunk['metadata']
            print(f"{i}. {meta.get('circular_title', 'N/A')[:80]}")
            print(f"   Source: {meta.get('source', 'N/A').upper()} | Page: {meta.get('page_number', 'N/A')}")
            if meta.get('date'):
                print(f"   Date: {meta.get('date')}")
            print()

    except Exception as e:
        print(f"  [ERROR] Error: {e}")


def interactive_mode():
    """Interactive CLI for testing queries"""
    print("\n" + "=" * 80)
    print("RegRadar - Interactive Query Tool")
    print("=" * 80)
    print("\nCommands:")
    print("  /search <query>  - Search for relevant circulars")
    print("  /ask <question>  - Get AI answer with citations")
    print("  /quit           - Exit")
    print("=" * 80)

    while True:
        try:
            user_input = input("\n> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("\nGoodbye!")
                break

            if user_input.startswith('/search '):
                query = user_input[8:].strip()
                if query:
                    search_circulars(query)

            elif user_input.startswith('/ask '):
                question = user_input[5:].strip()
                if question:
                    answer_question(question)

            else:
                # Default to asking question
                answer_question(user_input)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()

        if command == 'search' and len(sys.argv) > 2:
            query = ' '.join(sys.argv[2:])
            search_circulars(query)

        elif command == 'ask' and len(sys.argv) > 2:
            question = ' '.join(sys.argv[2:])
            answer_question(question)

        else:
            print("Usage:")
            print("  python test_query.py search <query>")
            print("  python test_query.py ask <question>")
            print("  python test_query.py                  (interactive mode)")

    else:
        # Interactive mode
        interactive_mode()
