# standard library imports
import logging
from typing import List

# local imports
from src.services.analyzer.spell_checker import SpellChecker
from src.services.analyzer.section_checker import SectionChecker
from utils.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """
    Main analyzer class for resume content validation and issue detection.

    Combines spell checking and section validation functionality.
    """

    def __init__(self):
        """Initialize the ResumeAnalyzer with required checkers."""
        try:
            self.spell_checker = SpellChecker()
            self.section_checker = SectionChecker()
        except Exception as e:
            logger.error(f"Failed to initialize ResumeAnalyzer: {e}")
            raise

    def analyze_resume(self, text: str, model: str) -> str:
        """
        Perform comprehensive resume analysis.

        Args:
            text (str): Resume text content to analyze
            model(str): name of the model to use

        Returns:
            IssueCheckResult: Analysis results containing missing sections
                            and spelling corrections
        """
        try:
            # Check for missing sections
            missing_sections = self.section_checker.missing_section_check(text)

            # Check for spelling errors
            spelling_corrections = self.spell_checker.spell_check(text, model)

            return self._generate_html(missing_sections, spelling_corrections)

        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return ""

    def _generate_html(
        self, missing_sections: List[str], spelling_corrections: List[dict]
    ) -> str:
        """
        Generate HTML output for the analysis results.

        Args:
            analysis_result (IssueCheckResult): Analysis results to format

        Returns:
            Formatted HTML string
        """
        logger.info(f"\n spelling corrections: {spelling_corrections}")
        logger.info(f"\n missing sections: {missing_sections}")
        try:
            return f"""
                <table class="issue-table">
                    <tr>
                        <th>Missing Section</th>
                        <th>Incorrect Spelling</th>
                    </tr>
                    <tr>
                        <td >
                            {("<br>".join([f"• {item}" for item in missing_sections]) if missing_sections else "")}
                        </td>
                        <td>
                            {("<br>".join([f"• {item['incorrect_word']} (Correct: {item['correct_word']})" 
                            for item in spelling_corrections]) if spelling_corrections else "-")}
                        </td>
                    </tr>
                </table>
            """
        except Exception as e:
            logger.error(f"HTML report generation failed: {e}")
            return ""
