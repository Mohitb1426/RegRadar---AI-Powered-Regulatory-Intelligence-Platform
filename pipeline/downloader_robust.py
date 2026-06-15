"""
Production-ready PDF downloader with validation
Handles bot detection, malformed PDFs, and retries
"""

import os
import requests
from pathlib import Path
import hashlib
import time
import fitz  # PyMuPDF for PDF validation


class RobustDownloader:
    """Production-ready PDF downloader with validation"""

    def __init__(self):
        self.local_data_dir = Path("data/pdfs")
        self.local_data_dir.mkdir(parents=True, exist_ok=True)

        # Production-ready headers to bypass bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/x-pdf,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.rbi.org.in/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1'
        }

    def generate_local_key(self, source: str, pdf_url: str) -> str:
        """Generate unique local path for PDF"""
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:12]
        return f"{source}/{url_hash}.pdf"

    def is_valid_pdf(self, file_path: str) -> bool:
        """
        Validate if file is actually a PDF (not HTML error page)
        Returns True if valid PDF
        """
        try:
            # Check file size (PDFs are usually > 1KB)
            if os.path.getsize(file_path) < 1024:
                return False

            # Try to open with PyMuPDF
            doc = fitz.open(file_path)
            page_count = doc.page_count
            doc.close()

            # Valid PDF should have at least 1 page
            return page_count > 0

        except Exception as e:
            print(f"    [VALIDATION] Not a valid PDF: {e}")
            return False

    def download_pdf(self, pdf_url: str, local_path: str, max_retries: int = 3) -> bool:
        """
        Download PDF with retries and validation
        Returns True if successful
        """
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = attempt * 2  # Exponential backoff
                    print(f"    [RETRY] Attempt {attempt}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)

                print(f"  --> Downloading PDF from {pdf_url[:60]}...")

                # Use session for better connection handling
                session = requests.Session()
                session.headers.update(self.headers)

                response = session.get(pdf_url, timeout=30, stream=True, allow_redirects=True)
                response.raise_for_status()

                # Check Content-Type header
                content_type = response.headers.get('Content-Type', '').lower()

                # Accept PDF or octet-stream (some servers don't set correct type)
                if 'html' in content_type:
                    print(f"    [ERROR] Got HTML instead of PDF (Content-Type: {content_type})")
                    print(f"    [INFO] This is likely bot detection or server error")
                    continue

                if 'pdf' not in content_type and 'octet-stream' not in content_type and 'application/force-download' not in content_type:
                    print(f"    [WARNING] Unexpected Content-Type: {content_type}")

                # Save to temporary file first
                temp_path = f"{local_path}.tmp"
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                file_size = os.path.getsize(temp_path)
                print(f"    [INFO] Downloaded {file_size / 1024:.1f} KB")

                # Validate PDF
                if self.is_valid_pdf(temp_path):
                    # Move from temp to final location
                    os.replace(temp_path, local_path)
                    print(f"  [OK] Valid PDF saved to {local_path}")
                    return True
                else:
                    print(f"    [ERROR] Downloaded file is not a valid PDF")
                    os.remove(temp_path)

                    # If it's HTML, show snippet for debugging
                    with open(temp_path, 'rb') as f:
                        first_bytes = f.read(100)
                        if b'html' in first_bytes.lower() or b'<!DOCTYPE' in first_bytes:
                            print(f"    [DEBUG] File starts with HTML, likely bot detection page")

                    continue

            except requests.exceptions.Timeout:
                print(f"    [ERROR] Timeout on attempt {attempt}")
            except requests.exceptions.RequestException as e:
                print(f"    [ERROR] Request failed: {e}")
            except Exception as e:
                print(f"    [ERROR] Unexpected error: {e}")

        print(f"  [FAILED] Could not download valid PDF after {max_retries} attempts")
        return False

    def download_and_save(self, circular_data: dict, max_retries: int = 3) -> str:
        """
        Download PDF with validation and retries
        Returns local path if successful, None otherwise
        """
        pdf_url = circular_data['pdf_url']
        source = circular_data['source']
        title = circular_data['title']

        print(f"\n[DOWNLOAD] {title[:60]}...")

        # Generate local path
        local_key = self.generate_local_key(source, pdf_url)

        # Create local directory for source
        local_dir = self.local_data_dir / source
        local_dir.mkdir(parents=True, exist_ok=True)

        # Local file path
        local_path = local_dir / f"{local_key.split('/')[-1]}"

        # Check if already exists and valid
        if local_path.exists():
            if self.is_valid_pdf(str(local_path)):
                print(f"  [SKIP] Valid PDF already exists: {local_path}")
                return str(local_key)
            else:
                print(f"  [INFO] Existing file is invalid, re-downloading...")
                os.remove(local_path)

        # Download PDF with retries
        if self.download_pdf(pdf_url, str(local_path), max_retries=max_retries):
            return str(local_key)
        else:
            return None


def download_circulars(circulars_list: list, max_retries: int = 3) -> list:
    """
    Download all circulars with robust validation

    Args:
        circulars_list: List of circular dicts
        max_retries: Number of retry attempts per PDF (default: 3)
    """
    print("\n" + "=" * 60)
    print("Starting PDF downloads (with validation)...")
    print("=" * 60)

    downloader = RobustDownloader()
    processed_circulars = []
    failed_circulars = []

    for circular in circulars_list:
        local_key = downloader.download_and_save(circular, max_retries=max_retries)

        if local_key:
            circular['s3_key'] = local_key  # Keep same key name for compatibility
            processed_circulars.append(circular)
        else:
            failed_circulars.append(circular)

    print("\n" + "=" * 60)
    print(f"Successfully downloaded: {len(processed_circulars)}/{len(circulars_list)}")
    if failed_circulars:
        print(f"Failed downloads: {len(failed_circulars)}")
        print("\nFailed PDFs:")
        for circ in failed_circulars[:5]:  # Show first 5
            print(f"  - {circ['title'][:60]}...")
            print(f"    URL: {circ['pdf_url']}")
    print("=" * 60)

    return processed_circulars


if __name__ == "__main__":
    # Test with sample circular
    test_circular = {
        'title': 'Test RBI Circular - KYC Guidelines 2024',
        'pdf_url': 'https://rbidocs.rbi.org.in/rdocs/notification/PDFs/NT19E5A78042FFD0446A99B0A5CA5B7E2BF31B88.PDF',
        'source': 'rbi'
    }

    downloader = RobustDownloader()
    local_key = downloader.download_and_save(test_circular)

    if local_key:
        print(f"\n[SUCCESS] PDF downloaded and validated!")
        print(f"Location: data/pdfs/{local_key}")
    else:
        print(f"\n[FAILED] Could not download valid PDF")
