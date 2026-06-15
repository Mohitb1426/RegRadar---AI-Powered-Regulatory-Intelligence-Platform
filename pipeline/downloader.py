"""
PDF downloader with AWS S3 storage
Downloads regulatory circulars and uploads to S3 bucket
"""

import os
import requests
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse
from pathlib import Path
from dotenv import load_dotenv
import hashlib

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


class S3Downloader:
    """Downloads PDFs and uploads to AWS S3"""

    def __init__(self):
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME]):
            raise ValueError("AWS credentials or bucket name not configured in .env")

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = AWS_BUCKET_NAME
        self.local_data_dir = Path("data/pdfs")
        self.local_data_dir.mkdir(parents=True, exist_ok=True)

    def generate_s3_key(self, source: str, pdf_url: str) -> str:
        """
        Generate unique S3 key for PDF
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
            print(f"  [OK] Downloaded {file_size / 1024:.1f} KB")
            return True

        except Exception as e:
            print(f"  [ERROR] Download failed: {e}")
            return False

    def upload_to_s3(self, local_path: str, s3_key: str) -> bool:
        """
        Upload PDF to S3 bucket
        Returns True if successful
        """
        try:
            print(f"  --> Uploading to S3: {s3_key}")

            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'application/pdf'}
            )

            print(f"  [OK] Uploaded to s3://{self.bucket_name}/{s3_key}")
            return True

        except ClientError as e:
            print(f"  [ERROR] S3 upload failed: {e}")
            return False

    def download_and_upload(self, circular_data: dict) -> str:
        """
        Download PDF and upload to S3
        Returns S3 key if successful, None otherwise

        Args:
            circular_data: dict with keys {title, pdf_url, source}
        """
        pdf_url = circular_data['pdf_url']
        source = circular_data['source']
        title = circular_data['title']

        print(f"\n[DOWNLOAD] Processing: {title[:60]}...")

        # Generate S3 key
        s3_key = self.generate_s3_key(source, pdf_url)

        # Check if already exists in S3
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            print(f"  [SKIP] Already exists in S3: {s3_key}")
            return s3_key
        except ClientError:
            pass  # Doesn't exist, proceed with download

        # Create local directory for source
        local_dir = self.local_data_dir / source
        local_dir.mkdir(parents=True, exist_ok=True)

        # Local file path
        local_path = local_dir / f"{s3_key.split('/')[-1]}"

        # Download PDF
        if not self.download_pdf(pdf_url, str(local_path)):
            return None

        # Upload to S3
        if not self.upload_to_s3(str(local_path), s3_key):
            return None

        # Optionally delete local file after successful upload (to save space)
        # os.remove(local_path)

        return s3_key

    def download_from_s3(self, s3_key: str, local_path: str) -> bool:
        """
        Download file from S3 to local filesystem
        Useful for processing already-uploaded PDFs
        """
        try:
            print(f"  --> Downloading from S3: {s3_key}")
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            print(f"  [OK] Downloaded to {local_path}")
            return True
        except ClientError as e:
            print(f"  [ERROR] S3 download failed: {e}")
            return False


def download_circulars(circulars_list: list) -> list:
    """
    Download all circulars and return list with s3_key added
    """
    print("\n" + "=" * 60)
    print("Starting PDF downloads...")
    print("=" * 60)

    downloader = S3Downloader()
    processed_circulars = []

    for circular in circulars_list:
        s3_key = downloader.download_and_upload(circular)

        if s3_key:
            circular['s3_key'] = s3_key
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

    downloader = S3Downloader()
    s3_key = downloader.download_and_upload(test_circular)

    if s3_key:
        print(f"\n[OK] Test successful! S3 key: {s3_key}")
    else:
        print("\n[ERROR] Test failed")
