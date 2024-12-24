from typing import Optional

from pydantic import BaseModel
from fastapi import UploadFile


class ParseRequest(BaseModel):
    """Schema for resume parsing request."""

    model: str
    file: UploadFile


class SkillsRequest(BaseModel):
    """Schema for skills-based question generation request."""

    model: str
    skills: str
    adhoc_skill: str
    num_questions: int = 1
    yoe: Optional[str] = "5 years"


class ParseResponse(BaseModel):
    """Schema for resume parsing response."""

    result_table: str
    issue_table: str
