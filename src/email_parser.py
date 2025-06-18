"""Module for parsing emails and extracting attachments."""
import base64
import email
import quopri
from email import policy
from typing import Optional, List
import csv
from io import StringIO


def parse_email(raw_email: str) -> email.message.EmailMessage:
    """Parse a raw email string into an EmailMessage object.

    Args:
        raw_email: The raw email content as a string.

    Returns:
        An EmailMessage object representing the parsed email.
    """
    return email.message_from_string(raw_email, policy=policy.default)


def find_csv_attachment(
    email_msg: email.message.EmailMessage
) -> Optional[email.message.EmailMessage]:
    """Find the first CSV attachment in an email message.

    Args:
        email_msg: The parsed email message.

    Returns:
        The CSV attachment as an EmailMessage, or None if no CSV
        attachment is found.
    """
    for part in email_msg.walk():
        if part.get_content_type() == "text/csv":
            return part
    return None


def decode_csv_attachment(
    attachment: email.message.EmailMessage
) -> List[dict]:
    """Decode a CSV attachment and return its contents.

    Returns a list of dictionaries containing the CSV data.

    Args:
        attachment: The CSV attachment as an EmailMessage.

    Returns:
        A list of dictionaries containing the CSV data.

    Raises:
        ValueError: If the attachment cannot be decoded or parsed as CSV.
    """
    # Get the content transfer encoding
    encoding = attachment["Content-Transfer-Encoding"]

    # Get the raw content
    content = attachment.get_payload()

    # Decode based on the encoding
    if encoding == "base64":
        content = base64.b64decode(content).decode("utf-8-sig")
    elif encoding == "quoted-printable":
        content = quopri.decodestring(content).decode("utf-8-sig")
    else:
        content = content.decode("utf-8-sig")

    # Parse the CSV content
    csv_file = StringIO(content)
    reader = csv.DictReader(csv_file)
    return list(reader)


def extract_csv_from_email(
    raw_email: str
) -> Optional[List[dict]]:
    """Extract and decode a CSV attachment from a raw email.

    Args:
        raw_email: The raw email content as a string.

    Returns:
        A list of dictionaries containing the CSV data, or None if no CSV
        attachment is found.

    Raises:
        ValueError: If the CSV attachment cannot be decoded or parsed.
    """
    email_msg = parse_email(raw_email)
    csv_attachment = find_csv_attachment(email_msg)

    if csv_attachment is None:
        return None

    return decode_csv_attachment(csv_attachment)


def extract_urls_from_csv(csv_data: List[dict]) -> List[str]:
    """Extract URLs from CSV data.

    Args:
        csv_data: List of dictionaries containing CSV data.

    Returns:
        List of URLs found in the CSV data.
    """
    urls = []
    for row in csv_data:
        # Look for URL in common column names
        for key in row:
            if 'url' in key.lower() and row[key]:
                urls.append(row[key])
    return urls
