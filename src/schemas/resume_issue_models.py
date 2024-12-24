from typing import List
from pydantic import BaseModel, Field


class SpellingCorrection(BaseModel):
    """Model for spelling correction data."""

    incorrect_word: str
    correct_word: str


class IssueCheckResult(BaseModel):
    """Model for overall issue check results."""

    missing_sections: List[str] = Field(default_factory=list)
    spelling_corrections: List[SpellingCorrection] = Field(default_factory=list)
