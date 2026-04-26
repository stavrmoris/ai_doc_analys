from typing import Literal

from pydantic import BaseModel, Field


SummaryMode = Literal["short", "detailed"]


class SummaryRequest(BaseModel):
    doc_id: int = Field(ge=1)
    mode: SummaryMode = "short"


class SummaryResponse(BaseModel):
    summary: str
