# standard library imports
import logging
from typing import List, Set

# third party imports
import spacy

# local imports
from utils.constants import SECTIONS, ERROR_MESSAGES
from utils.logging_config import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


class SectionChecker:
    """
    Analyzes resume text to identify missing sections using SpaCy NLP.
    """

    # Load SpaCy model once at class level
    nlp = spacy.load("en_core_web_lg")

    # Entity labels for section detection
    ENTITY_LABELS: Set[str] = {
        "ORG",
        "WORK_OF_ART",
        "GPE",
        "PRODUCT",
        "LANGUAGE",
        "PERSON",
        "DATE",
        "CARDINAL",
    }

    def __init__(self):
        pass

    def missing_section_check(self, text: str) -> List[str]:
        """
        Check for missing sections in a resume using SpaCy.

        Args:
            text: Resume text to analyze

        Returns:
            List of missing section names
        """
        if not text or not text.strip():
            logger.warning(ERROR_MESSAGES["EMPTY_TEXT"])
            return list(SECTIONS.keys())

        try:
            doc = self.nlp(text)
            found_sections = set()

            # Check entities for section keywords
            for ent in doc.ents:
                if ent.label_ in self.ENTITY_LABELS:
                    for section, keywords in SECTIONS.items():
                        if any(keyword in ent.text.lower() for keyword in keywords):
                            found_sections.add(section)

            # Check text for section keywords
            text_lower = text.lower()
            for section, keywords in SECTIONS.items():
                if any(keyword in text_lower for keyword in keywords):
                    found_sections.add(section)

            missing_sections = list(set(SECTIONS.keys()) - found_sections)
            logger.debug(f"\n Found missing sections: {missing_sections}")

            return missing_sections

        except spacy.errors.SpacyError as e:
            logger.error(ERROR_MESSAGES["SECTION_CHECK"].format(str(e)))
            return []
        except (KeyError, AttributeError) as e:
            logger.error(ERROR_MESSAGES["SECTION_CHECK"].format(str(e)))
            return []
