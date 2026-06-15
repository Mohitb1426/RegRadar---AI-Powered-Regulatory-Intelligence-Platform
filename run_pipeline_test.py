"""
RegRadar Test Pipeline (Without S3)
Runs complete pipeline with local PDF storage
"""

import sys
from datetime import datetime

# Import pipeline components
from pipeline.scraper import scrape_all_circulars
from pipeline.downloader_local import download_circulars  # Use local downloader
from pipeline.parser import parse_circulars
from pipeline.chunker import chunk_and_index_circulars
from pipeline.summarizer import summarize_circulars
from pipeline.db import (
    init_db,
    add_circular,
    update_circular_summary,
    mark_circular_indexed
)


def print_banner():
    """Print pipeline banner"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "RegRadar Test Pipeline (Local Storage)")
    print(" " * 15 + "AI-Powered Regulatory Intelligence")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def print_summary(stats: dict):
    """Print pipeline execution summary"""
    print("\n")
    print("=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Circulars discovered:  {stats['discovered']}")
    print(f"PDFs downloaded:       {stats['downloaded']}")
    print(f"PDFs parsed:           {stats['parsed']}")
    print(f"Circulars summarized:  {stats['summarized']}")
    print(f"Circulars indexed:     {stats['indexed']}")
    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def run_test_pipeline(limit: int = 3):
    """
    Run test pipeline with limited circulars

    Args:
        limit: Maximum number of circulars to process per source (default: 3)
    """
    print_banner()

    stats = {
        'discovered': 0,
        'downloaded': 0,
        'parsed': 0,
        'summarized': 0,
        'indexed': 0
    }

    try:
        # Step 0: Initialize database
        print("\n[STEP 0] Database Initialization")
        print("-" * 80)
        init_db()
        print("Database ready!")

        # Step 1: Scrape websites
        print("\n[STEP 1] Web Scraping (RBI + SEBI)")
        print("-" * 80)
        print(f"Looking for up to {limit} circulars per source...")
        circulars = scrape_all_circulars(limit=limit)
        stats['discovered'] = len(circulars)

        if not circulars:
            print("\nNo new circulars found. This is normal if:")
            print("  - Websites are temporarily unreachable")
            print("  - All recent circulars are already in database")
            print("  - Website structure has changed")
            print("\nExiting test pipeline.")
            print_summary(stats)
            return

        # Step 2: Download PDFs (local storage)
        print("\n[STEP 2] PDF Download (Local Storage)")
        print("-" * 80)
        downloaded = download_circulars(circulars)
        stats['downloaded'] = len(downloaded)

        if not downloaded:
            print("\nNo PDFs downloaded successfully.")
            print_summary(stats)
            return

        # Step 3: Add circulars to database
        print("\n[STEP 3] Save to Database")
        print("-" * 80)
        for circular in downloaded:
            db_circular = add_circular(
                title=circular['title'],
                pdf_url=circular['pdf_url'],
                source=circular['source'],
                date=circular.get('date'),
                s3_key=circular.get('s3_key')  # Actually local path
            )
            if db_circular:
                circular['id'] = db_circular.id

        # Step 4: Parse PDFs
        print("\n[STEP 4] PDF Text Extraction")
        print("-" * 80)
        parsed = parse_circulars(downloaded)
        stats['parsed'] = len(parsed)

        if not parsed:
            print("\nNo PDFs parsed successfully.")
            print_summary(stats)
            return

        # Step 5: Generate AI summaries
        print("\n[STEP 5] AI Summarization (Claude Sonnet 4.5)")
        print("-" * 80)
        summarized = summarize_circulars(parsed)
        stats['summarized'] = len(summarized)

        # Update database with summaries
        for circular in summarized:
            if 'summary' in circular and 'id' in circular:
                update_circular_summary(circular['id'], circular['summary'])

        # Step 6: Chunk, embed, and index
        print("\n[STEP 6] Chunking & Vector Indexing")
        print("-" * 80)
        print("Creating text chunks...")
        print("Generating embeddings with Voyage AI...")
        print("Indexing vectors in Pinecone...")
        indexed = chunk_and_index_circulars(summarized)
        stats['indexed'] = len(indexed)

        # Mark as indexed in database
        for circular in indexed:
            if 'id' in circular:
                mark_circular_indexed(circular['id'])

        # Print summary
        print_summary(stats)

        if stats['indexed'] > 0:
            print("SUCCESS! Pipeline completed successfully!")
            print("\nNext steps:")
            print("1. Test queries:")
            print("   python pipeline/test_query.py ask 'What are the new regulations?'")
            print()
            print("2. Interactive mode:")
            print("   python pipeline/test_query.py")
            print()
        else:
            print("WARNING: Pipeline completed but no circulars were indexed.")

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        print_summary(stats)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        print_summary(stats)


if __name__ == "__main__":
    # Run with 3 circulars for quick testing
    print("\nRunning TEST PIPELINE with 3 circulars per source")
    print("This will take approximately 5-10 minutes")
    print("Estimated cost: ~$0.05 - $0.10")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        run_test_pipeline(limit=3)
    else:
        print("Test cancelled.")
