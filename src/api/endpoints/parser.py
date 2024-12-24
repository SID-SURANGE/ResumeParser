# Standard library imports
import logging
from typing import Dict

# Third party imports
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse

# Local imports
from src.services.parser_service import ParserService
from src.schemas.parser import SkillsRequest, ParseResponse
from utils.logging_config import configure_logging
from utils.constants import ERROR_MESSAGES

# Create a router for the parser endpoints
router = APIRouter(tags=["Parser"])

configure_logging()
logger = logging.getLogger(__name__)

# Create an instance of the parser service
parser_service = ParserService()


@router.post("/parse", response_model=ParseResponse)
async def resume_parser(
    file: UploadFile = File(...), model: str = Form(...)
) -> JSONResponse:
    """
    Parse a resume PDF file and extract structured information.

    Args:
        file (UploadFile): PDF resume file to be parsed
        model (str): name of model

    Returns:
        JSONResponse: Contains parsed resume data and issue analysis
            - result_table: HTML formatted resume sections
            - issue_table: Spelling issues found

    Raises:
        HTTPException:
            - 400: If file is not PDF format
            - 500: If parsing or processing fails
    """
    try:
        print(f"file {file}, model {model}")
        return await parser_service.parse_resume(file=file, model=model)
    except HTTPException as he:
        logger.error(f"HTTP Exception during parsing: {he.detail}")
        raise HTTPException(status_code=he.status_code, detail=he.detail)
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=400, detail=ERROR_MESSAGES["PARSE_ERROR"].format(str(ve))
        )
    except Exception as e:
        logger.error(f"Resume parsing error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ERROR_MESSAGES["UNEXPECTED_ERROR"].format(str(e))
        )


@router.post("/questions", response_model=Dict[str, list])
async def get_questions(skills_data: SkillsRequest) -> JSONResponse:
    """
    Generate interview questions based on skills and experience.

    Args:
        skills_data (SkillsRequest): Contains:
            - model: name of model to be used
            - skills: List of technical skills
            - num_questions: Number of questions to generate
            - yoe: Years of experience

    Returns:
        JSONResponse: Contains generated interview questions
            - questions: List of generated questions

    Raises:
        HTTPException:
            - 500: If question generation fails
    """
    try:
        return await parser_service.generate_questions(skills_data)
    except ValueError as ve:
        logger.error(f"Validation error in question generation: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=ERROR_MESSAGES["QUESTION_GENERATION_ERROR"].format(str(ve)),
        )
    except HTTPException as he:
        logger.error(f"HTTP Exception in question generation: {he.detail}")
        raise HTTPException(status_code=he.status_code, detail=he.detail)
    except Exception as e:
        logger.error(f"Question generation error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=ERROR_MESSAGES["UNEXPECTED_ERROR"].format(str(e))
        )
