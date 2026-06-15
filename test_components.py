"""
Test individual components without Unicode issues
"""

import sys
import os

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def test_voyage_ai():
    """Test Voyage AI embeddings"""
    print("\n[TEST] Voyage AI Embeddings")
    print("-" * 60)
    try:
        from pipeline.chunker import EmbeddingService
        service = EmbeddingService()
        embedding = service.embed_single("Test embedding for RegRadar")
        print(f"SUCCESS: Embedding dimension = {len(embedding)}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_pinecone():
    """Test Pinecone connection"""
    print("\n[TEST] Pinecone Vector Database")
    print("-" * 60)
    try:
        from pipeline.chunker import VectorStore
        store = VectorStore()
        stats = store.index.describe_index_stats()
        print(f"SUCCESS: Connected to Pinecone")
        print(f"Total vectors in index: {stats.total_vector_count}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_bedrock():
    """Test AWS Bedrock Claude"""
    print("\n[TEST] AWS Bedrock (Claude Sonnet 4)")
    print("-" * 60)
    try:
        from pipeline.summarizer import BedrockSummarizer
        summarizer = BedrockSummarizer()
        response = summarizer.generate("Respond with: Test successful", max_tokens=20)
        if response:
            print(f"SUCCESS: Claude responded")
            print(f"Response: {response[:100]}")
            return True
        else:
            print("FAILED: No response from Claude")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_database():
    """Test PostgreSQL connection"""
    print("\n[TEST] PostgreSQL Database")
    print("-" * 60)
    try:
        from pipeline.db import init_db
        init_db()
        print("SUCCESS: Database initialized")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    print("=" * 60)
    print("RegRadar Component Testing")
    print("=" * 60)

    results = {}

    # Test each component
    results['Voyage AI'] = test_voyage_ai()
    results['Pinecone'] = test_pinecone()
    results['AWS Bedrock'] = test_bedrock()
    results['Database'] = test_database()

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    total = len(results)
    passed = sum(results.values())

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\nAll components working! Ready to run pipeline.")
    else:
        print("\nSome components failed. Check errors above.")

if __name__ == "__main__":
    main()
