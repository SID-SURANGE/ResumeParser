# Standard library
import json
import logging
from typing import List, Dict, Union

# Third-party imports
from json_repair import repair_json

# Local imports
from utils import prompts
from models.base_config import BaseParser
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class ResumeIssueParser(BaseParser):
    """Handles resume issue detection and validation"""

    def _validate_input(self, text: str) -> None:
        """Validate input text"""
        if not text or not isinstance(text, str):
            raise ValueError("Invalid input: text must be a non-empty string")

    def _process_json_response(
        self, message_content: str, key: str
    ) -> Union[List[Dict[str, str]], List]:
        """Process JSON response from LLM"""
        try:
            if message_content.startswith("```"):
                message_content = message_content.strip("```json").strip("```")

            message_content = repair_json(message_content)

            data = json.loads(message_content)
            return data.get(key, [])
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return []

    def spell_check(self, resume_text: str, model: str) -> List[Dict[str, str]]:
        """Perform spell check on resume text"""
        self._validate_input(resume_text)

        message_content = self.llm_client.get_completion(
            model,
            prompts.PROMPT_TEXT_SPELL_CHECK,
            prompts.USER_PROMPT_SPELL_CHECK,
            resume_text,
        )

        misspelled_words = self._process_json_response(
            message_content, "misspelled_words"
        )

        if not misspelled_words:
            return [{"message": "No incorrect words found"}]

        return [
            {
                "incorrect_word": item["incorrect_word"],
                "correct_word": item["correct_word"],
            }
            for item in misspelled_words
            if item["incorrect_word"].strip() != item["correct_word"].strip()
        ]
