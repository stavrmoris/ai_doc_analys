from pydantic import BaseModel, ConfigDict, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50)
    doc_id: int | None = Field(default=None, ge=1)


class SearchResult(BaseModel):
    doc_id: int
    page_num: int | None = None
    section_title: str | None = None
    text: str
    score: float

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    results: list[SearchResult]
