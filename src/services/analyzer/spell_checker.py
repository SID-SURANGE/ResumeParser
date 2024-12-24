# standard library
import logging
from typing import List, Dict

# local imports
from models.quality_check import ResumeIssueParser
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class SpellChecker:
    def __init__(self):
        self.issue_parser = ResumeIssueParser()

    def spell_check(self, text: str, model: str) -> List[Dict[str, str]]:
        """Identify spelling errors in the text using LLM."""
        try:
            corrections = self.issue_parser.spell_check(text, model)
            if isinstance(corrections, dict) and "message" in corrections:
                logger.info(corrections["message"])
                return []
            return corrections
        except Exception as e:
            logger.error(f"Spell check failed: {e}")
            return []
