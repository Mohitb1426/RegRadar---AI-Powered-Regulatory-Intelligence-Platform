"""
Local PDF downloader (without S3)
Downloads regulatory circulars to local filesystem only
"""

import os
import requests
from pathlib import Path
import hashlib


class LocalDownloader:
    """Downloads PDFs to local filesystem"""

    def __init__(self):
        self.local_data_dir = Path("data/pdfs")
        self.local_data_dir.mkdir(parents=True, exist_ok=True)

    def generate_local_key(self, source: str, pdf_url: str) -> str:
        """
        Generate unique local path for PDF
        Format: {source}/{hash}.pdf
        """
        url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:12]
        return f"{source}/{url_hash}.pdf"

    def download_pdf(self, pdf_url: str, local_path: str) -> bool:
        """
        Download PDF from URL to local filesystem
        Returns True if successful
        """
        try:
            print(f"  --> Downloading PDF from {pdf_url[:60]}...")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(pdf_url, headers=headers, timeout=60, stream=True)
            response.raise_for_status()

            # Verify it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' not in content_type.lower() and not pdf_url.lower().endswith('.pdf'):
                print(f"  [ERROR] Not a PDF file: {content_type}")
                return False

            # Save to local file
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(local_path)
            print(f"  [OK] Downloaded {file_size / 1024:.1f} KB to {local_path}")
            return True

        except Exception as e:
            print(f"  [ERROR] Download failed: {e}")
            return False

    def download_and_save(self, circular_data: dict) -> str:
        """
        Download PDF and save locally
        Returns local path if successful, None otherwise

        Args:
            circular_data: dict with keys {title, pdf_url, source}
        """
        pdf_url = circular_data['pdf_url']
        source = circular_data['source']
        title = circular_data['title']

        print(f"\n[DOWNLOAD] Processing: {title[:60]}...")

        # Generate local path
        local_key = self.generate_local_key(source, pdf_url)

        # Create local directory for source
        local_dir = self.local_data_dir / source
        local_dir.mkdir(parents=True, exist_ok=True)

        # Local file path
        local_path = local_dir / f"{local_key.split('/')[-1]}"

        # Check if already exists
        if local_path.exists():
            print(f"  [SKIP] Already exists: {local_path}")
            return str(local_key)

        # Download PDF
        if not self.download_pdf(pdf_url, str(local_path)):
            return None

        return str(local_key)


def download_circulars(circulars_list: list) -> list:
    """
    Download all circulars locally (no S3)
    """
    print("\n" + "=" * 60)
    print("Starting PDF downloads (local storage)...")
    print("=" * 60)

    downloader = LocalDownloader()
    processed_circulars = []

    for circular in circulars_list:
        local_key = downloader.download_and_save(circular)

        if local_key:
            circular['s3_key'] = local_key  # Keep same key name for compatibility
            processed_circulars.append(circular)

    print("\n" + "=" * 60)
    print(f"Successfully downloaded: {len(processed_circulars)}/{len(circulars_list)}")
    print("=" * 60)

    return processed_circulars


if __name__ == "__main__":
    # Test downloader with sample circular
    test_circular = {
        'title': 'Test RBI Circular - KYC Guidelines 2024',
        'pdf_url': 'https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12345',
        'source': 'rbi'
    }

    downloader = LocalDownloader()
    local_key = downloader.download_and_save(test_circular)

    if local_key:
        print(f"\n[OK] Test successful! Local key: {local_key}")
    else:
        print("\n[ERROR] Test failed")
