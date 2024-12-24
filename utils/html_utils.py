# standard library imports
import re, logging

# local imports
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def sanitize_html_content(html_text: str) -> str:
    """
    Sanitizes HTML content by removing unwanted patterns and characters.

    Args:
        html_text (str): HTML table string to sanitize

    Returns:
        str: Sanitized HTML string
    """
    try:
        html_text = re.sub(r"•\s*-", "•", html_text)
        html_text = html_text.replace("#", "")
        html_text = re.sub(r"[:\-,]{2,}", lambda m: m.group()[0], html_text)
    except Exception as e:
        logger.info("Error while santizing html content ", e)

    return html_text
