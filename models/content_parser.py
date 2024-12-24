# Standard library
import json
import logging
from typing import Dict, Any, List

# Local imports
from utils.logging_config import configure_logging
from utils import prompts
from models.base_config import BaseParser

# remove
import os
from dotenv import load_dotenv

load_dotenv()
HFAPI_KEY = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


class ResumeDataParser(BaseParser):
    """Handles resume parsing and data extraction"""

    def get_sections(self, html_text: str, model: str) -> Dict[str, Any]:
        """Extract sections from resume HTML text"""
        if not html_text:
            raise ValueError("HTML text cannot be empty")

        generated_text = self.llm_client.get_completion(
            model,
            prompts.PROMPT_TEXT_SECTIONS + str(prompts.MAIN_SECTIONS),
            prompts.USER_PROMPT_SECTIONS,
            html_text,
        )

        logger.info(
            f"\n1.1 LLM output for getting sections {generated_text} and its type {type(generated_text)}"
        )
        return self._process_json_response(generated_text)

    # def get_sections(self, html_text: str) -> Dict[str, Any]:
    #     from huggingface_hub import InferenceClient

    #     logger.info('INPUT TEXT ', html_text)
    #     client = InferenceClient(token=HFAPI_KEY)

    #     messages = [
    #                 {"role": "system", "content":constants.PROMPT_TEXT_SECTIONS + str(constants.MAIN_SECTIONS)},
    #                 {"role": "user", "content": constants.USER_PROMPT_SECTIONS + html_text},
    #             ]

    #     # Make API call
    #     response = client.text_generation(
    #         #model="NousResearch/Hermes-3-Llama-3.1-8B",
    #         #model="NousResearch/Hermes-3-Llama-3.1-70B-FP8",
    #         #model="meta-llama/Llama-3.2-3B-Instruct",
    #         model="mistralai/Ministral-8B-Instruct-2410",
    #         prompt=str(messages),
    #         max_new_tokens= 1500,
    #         temperature= 0.1,
    #         return_full_text= False,
    #         stop=["<|endoftext|>", "respond;"],
    #         repetition_penalty=1.2
    #     )

    #     #logger.info('generated text by model RAW %s', response)

    #     # Process the response
    #     try:
    #         generated_text = response
    #         logger.info('generated text by model %s', generated_text)
    #         return self._process_json_response(generated_text)
    #     except Exception as e:
    #         logger.error('Error processing response: %s', str(e))
    #         return {}

    def generate_questions_for_skills(
        self,
        model: str,
        skills: List[str],
        adhoc_skill: str,
        num_questions: int,
        yoe: int,
    ) -> str:
        """Generate interview questions based on skills"""
        try:
            if not skills:
                raise ValueError("Skills list cannot be empty")

            skillset = ", ".join(skills)

            logger.info(f"The adhoc skill requested is {adhoc_skill}")
            UPDATED_PROMPT_TEXT_FOR_QUE = prompts.PROMPT_TEXT_FOR_QUE.format(
                que_count=num_questions
            )
            UPDATED_PROMPT_TEXT_FOR_QUE_ADHOC_SKILL = (
                prompts.PROMPT_TEXT_FOR_QUE_ADHOC_SKILL.format(que_count=num_questions)
            )

            if not adhoc_skill:
                prompt = (
                    f"{UPDATED_PROMPT_TEXT_FOR_QUE}{num_questions} questions. "
                    f"Interviewee has {yoe} years of experience."
                )

                return self.llm_client.get_completion(
                    model, prompt, prompts.USER_PROMPT_FOR_QUE, skillset
                ).replace("-", "")
            else:
                prompt = (
                    f"{UPDATED_PROMPT_TEXT_FOR_QUE_ADHOC_SKILL}{num_questions} questions. "
                    f"Interviewee has {yoe} years of experience."
                )

                return self.llm_client.get_completion(
                    model, prompt, prompts.USER_PROMPT_FOR_QUE_ADHOC_SKILL, adhoc_skill
                ).replace("-", "")
        except Exception as e:
            logger.error(f"Error generating questions for skills: {e}")
            return None
