from typing import List

from pydantic import BaseModel, Field


class PromptQueryRequest(BaseModel):
    natural_language: str = Field(
        ..., min_length=5, description="Human readable question, e.g. 'Show total sales by month'"
    )


class PromptQueryResponse(BaseModel):
    sql: str
    columns: List[str]
    rows: List[List[str]]
    notes: str
