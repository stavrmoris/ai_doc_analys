from pydantic import BaseModel, ConfigDict, Field


class QARequest(BaseModel):
    question: str = Field(min_length=1)
    doc_id: int | None = Field(default=None, ge=1)


class Citation(BaseModel):
    doc_id: int
    page: int | None = None
    text: str

    model_config = ConfigDict(from_attributes=True)


class QAResponse(BaseModel):
    answer: str
    citations: list[Citation]
