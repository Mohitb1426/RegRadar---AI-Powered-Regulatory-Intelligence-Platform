"""
Improved web scraper for RBI and SEBI regulatory circulars
Better PDF link extraction and URL handling
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
import re
import time

try:
    from .db import circular_exists
except ImportError:
    from db import circular_exists


class ImprovedRBIScraper:
    """Improved scraper for Reserve Bank of India circulars"""

    BASE_URL = "https://www.rbi.org.in"

    # Use the circulars list page (more reliable)
    CIRCULARS_URL = f"{BASE_URL}/Scripts/BS_PressReleaseDisplay.aspx"

    # Alternative: Direct PDF links page
    ALT_URL = "https://rbidocs.rbi.org.in/rdocs/notification/PDFs/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.BASE_URL
        })

    def scrape_circulars(self, limit=50):
        """
        Scrape recent RBI circulars
        Returns list of dicts: {title, pdf_url, date, source}
        """
        print(f"\n[SCRAPER] Scraping RBI circulars...")

        circulars = []

        # Try multiple strategies
        circulars.extend(self._scrape_press_releases(limit))

        if len(circulars) < limit:
            circulars.extend(self._scrape_notifications(limit - len(circulars)))

        print(f"[OK] Found {len(circulars)} new RBI circulars")
        return circulars[:limit]

    def _scrape_press_releases(self, limit):
        """Scrape from press release page"""
        circulars = []

        try:
            url = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links to PDFs
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$|\.PDF$', re.IGNORECASE))

            for link in pdf_links[:limit]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    pdf_url = link.get('href')

                    # Fix relative URLs
                    if pdf_url.startswith('/'):
                        pdf_url = self.BASE_URL + pdf_url
                    elif pdf_url.startswith('rdocs'):
                        pdf_url = f"https://rbidocs.rbi.org.in/{pdf_url}"
                    elif not pdf_url.startswith('http'):
                        pdf_url = f"{self.BASE_URL}/{pdf_url}"

                    # Skip if already indexed
                    if circular_exists(pdf_url):
                        print(f"  [SKIP] Already indexed: {title[:60]}...")
                        continue

                    # Try to extract date
                    date_obj = self._extract_date(link)

                    circular = {
                        'title': title[:500],
                        'pdf_url': pdf_url,
                        'date': date_obj,
                        'source': 'rbi'
                    }

                    circulars.append(circular)
                    print(f"  [OK] Found: {title[:60]}...")

                except Exception as e:
                    continue

        except Exception as e:
            print(f"  [ERROR] Press releases scraping failed: {e}")

        return circulars

    def _scrape_notifications(self, limit):
        """Scrape from notifications page"""
        circulars = []

        try:
            url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find notification tables
            tables = soup.find_all('table', {'class': ['tablebg', 'tablestyle']})

            for table in tables:
                rows = table.find_all('tr')

                for row in rows:
                    pdf_link = row.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))

                    if pdf_link:
                        try:
                            title = pdf_link.get_text(strip=True) or row.get_text(strip=True)
                            if not title or len(title) < 10:
                                continue

                            pdf_url = pdf_link.get('href')

                            # Fix URLs
                            if not pdf_url.startswith('http'):
                                if 'rbidocs' in pdf_url:
                                    pdf_url = f"https://rbidocs.rbi.org.in/{pdf_url.lstrip('/')}"
                                else:
                                    pdf_url = f"{self.BASE_URL}/{pdf_url.lstrip('/')}"

                            if circular_exists(pdf_url):
                                continue

                            date_obj = self._extract_date(row)

                            circular = {
                                'title': title[:500],
                                'pdf_url': pdf_url,
                                'date': date_obj,
                                'source': 'rbi'
                            }

                            circulars.append(circular)
                            print(f"  [OK] Found: {title[:60]}...")

                            if len(circulars) >= limit:
                                return circulars

                        except Exception as e:
                            continue

        except Exception as e:
            print(f"  [ERROR] Notifications scraping failed: {e}")

        return circulars

    def _extract_date(self, element):
        """Extract date from element or nearby text"""
        try:
            # Try parent row
            parent = element.find_parent('tr')
            if parent:
                cells = parent.find_all('td')
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Look for date patterns
                    date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', cell_text)
                    if date_match:
                        return date_parser.parse(date_match.group(1), fuzzy=True).date()

                    # Try direct parsing
                    try:
                        return date_parser.parse(cell_text, fuzzy=True).date()
                    except:
                        continue
        except:
            pass

        return None


class ImprovedSEBIScraper:
    """Improved scraper for SEBI circulars"""

    BASE_URL = "https://www.sebi.gov.in"
    CIRCULARS_URL = f"{BASE_URL}/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=1&smid=0"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': self.BASE_URL
        })

    def scrape_circulars(self, limit=50):
        """Scrape recent SEBI circulars"""
        print(f"\n[SCRAPER] Scraping SEBI circulars...")

        try:
            response = self.session.get(self.CIRCULARS_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            circulars = []

            # Find all PDF links
            pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))

            for link in pdf_links[:limit]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    pdf_url = link.get('href')

                    # Fix relative URLs
                    if not pdf_url.startswith('http'):
                        pdf_url = f"{self.BASE_URL}/{pdf_url.lstrip('/')}"

                    if circular_exists(pdf_url):
                        print(f"  [SKIP] Already indexed: {title[:60]}...")
                        continue

                    # Try to extract date
                    date_obj = None
                    date_match = re.search(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b', title)
                    if date_match:
                        try:
                            date_obj = date_parser.parse(date_match.group(1)).date()
                        except:
                            pass

                    circular = {
                        'title': title[:500],
                        'pdf_url': pdf_url,
                        'date': date_obj,
                        'source': 'sebi'
                    }

                    circulars.append(circular)
                    print(f"  [OK] Found: {title[:60]}...")

                except Exception as e:
                    continue

            print(f"[OK] Found {len(circulars)} new SEBI circulars")
            return circulars

        except Exception as e:
            print(f"[ERROR] SEBI scraping failed: {e}")
            return []


def scrape_all_circulars(limit=50):
    """
    Scrape circulars from both RBI and SEBI with improved methods
    """
    print("=" * 60)
    print("Starting circular discovery (Improved)...")
    print("=" * 60)

    all_circulars = []

    # Scrape RBI
    rbi_scraper = ImprovedRBIScraper()
    rbi_circulars = rbi_scraper.scrape_circulars(limit=limit)
    all_circulars.extend(rbi_circulars)

    # Small delay between scrapers
    time.sleep(1)

    # Scrape SEBI
    sebi_scraper = ImprovedSEBIScraper()
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
    circulars = scrape_all_circulars(limit=5)

    print("\nSample circulars:")
    for i, circular in enumerate(circulars[:3], 1):
        print(f"\n{i}. {circular['title']}")
        print(f"   URL: {circular['pdf_url']}")
        print(f"   Date: {circular['date']}")
        print(f"   Source: {circular['source'].upper()}")
