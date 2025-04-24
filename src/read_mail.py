"""Module for reading and processing postfix inbox mail files."""
import sys
from typing import List
from dataclasses import dataclass

from src.email_parser import extract_csv_from_email, extract_urls_from_csv
from src.scrape_tender import scrape_tender, TenderDetails
from src.gpt import GPT


@dataclass
class TenderAnalysis:
    """Data class to store tender details and analysis."""
    tender: TenderDetails
    score: float
    analysis: str


def read_mail_file(mail_path: str) -> str:
    """Read a postfix inbox mail file.

    Args:
        mail_path: Path to the mail file.

    Returns:
        The contents of the mail file as a string.
    """
    with open(mail_path, 'r', encoding='utf-8') as f:
        return f.read()


def process_tender_url(url: str, gpt: GPT) -> TenderAnalysis:
    """Process a single tender URL.

    Args:
        url: The tender URL to process.
        gpt: GPT instance for analysis.

    Returns:
        A TenderAnalysis object containing the tender details and analysis.
    """
    tender = scrape_tender(url)
    if not tender:
        raise ValueError(f"Failed to scrape tender from URL: {url}")

    # Create a prompt for GPT analysis
    prompt = (
        f"Agency: {tender.agency}\n"
        f"Category: {tender.category}\n"
        f"Description: {tender.description}\n"
    )

    # Get GPT analysis
    score = gpt.classify_tender(prompt)

    return TenderAnalysis(tender=tender, score=score, analysis=prompt)


def analyze_mail_file(mail_path: str) -> List[TenderAnalysis]:
    """Process a mail file containing tender URLs.

    Args:
        mail_path: Path to the mail file.

    Returns:
        List of TenderAnalysis objects for each tender found in the mail.
    """
    # Read and parse the mail file
    gpt = GPT()
    mail_content = read_mail_file(mail_path)
    csv_data = extract_csv_from_email(mail_content)
    if not csv_data:
        raise ValueError("No CSV data found in email")

    # Extract URLs from CSV data
    urls = extract_urls_from_csv(csv_data)
    if not urls:
        raise ValueError("No URLs found in CSV data")

    # Process each URL
    results = []
    for url in urls:
        try:
            analysis = process_tender_url(url, gpt)
            results.append(analysis)
        except Exception as e:
            print(f"Error processing URL {url}: {e}", file=sys.stderr)

    return results
