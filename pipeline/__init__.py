"""
RegRadar Data Pipeline Package
Automated regulatory circular ingestion and processing
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .db import (
    init_db,
    circular_exists,
    add_circular,
    update_circular_summary,
    mark_circular_indexed,
    get_unindexed_circulars,
    get_all_circulars
)

from .scraper import scrape_all_circulars, RBIScraper, SEBIScraper
from .downloader import download_circulars, S3Downloader
from .parser import parse_circulars, PDFParser
from .chunker import chunk_and_index_circulars, CircularChunker, EmbeddingService, VectorStore
from .summarizer import summarize_circulars, BedrockSummarizer

__all__ = [
    # Database
    'init_db',
    'circular_exists',
    'add_circular',
    'update_circular_summary',
    'mark_circular_indexed',
    'get_unindexed_circulars',
    'get_all_circulars',
    # Scraping
    'scrape_all_circulars',
    'RBIScraper',
    'SEBIScraper',
    # Downloading
    'download_circulars',
    'S3Downloader',
    # Parsing
    'parse_circulars',
    'PDFParser',
    # Chunking & Indexing
    'chunk_and_index_circulars',
    'CircularChunker',
    'EmbeddingService',
    'VectorStore',
    # Summarization
    'summarize_circulars',
    'BedrockSummarizer',
]
