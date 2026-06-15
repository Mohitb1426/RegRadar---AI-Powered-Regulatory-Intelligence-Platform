"""
PDF text extraction with page-level tracking
Uses PyMuPDF to extract text while preserving page numbers
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict
import os


class PDFParser:
    """Extract text from PDFs with page number tracking"""

    def __init__(self):
        self.parsed_data_dir = Path("data/parsed")
        self.parsed_data_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_with_pages(self, pdf_path: str) -> List[Dict[str, any]]:
        """
        Extract text from PDF, returning list of page dictionaries

        Returns:
            List of dicts: [{page_number: int, text: str, char_count: int}, ...]
        """
        pages_data = []

        try:
            print(f"\n[PDF] Parsing PDF: {Path(pdf_path).name}")

            # Open PDF
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count

            print(f"  --> Total pages: {total_pages}")

            for page_num in range(total_pages):
                try:
                    page = doc[page_num]
                    text = page.get_text()

                    # Clean up text
                    text = text.strip()

                    # Skip empty pages
                    if len(text) < 50:
                        continue

                    page_data = {
                        'page_number': page_num + 1,  # 1-indexed for user display
                        'text': text,
                        'char_count': len(text)
                    }

                    pages_data.append(page_data)

                except Exception as e:
                    print(f"  [ERROR] Error extracting page {page_num + 1}: {e}")
                    continue

            doc.close()

            total_chars = sum(p['char_count'] for p in pages_data)
            print(f"  [OK] Extracted {len(pages_data)} pages, {total_chars:,} characters")

            return pages_data

        except Exception as e:
            print(f"  [ERROR] PDF parsing failed: {e}")
            return []

    def parse_circular(self, pdf_path: str, circular_id: str, source: str) -> Dict:
        """
        Parse circular and return structured data

        Args:
            pdf_path: Path to PDF file
            circular_id: UUID of circular in database
            source: 'rbi' or 'sebi'

        Returns:
            Dict with keys: circular_id, source, pages, full_text
        """
        pages_data = self.extract_text_with_pages(pdf_path)

        if not pages_data:
            return None

        # Combine all text
        full_text = "\n\n".join([f"[Page {p['page_number']}]\n{p['text']}" for p in pages_data])

        result = {
            'circular_id': circular_id,
            'source': source,
            'pages': pages_data,
            'full_text': full_text,
            'total_pages': len(pages_data),
            'total_chars': sum(p['char_count'] for p in pages_data)
        }

        return result

    def get_local_pdf_path(self, s3_key: str) -> str:
        """
        Get local path for PDF based on S3 key
        Assumes PDFs are stored in data/pdfs/{source}/
        """
        return f"data/pdfs/{s3_key}"


def parse_circulars(circulars_list: list) -> list:
    """
    Parse all downloaded circulars
    Returns list of parsed data dictionaries
    """
    print("\n" + "=" * 60)
    print("Starting PDF text extraction...")
    print("=" * 60)

    parser = PDFParser()
    parsed_circulars = []

    for circular in circulars_list:
        # Get local PDF path
        if 's3_key' not in circular:
            print(f"  [SKIP] Skipping (no S3 key): {circular['title'][:60]}...")
            continue

        pdf_path = parser.get_local_pdf_path(circular['s3_key'])

        # Check if file exists locally
        if not os.path.exists(pdf_path):
            print(f"  [SKIP] PDF not found locally: {pdf_path}")
            # In production, download from S3 here
            continue

        # Parse PDF
        parsed_data = parser.parse_circular(
            pdf_path=pdf_path,
            circular_id=str(circular.get('id', '')),
            source=circular['source']
        )

        if parsed_data:
            # Add parsed data to circular
            circular['parsed_data'] = parsed_data
            parsed_circulars.append(circular)

    print("\n" + "=" * 60)
    print(f"Successfully parsed: {len(parsed_circulars)}/{len(circulars_list)}")
    print("=" * 60)

    return parsed_circulars


if __name__ == "__main__":
    # Test parser with local PDF
    import sys

    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
    else:
        # Default test PDF path
        test_pdf = "data/pdfs/test.pdf"

    if os.path.exists(test_pdf):
        parser = PDFParser()
        result = parser.extract_text_with_pages(test_pdf)

        if result:
            print(f"\n[OK] Extracted {len(result)} pages")
            print(f"\nFirst page preview:")
            print("-" * 60)
            print(result[0]['text'][:500])
            print("-" * 60)
    else:
        print(f"Test PDF not found: {test_pdf}")
        print("Usage: python parser.py <path_to_pdf>")
