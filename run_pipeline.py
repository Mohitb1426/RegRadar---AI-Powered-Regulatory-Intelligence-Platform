"""
RegRadar Master Pipeline Orchestrator
Runs complete data ingestion pipeline: scrape → download → parse → chunk → summarize → index
"""

import sys
from datetime import datetime
from pipeline.scraper import scrape_all_circulars
from pipeline.downloader import download_circulars
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
    print(" " * 20 + "RegRadar Data Pipeline")
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


def run_full_pipeline(limit: int = 50):
    """
    Run complete data pipeline

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
        print("\n📦 STEP 0: Database Initialization")
        print("-" * 80)
        init_db()

        # Step 1: Scrape websites
        print("\n📡 STEP 1: Web Scraping")
        print("-" * 80)
        circulars = scrape_all_circulars(limit=limit)
        stats['discovered'] = len(circulars)

        if not circulars:
            print("\n⚠️  No new circulars found. Exiting.")
            print_summary(stats)
            return

        # Step 2: Download PDFs and upload to S3
        print("\n📥 STEP 2: PDF Download & S3 Upload")
        print("-" * 80)
        downloaded = download_circulars(circulars)
        stats['downloaded'] = len(downloaded)

        if not downloaded:
            print("\n⚠️  No PDFs downloaded. Exiting.")
            print_summary(stats)
            return

        # Step 3: Add circulars to database
        print("\n💾 STEP 3: Database Storage")
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
        print("\n📄 STEP 4: PDF Text Extraction")
        print("-" * 80)
        parsed = parse_circulars(downloaded)
        stats['parsed'] = len(parsed)

        if not parsed:
            print("\n⚠️  No PDFs parsed. Exiting.")
            print_summary(stats)
            return

        # Step 5: Generate summaries
        print("\n🤖 STEP 5: AI Summarization")
        print("-" * 80)
        summarized = summarize_circulars(parsed)
        stats['summarized'] = len(summarized)

        # Update database with summaries
        for circular in summarized:
            if 'summary' in circular and 'id' in circular:
                update_circular_summary(circular['id'], circular['summary'])

        # Step 6: Chunk, embed, and index
        print("\n🔄 STEP 6: Chunking & Vector Indexing")
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
            print("✅ Pipeline completed successfully!")
            print("\nNext steps:")
            print("1. Test queries: python pipeline/test_query.py")
            print("2. Interactive mode: python pipeline/test_query.py")
            print()
        else:
            print("⚠️  Pipeline completed but no circulars were indexed.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print_summary(stats)
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        print_summary(stats)


def run_test_pipeline():
    """Run pipeline in test mode with limited circulars"""
    print("\n🧪 Running in TEST MODE (5 circulars per source)")
    run_full_pipeline(limit=5)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'test':
            run_test_pipeline()
        elif command == 'full':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            run_full_pipeline(limit=limit)
        else:
            print("Usage:")
            print("  python run_pipeline.py          - Run full pipeline (50 circulars)")
            print("  python run_pipeline.py test     - Run test pipeline (5 circulars)")
            print("  python run_pipeline.py full <N> - Run pipeline with N circulars per source")
    else:
        # Default: run full pipeline
        run_full_pipeline()
