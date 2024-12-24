# standard library imports
import os
import logging
from typing import Optional

# third party imports
import fitz
from docling.document_converter import DocumentConverter

# local imports
from utils.logging_config import configure_logging
from src.services.parser.exceptions import ResumeParsingError

configure_logging()
logger = logging.getLogger(__name__)


class ResumeReader:
    """
    Handles reading and extracting text content from resume files.

    Attributes:
        supported_formats (List[str]): List of supported output formats
    """

    def __init__(self):
        self.supported_formats = ["html", "text"]
        self.converter = DocumentConverter()

    def read_resume(self, path: str, output_type: str) -> Optional[str]:
        """
        Reads and extracts text from resume file.

        Args:
            path (str): Path to resume file
            output_type (str): Output format ("html" or "text")

        Returns:
            Optional[str]: Extracted text content or None if extraction fails

        Raises:
            ResumeParsingError: If file reading fails or format is unsupported
        """
        try:
            self._validate_inputs(path, output_type)

            if output_type == "html":
                result = self.converter.convert(path)
                md_text = (
                    result.document.export_to_markdown()
                )  # or pymupdf4llm.to_markdown(path)
                plain_text = result.document.export_to_text()
            else:
                with fitz.open(path) as doc:
                    text = " ".join(page.get_text() for page in doc)
                    md_text, plain_text = text, text
            return md_text, plain_text

        except Exception as e:
            logger.error(f"Error reading resume: {e}")
            raise ResumeParsingError(
                message="Failed to read resume file",
                code=1003,
                details={"path": path, "error": str(e)},
            )

    def _validate_inputs(self, path: str, output_type: str) -> None:
        """Validates input parameters before processing."""
        if not os.path.exists(path):
            raise ResumeParsingError(
                message="Resume file not found", code=1001, details={"path": path}
            )

        if output_type not in self.supported_formats:
            raise ResumeParsingError(
                message=f"Unsupported output type. Use {self.supported_formats}",
                code=1002,
                details={"output_type": output_type},
            )
