"""
RegRadar Production Pipeline
Uses improved scraper and robust downloader with validation
"""

import sys
from datetime import datetime

# Import production-ready components
from pipeline.scraper_improved import scrape_all_circulars
from pipeline.downloader_robust import download_circulars
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
    print(" " * 20 + "RegRadar Production Pipeline")
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
    print("-" * 80)
    print(f"Success rate:          {stats['indexed']}/{stats['discovered']} ({100*stats['indexed']/max(stats['discovered'],1):.1f}%)")
    print("=" * 80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


def run_production_pipeline(limit: int = 10):
    """
    Run production pipeline with improved components

    Args:
        limit: Maximum number of circulars to process per source
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

        # Step 1: Scrape websites (improved scraper)
        print("\n[STEP 1] Web Scraping (Improved)")
        print("-" * 80)
        print(f"Looking for up to {limit} circulars per source...")
        circulars = scrape_all_circulars(limit=limit)
        stats['discovered'] = len(circulars)

        if not circulars:
            print("\n[INFO] No new circulars found.")
            print("This could mean:")
            print("  - All recent circulars are already in database")
            print("  - Websites are temporarily unreachable")
            print("  - Website structure has changed")
            print_summary(stats)
            return

        # Step 2: Download PDFs with validation and retries
        print("\n[STEP 2] PDF Download with Validation")
        print("-" * 80)
        downloaded = download_circulars(circulars, max_retries=3)
        stats['downloaded'] = len(downloaded)

        if not downloaded:
            print("\n[WARNING] No PDFs downloaded successfully.")
            print("This is usually due to:")
            print("  - Bot detection on regulatory websites")
            print("  - Network issues")
            print("  - Invalid PDF URLs")
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
                s3_key=circular.get('s3_key')
            )
            if db_circular:
                circular['id'] = db_circular.id

        # Step 4: Parse PDFs
        print("\n[STEP 4] PDF Text Extraction")
        print("-" * 80)
        parsed = parse_circulars(downloaded)
        stats['parsed'] = len(parsed)

        if not parsed:
            print("\n[WARNING] No PDFs parsed successfully.")
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
        print("\n[STEP 6] Vector Indexing (Voyage AI + Pinecone)")
        print("-" * 80)
        indexed = chunk_and_index_circulars(summarized)
        stats['indexed'] = len(indexed)

        # Mark as indexed in database
        for circular in indexed:
            if 'id' in circular:
                mark_circular_indexed(circular['id'])

        # Print summary
        print_summary(stats)

        if stats['indexed'] > 0:
            print("[SUCCESS] Pipeline completed successfully!")
            print("\nCirculars are now searchable:")
            print("  python pipeline/test_query.py ask 'What are the new regulations?'")
            print()
        else:
            print("[WARNING] Pipeline completed but no circulars were indexed.")

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user")
        print_summary(stats)
    except Exception as e:
        print(f"\n\n[ERROR] Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        print_summary(stats)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    else:
        limit = 10  # Default: 10 circulars per source

    print(f"\n[INFO] Running PRODUCTION PIPELINE")
    print(f"[INFO] Processing up to {limit} circulars per source")
    print(f"[INFO] Features:")
    print(f"  - Improved web scraping with multiple strategies")
    print(f"  - PDF validation (rejects HTML error pages)")
    print(f"  - Automatic retries (up to 3 attempts)")
    print(f"  - Production-ready headers to bypass bot detection")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        run_production_pipeline(limit=limit)
    else:
        print("Pipeline cancelled.")
