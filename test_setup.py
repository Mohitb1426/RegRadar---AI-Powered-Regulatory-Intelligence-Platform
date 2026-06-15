"""
RegRadar Setup Testing Script
Tests each component before running the full pipeline
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(title):
    """Print test section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_env_variables():
    """Test if all required environment variables are set"""
    print_header("Step 1: Environment Variables")

    required_vars = {
        'AWS_ACCESS_KEY_ID': 'AWS Bedrock access',
        'AWS_SECRET_ACCESS_KEY': 'AWS Bedrock secret',
        'VOYAGE_API_KEY': 'Voyage AI embeddings',
        'PINECONE_API_KEY': 'Pinecone vector database',
        'DATABASE_URL': 'PostgreSQL database'
    }

    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value not in ['your_access_key_here', 'your_secret_key_here',
                                     'pa-your_voyage_key_here', 'your_pinecone_key_here',
                                     'postgresql+asyncpg://user:password@host:5432/regradar']:
            print(f"  OK {var}: {description}")
        else:
            print(f"  MISSING {var}: {description}")
            all_set = False

    return all_set

def test_database():
    """Test database connection and initialization"""
    print_header("Step 2: Database Connection")

    try:
        from pipeline import db
        print("  OK Database module imported")

        # Try to initialize database
        db.init_db()
        print("  OK Database tables created/verified")
        return True
    except Exception as e:
        print(f"  ERROR Database test failed: {e}")
        return False

def test_aws_bedrock():
    """Test AWS Bedrock connection"""
    print_header("Step 3: AWS Bedrock (Claude Sonnet 4)")

    try:
        from pipeline.summarizer import BedrockSummarizer
        print("  OK Summarizer module imported")

        summarizer = BedrockSummarizer()
        print("  OK AWS Bedrock client created")

        # Test with simple prompt
        response = summarizer.generate("Say 'Hello from Claude Sonnet 4!'", max_tokens=50)
        if response:
            print(f"  OK Claude response: {response[:60]}...")
            return True
        else:
            print("  ERROR No response from Claude")
            return False
    except Exception as e:
        print(f"  ERROR AWS Bedrock test failed: {e}")
        return False

def test_voyage_ai():
    """Test Voyage AI embeddings"""
    print_header("Step 4: Voyage AI Embeddings")

    try:
        from pipeline.chunker import EmbeddingService
        print("  OK Embedding service imported")

        service = EmbeddingService()
        print("  OK Voyage AI client created")

        # Test embedding
        embedding = service.embed_single("Test embedding generation")
        if embedding and len(embedding) == 1024:
            print(f"  OK Embedding generated (dimension: {len(embedding)})")
            return True
        else:
            print("  ERROR Invalid embedding dimension")
            return False
    except Exception as e:
        print(f"  ERROR Voyage AI test failed: {e}")
        return False

def test_pinecone():
    """Test Pinecone connection"""
    print_header("Step 5: Pinecone Vector Database")

    try:
        from pipeline.chunker import VectorStore
        print("  OK Vector store module imported")

        store = VectorStore()
        print("  OK Pinecone index connected")

        # Get index stats
        stats = store.index.describe_index_stats()
        print(f"  OK Index stats: {stats.total_vector_count} vectors")
        return True
    except Exception as e:
        print(f"  ERROR Pinecone test failed: {e}")
        return False

def test_aws_s3():
    """Test AWS S3 bucket access"""
    print_header("Step 6: AWS S3 Storage")

    try:
        from pipeline.downloader import S3Downloader
        print("  OK Downloader module imported")

        downloader = S3Downloader()
        print("  OK S3 client created")

        # Check if bucket exists
        bucket_name = os.getenv('AWS_BUCKET_NAME')
        try:
            downloader.s3_client.head_bucket(Bucket=bucket_name)
            print(f"  OK Bucket '{bucket_name}' exists and accessible")
            return True
        except:
            print(f"  WARNING Bucket '{bucket_name}' not found - will be created on first run")
            return True
    except Exception as e:
        print(f"  ERROR S3 test failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing modules"""
    print_header("Step 7: PDF Processing")

    try:
        from pipeline.parser import PDFParser
        print("  OK PDF parser module imported")

        import fitz  # PyMuPDF
        print(f"  OK PyMuPDF version: {fitz.version}")
        return True
    except Exception as e:
        print(f"  ERROR PDF processing test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "=" * 70)
    print("  RegRadar Phase 1 - Setup Testing")
    print("=" * 70)

    results = {
        'Environment Variables': test_env_variables(),
        'Database': test_database(),
        'AWS Bedrock (Claude)': test_aws_bedrock(),
        'Voyage AI (Embeddings)': test_voyage_ai(),
        'Pinecone (Vector DB)': test_pinecone(),
        'AWS S3 (Storage)': test_aws_s3(),
        'PDF Processing': test_pdf_processing()
    }

    # Print summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        icon = "OK" if passed else "XX"
        print(f"  [{icon}] {test_name}: {status}")

    total = len(results)
    passed = sum(results.values())

    print("=" * 70)
    print(f"  Total: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n  SUCCESS! All components are ready.")
        print("  Next step: Run test pipeline with 'python run_pipeline.py test'")
    else:
        print("\n  WARNING: Some tests failed. Check configuration above.")
        print("  Fix issues before running the pipeline.")

    print()

if __name__ == "__main__":
    run_all_tests()
