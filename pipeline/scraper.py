"""
Web scraper for RBI and SEBI regulatory circulars
Discovers new circulars from official websites
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
import re

try:
    from .db import circular_exists
except ImportError:
    from db import circular_exists


class RBIScraper:
    """Scraper for Reserve Bank of India circulars"""

    BASE_URL = "https://www.rbi.org.in"
    CIRCULARS_URL = f"{BASE_URL}/scripts/BS_ViewMasCirculardetails.aspx"

    def scrape_circulars(self, limit=50):
        """
        Scrape recent RBI circulars
        Returns list of dicts: {title, pdf_url, date, source}
        """
        print(f"\n[SCRAPER] Scraping RBI circulars from {self.CIRCULARS_URL}")

        try:
            response = requests.get(self.CIRCULARS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            circulars = []

            # Find all circular rows (adapt selectors based on actual RBI website structure)
            # This is a generic pattern - may need adjustment
            rows = soup.find_all('tr')

            for row in rows[:limit]:
                try:
                    # Look for PDF links
                    pdf_link = row.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
                    if not pdf_link:
                        continue

                    # Extract title
                    title_text = pdf_link.get_text(strip=True)
                    if not title_text or len(title_text) < 10:
                        # Try to get title from another cell
                        cells = row.find_all('td')
                        title_text = ' '.join([cell.get_text(strip=True) for cell in cells if cell.get_text(strip=True)])

                    # Extract PDF URL
                    pdf_url = pdf_link.get('href')
                    if not pdf_url.startswith('http'):
                        pdf_url = self.BASE_URL + pdf_url if pdf_url.startswith('/') else f"{self.BASE_URL}/{pdf_url}"

                    # Extract date (look for date pattern in row)
                    date_obj = None
                    date_text = None
                    cells = row.find_all('td')
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        # Try to parse date
                        try:
                            date_obj = date_parser.parse(cell_text, fuzzy=True)
                            date_text = date_obj.date()
                            break
                        except:
                            continue

                    # Check if already exists in database
                    if circular_exists(pdf_url):
                        print(f"  [SKIP] Already indexed: {title_text[:60]}...")
                        continue

                    circular = {
                        'title': title_text[:500],  # Limit to 500 chars
                        'pdf_url': pdf_url,
                        'date': date_text,
                        'source': 'rbi'
                    }

                    circulars.append(circular)
                    print(f"  [OK] Found new: {title_text[:60]}...")

                except Exception as e:
                    continue  # Skip problematic rows

            print(f"[OK] Found {len(circulars)} new RBI circulars")
            return circulars

        except Exception as e:
            print(f"[ERROR] Error scraping RBI: {e}")
            return []


class SEBIScraper:
    """Scraper for Securities and Exchange Board of India circulars"""

    BASE_URL = "https://www.sebi.gov.in"
    CIRCULARS_URL = f"{BASE_URL}/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=34"

    def scrape_circulars(self, limit=50):
        """
        Scrape recent SEBI circulars
        Returns list of dicts: {title, pdf_url, date, source}
        """
        print(f"\n[SCRAPER] Scraping SEBI circulars from {self.CIRCULARS_URL}")

        try:
            response = requests.get(self.CIRCULARS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            circulars = []

            # Find all circular links (adapt selectors based on actual SEBI website structure)
            # This is a generic pattern - may need adjustment
            links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))

            for link in links[:limit]:
                try:
                    title_text = link.get_text(strip=True)

                    # Skip if title is too short or generic
                    if not title_text or len(title_text) < 10:
                        continue

                    # Extract PDF URL
                    pdf_url = link.get('href')
                    if not pdf_url.startswith('http'):
                        pdf_url = self.BASE_URL + pdf_url if pdf_url.startswith('/') else f"{self.BASE_URL}/{pdf_url}"

                    # Check if already exists
                    if circular_exists(pdf_url):
                        print(f"  [SKIP] Already indexed: {title_text[:60]}...")
                        continue

                    # Try to extract date from title or nearby elements
                    date_obj = None
                    # Look for date pattern in title
                    date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b', title_text)
                    if date_match:
                        try:
                            date_obj = date_parser.parse(date_match.group(1)).date()
                        except:
                            pass

                    # Look for date in parent row
                    if not date_obj:
                        parent = link.find_parent('tr')
                        if parent:
                            cells = parent.find_all('td')
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                try:
                                    date_obj = date_parser.parse(cell_text, fuzzy=True).date()
                                    break
                                except:
                                    continue

                    circular = {
                        'title': title_text[:500],
                        'pdf_url': pdf_url,
                        'date': date_obj,
                        'source': 'sebi'
                    }

                    circulars.append(circular)
                    print(f"  [OK] Found new: {title_text[:60]}...")

                except Exception as e:
                    continue  # Skip problematic links

            print(f"[OK] Found {len(circulars)} new SEBI circulars")
            return circulars

        except Exception as e:
            print(f"[ERROR] Error scraping SEBI: {e}")
            return []


def scrape_all_circulars(limit=50):
    """
    Scrape circulars from both RBI and SEBI
    Returns combined list of new circulars
    """
    print("=" * 60)
    print("Starting circular discovery...")
    print("=" * 60)

    all_circulars = []

    # Scrape RBI
    rbi_scraper = RBIScraper()
    rbi_circulars = rbi_scraper.scrape_circulars(limit=limit)
    all_circulars.extend(rbi_circulars)

    # Scrape SEBI
    sebi_scraper = SEBIScraper()
    sebi_circulars = sebi_scraper.scrape_circulars(limit=limit)
    all_circulars.extend(sebi_circulars)

    print("\n" + "=" * 60)
    print(f"Total new circulars discovered: {len(all_circulars)}")
    print(f"  - RBI: {len(rbi_circulars)}")
    print(f"  - SEBI: {len(sebi_circulars)}")
    print("=" * 60)

    return all_circulars


if __name__ == "__main__":
    # Test scraper
    circulars = scrape_all_circulars(limit=10)

    print("\nSample circulars:")
    for i, circular in enumerate(circulars[:3], 1):
        print(f"\n{i}. {circular['title']}")
        print(f"   URL: {circular['pdf_url']}")
        print(f"   Date: {circular['date']}")
        print(f"   Source: {circular['source'].upper()}")
