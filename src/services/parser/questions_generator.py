# standard library imports
import re
import logging
from typing import List, Union, Optional

# local imports
from models.content_parser import ResumeDataParser
from src.services.parser.exceptions import ResumeParsingError
from configs.config import MODEL_MAP

logger = logging.getLogger(__name__)
main_parser_obj = ResumeDataParser()


class QuestionGenerator:
    """Handles generation of interview questions based on skills."""

    def _format_questions(self, questions_text: str, num_questions: int) -> str:
        """
        Format questions string for better display in Gradio textbox.

        Args:
            questions_text: String containing all questions with bullet points

        Returns:
            Formatted string with numbered questions and proper spacing
        """
        if not questions_text:
            return "No questions available."

        # Split by bullet point and clean up
        questions = [q.strip() for q in questions_text.split("•") if q.strip()]

        # Format with numbers and spacing
        formatted_output = ""
        for i, question in enumerate(questions, 1):
            formatted_output += f"{i}. {question}\n\n"

            # extra handling to return only the questions asked in response
            if i == num_questions:
                break

        return formatted_output

    def process_skills(
        self,
        model: str,
        skills: Union[str, List[str]],
        adhoc_skill: str,
        num_questions: int,
        yoe: Union[str, int],
    ) -> Optional[List[str]]:
        """
        Generates interview questions based on provided skills and experience.

        Args:
            model: name of model to be used
            skills: Skills string or list of skills
            adhoc_skill: Skill entered by the user
            num_questions: Number of questions to generate (1-10)
            yoe: Years of experience (string or integer)

        Returns:
            List of generated questions or None if error occurs

        Raises:

            ResumeParsingError: If invalid input parameters or processing fails
        """
        try:
            # Input validation
            if not model:
                model = "hermes-3-llama-3.1-8b"
            else:
                model = MODEL_MAP.get(model, "hermes-3-llama-3.1-8b")

            if not skills:
                raise ResumeParsingError(
                    message="Skills cannot be empty",
                    code=3001,
                    details={"skills": skills},
                )

            if isinstance(skills, str):
                skills = [skill.strip() for skill in skills.split(",")]

            if not isinstance(num_questions, int) or not 1 <= num_questions <= 10:
                raise ResumeParsingError(
                    message="Number of questions must be between 1 and 10",
                    code=3002,
                    details={"num_questions": num_questions},
                )

            def convert_yoe_to_int(yoe_str: str) -> int:
                """
                Convert years of experience string to integer value, rounding up partial years.

                Args:
                    yoe_str: Years of experience as string

                Returns:
                    Integer value representing total years of experience
                """
                # Check for years and months format
                match = re.match(r"(\d+)\s*years?\s*(\d*)\s*months?", yoe_str)
                if match:
                    years = int(match.group(1))
                    months = int(match.group(2)) if match.group(2) else 0
                    return years + (1 if months > 0 else 0)

                # Check for only years format
                match = re.match(r"(\d+)\s*years?", yoe_str)
                if match:
                    return int(match.group(1))

                # Check for only months format
                match = re.match(r"(\d+)\s*months?", yoe_str)
                if match:
                    return 1 if int(match.group(1)) > 0 else 0

                raise ResumeParsingError(
                    message="Invalid format for years of experience",
                    code=3002,
                    details={"yoe": yoe_str},
                )

            print(f"yoe {yoe}")
            # Convert yoe to int if string
            if isinstance(yoe, str):
                yoe = convert_yoe_to_int(yoe)

            if not 0 <= yoe <= 50:
                raise ResumeParsingError(
                    message="Years of experience must be between 0 and 50",
                    code=3003,
                    details={"yoe": yoe},
                )

            # Generate questions
            questions = main_parser_obj.generate_questions_for_skills(
                model, skills, adhoc_skill, num_questions, yoe
            )

            if not questions:
                raise ResumeParsingError(
                    message="No questions generated for given skills",
                    code=3004,
                    details={"skills": skills, "num_questions": num_questions},
                )

            return self._format_questions(questions, num_questions)

        except ResumeParsingError as e:
            logger.error(str(e))
            return None
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            raise ResumeParsingError(
                message="Failed to generate interview questions",
                code=3005,
                details={"error": str(e)},
            )
