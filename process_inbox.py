#!/usr/bin/env python3
"""Entrypoint script for analyzing tender emails.
Sends a notification email if any matching tenders are found.
"""

import os
import sys
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from dataclasses import dataclass

from src.read_mail import analyze_mail_file
from src.scrape_tender import TenderDetails

load_dotenv()
MIN_TENDER_SCORE = 7


@dataclass
class Config:
    """Configuration for the email processing system."""
    smtp_hostname: str
    smtp_port: str
    smtp_username: str
    smtp_password: str
    notification_email: str
    postfix_mail_dir: Path
    postfix_read_dir: Path


def load_config() -> Config:
    """Load configuration from environment variables.

    Returns:
        Config object containing configuration values.

    Raises:
        ValueError: If required environment variables are missing.
    """

    required_vars = [
        {
            'name': 'SMTP_HOSTNAME',
        },
        {
            'name': 'SMTP_PORT',
        },
        {
            'name': 'SMTP_USERNAME',
        },
        {
            'name': 'SMTP_PASSWORD',
        },
        {
            'name': 'NOTIFICATION_EMAIL',
        },
        {
            'name': 'POSTFIX_MAIL_DIR',
            'type': Path,
        },
        {
            'name': 'POSTFIX_READ_DIR',
            'type': Path,
        },
    ]

    config_values = {}
    for var in required_vars:
        name = var['name']
        _type = var.get('type', str)
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config_values[name.lower()] = _type(value)

    return Config(**config_values)


def send_notification(
    config: Config,
    tender: TenderDetails,
    score: float
) -> None:
    """Send email notification about a high-scoring tender.

    Args:
        config: Configuration object containing SMTP settings.
        tender: The tender details to notify about.
        score: The tender's relevance score.
    """
    # Create message
    msg = MIMEMultipart()
    msg['From'] = config.smtp_username
    msg['To'] = config.notification_email
    msg['Subject'] = f"High-Scoring Tender Alert: {tender.agency}"

    # Create email body
    body = f"""
High-Scoring Tender Alert (Score: {score}/10)

{tender.url}

Agency: {tender.agency}
Category: {tender.category}
Description: {tender.description}
"""

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    with smtplib.SMTP(
        config.smtp_hostname,
        int(config.smtp_port),
    ) as server:
        server.starttls()
        server.login(config.smtp_username, config.smtp_password)
        server.send_message(msg)


def process_mail_dir() -> None:
    """Process all mail files in the given directory.

    Args:
        config: Configuration object containing SMTP settings.
        mail_dir: Path to the directory containing mail files.
    """
    config = load_config()
    mail_path = config.postfix_mail_dir
    if not mail_path.exists():
        print(
            f"Error: Mail directory not found: {config.postfix_mail_dir}",
            file=sys.stderr)
        return

    # Process each mail file
    for mail_file in mail_path.glob('*'):
        if mail_file.is_file():
            try:
                print(f"Processing {mail_file.name}...")
                results = analyze_mail_file(str(mail_file))

                # Check for high-scoring tenders
                for result in results:
                    print(f"Analysing tender: {result.tender.url}")
                    print(f"Score returned: {result.score}")
                    if result.score > MIN_TENDER_SCORE:
                        print(
                            "Found high-scoring tender:",
                            result.tender.agency,
                        )
                        send_notification(
                            config,
                            result.tender,
                            result.score,
                        )

            except Exception as e:
                print(
                    f"Error processing {mail_file.name}: {e}",
                    file=sys.stderr,
                )
            # Archive the processed mail file
            archive_dir = config.postfix_read_dir
            archive_dir.mkdir(exist_ok=True, parents=True)
            mail_file.rename(archive_dir / mail_file.name)


def main():
    """Main entry point for the script."""
    try:
        process_mail_dir()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
