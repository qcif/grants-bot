"""Module for scraping tender descriptions from AusTender URLs."""
import re
from typing import Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class TenderDetails:
    """Data class to store tender details."""
    description: str
    category: str
    agency: str


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and newlines.

    Args:
        text: The text to clean.

    Returns:
        The cleaned text.
    """
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def extract_tender_details(html: str) -> Optional[TenderDetails]:
    """Extract tender details from AusTender HTML.

    Args:
        html: The HTML content of the tender page.

    Returns:
        A TenderDetails object containing the extracted information,
        or None if the page couldn't be parsed.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Find the main content div
    content = soup.find('div', {'class': 'box boxW listInner'})
    if not content:
        return None

    # Extract details from the list-desc divs
    details: dict[str, str] = {}
    for desc in content.find_all('div', {'class': 'list-desc'}):
        label = desc.find('label')
        if label:
            key = label.get('for', '').replace('_', ' ').title()
            value_div = desc.find('div', {'class': 'list-desc-inner'})
            if value_div:
                value = clean_text(value_div.text)
                details[key] = value

    return TenderDetails(
        description=details.get('Description', ''),
        category=details.get('Category', ''),
        agency=details.get('Agency', '')
    )


def scrape_tender(url: str) -> Optional[TenderDetails]:
    """Scrape tender details from an AusTender URL.

    Args:
        url: The URL of the tender page.

    Returns:
        A TenderDetails object containing the tender information,
        or None if the page couldn't be accessed or parsed.

    Raises:
        requests.RequestException: If there's an error accessing the URL.
    """
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/91.0.4472.124 Safari/537.36'
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return extract_tender_details(response.text)


if __name__ == "__main__":
    # Test with the example URLs from the email
    test_urls = [
        ("https://www.tenders.gov.au/Atm/Show/"
         "26782498-62fa-4a2f-a65f-37b562197b5a"),
        ("https://www.tenders.gov.au/Atm/Show/"
         "c95aa845-66c8-4996-89cf-4a3ccd1ea9eb")
    ]

    for url in test_urls:
        print(f"\nScraping {url}...")
        try:
            tender = scrape_tender(url)
            if tender:
                print(f"Description: {tender.description}")
                print(f"Category: {tender.category}")
                print(f"Agency: {tender.agency}")
            else:
                print("Failed to parse tender details")
        except requests.RequestException as e:
            print(f"Error accessing URL: {e}")
