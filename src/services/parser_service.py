# standard library imports
import os, logging

# third party imports
from fastapi import UploadFile, HTTPException
from fastapi.responses import JSONResponse

# local imports
from src.services.parser.resume_reader import ResumeReader
from src.services.parser.section_extractor import SectionExtractor
from src.services.parser.entity_extractor import EntityExtractor
from src.services.parser.questions_generator import QuestionGenerator
from src.services.analyzer.resume_analyzer import ResumeAnalyzer
from src.schemas.parser import SkillsRequest
from configs.config import APP_CONFIG, MODEL_MAP
from utils.file_utils import save_upload_file
from utils.html_utils import sanitize_html_content
from utils.logging_config import configure_logging
from utils.constants import ERROR_MESSAGES
from utils.pre_processing import clean_text_md

configure_logging()
logger = logging.getLogger(__name__)


class ParserService:
    """Service class for handling resume parsing and question generation."""

    def __init__(self):
        """Initialize parser service with required components."""
        try:
            self.resume_reader = ResumeReader()
            self.section_extractor = SectionExtractor()
            self.entity_extractor = EntityExtractor()
            self.question_generator = QuestionGenerator()
            self.resume_analyzer = ResumeAnalyzer()
            self.temp_dir = APP_CONFIG["TEMP_DIR"]
            self.output_type = APP_CONFIG["OUTPUT_TYPE"]
        except Exception as e:
            logger.error(f"Failed to initialize ParserService: {e}")
            raise HTTPException(
                status_code=500,
                detail=ERROR_MESSAGES["SERVICE_INIT_ERROR"].format(str(e)),
            )

    async def parse_resume(self, file: UploadFile, model: str) -> JSONResponse:
        """
        Process resume file and extract information.

        Args:
            model (str): name of model to use
            file (UploadFile): Resume file to process

        Returns:
            JSONResponse: Parsed resume data and issues

        Raises:
            HTTPException: For various processing errors
        """

        try:
            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail=ERROR_MESSAGES["PDF_ONLY"])

            # fetch the model name from the mapping
            model = MODEL_MAP.get(model, "hermes-3-llama-3.1-8b")

            # Save and read file
            try:
                pdf_path = await save_upload_file(file)
                md_text, plain_text = self.resume_reader.read_resume(
                    pdf_path, self.output_type
                )
                text = md_text
                # logger.info(f"\n 1 MD TEXT EXTRACTED FROM RESUME {text}")
                # logger.info(f"\n 1 PLAIN TEXT EXTRACTED FROM RESUME {plain_text}")
                text, plain_text = clean_text_md(text), clean_text_md(plain_text)
                logger.info(f"\n 2 MD TEXT EXTRACTED FROM RESUME {text}")
                logger.info(f"\n 2 PLAIN TEXT EXTRACTED FROM RESUME {plain_text}")

                if not text:
                    raise ValueError(ERROR_MESSAGES["EMPTY_TEXT"])

                # save the text to a file
                raw_path = os.path.join(APP_CONFIG["TEMP_DIR"], "raw_text.txt")
                try:
                    with open(raw_path, "w", encoding="utf-8") as f:
                        f.write(text)
                except Exception as e:
                    raise IOError(ERROR_MESSAGES["RAW_TEXT_SAVE_ERROR"].format(str(e)))
            except Exception as e:
                logger.error(f"File processing error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=ERROR_MESSAGES["FILE_READ_ERROR"].format(str(e)),
                )

            # Extract sections and entities
            try:
                sections = self.section_extractor.fetch_sections(text, model)
                if not sections:
                    raise ValueError(
                        ERROR_MESSAGES["EMPTY_SECTION_ERROR"].format(
                            "No sections found"
                        )
                    )
                logger.info(f"\n2. Section data extracted {sections}")

                html_table = self.entity_extractor.extract_entities(sections)
                logger.info(f"\n3. HTML extract entites data extracted {html_table}")
                if not html_table:
                    raise ValueError(ERROR_MESSAGES["ENTITIES_EXTRACTION_ERROR"])
                elif not isinstance(html_table, str):
                    ValueError(ERROR_MESSAGES["INCORRECT_FORMAT"])
            except ValueError as e:
                logger.error(f"Section processing error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=ERROR_MESSAGES["SECTION_PROCESSING_ERROR"].format(str(e)),
                )
            except Exception as e:
                logger.error(f"Parsing error: {e}")
                raise HTTPException(
                    status_code=500, detail=ERROR_MESSAGES["PARSE_ERROR"].format(str(e))
                )

            # Process and sanitize output
            try:
                html_table = sanitize_html_content(html_table)
                logger.info(f"\n4. SANTIZIED HTML {html_table}")

                issue_checker_output = self.resume_analyzer.analyze_resume(
                    plain_text, model
                )
                logger.info(f"\n5. ISSUE CHECKER OUTPUT {issue_checker_output}")

            except Exception as e:
                logger.error(f"Spell check output error {e}")
                raise HTTPException(
                    status_code=500,
                    detail=ERROR_MESSAGES["SANITIZATION_ERROR"].format(str(e)),
                )

            return JSONResponse(
                content={
                    "result_table": html_table,
                    "issue_table": issue_checker_output,
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Resume parsing error: {e}")
            raise HTTPException(
                status_code=500,
                detail=ERROR_MESSAGES["UNEXPECTED_ERROR"].format(str(e)),
            )

    async def generate_questions(self, skills_data: SkillsRequest) -> JSONResponse:
        """
        Generate interview questions based on skills.

        Args:
            skills_data (SkillsRequest): Skills and experience data

        Returns:
            JSONResponse: Generated questions

        Raises:
            HTTPException: If question generation fails
        """
        try:
            questions = self.question_generator.process_skills(
                skills_data.model,
                skills_data.skills,
                skills_data.adhoc_skill,
                skills_data.num_questions,
                skills_data.yoe,
            )
            if not questions:
                raise ValueError(
                    status_code=500,
                    detail=ERROR_MESSAGES["QUESTION_GENERATION_ERROR"].format(
                        "No questions generated"
                    ),
                )
            return JSONResponse(content={"questions": questions})
        except ValueError as e:
            logger.error(f"Question generation validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate questions")
