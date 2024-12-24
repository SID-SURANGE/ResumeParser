# standard library imports
import logging
from typing import Dict, Any

# local imports
from models.content_parser import ResumeDataParser
from src.services.parser.exceptions import ResumeParsingError
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

# Create an instance of the ResumeDataParser class
main_parser_obj = ResumeDataParser()


class SectionExtractor:
    """Handles extraction of structured sections from resume text."""

    def fetch_sections(self, html_text: str, model: str) -> Dict[str, Any]:
        """
        Extracts structured sections from resume text.

        Args:
            html_text (str): Input HTML text
            model (str): name of model to use

        Returns:
            Dict[str, Any]: Dictionary with section names and content

        Raises:
            ResumeParsingError: If input is empty or section extraction fails
        """
        try:
            self._validate_input(html_text)

            section_data = main_parser_obj.get_sections(html_text, model)
            if not section_data:
                raise ResumeParsingError(
                    message="No sections extracted from text",
                    code=2002,
                    details={"text_preview": html_text[:100]},
                )
            return section_data

        except Exception as e:
            logger.error(f"Section extraction error: {e}")
            raise ResumeParsingError(
                message="Failed to extract resume sections",
                code=2003,
                details={"error": str(e)},
            )

    def _validate_input(self, html_text: str) -> None:
        """Validates input text before processing."""
        if not html_text.strip():
            raise ResumeParsingError(
                message="Empty input text",
                code=2001,
                details={"text_length": len(html_text)},
            )
