from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: int
    filename: str
    file_type: str
    storage_path: str
    upload_time: datetime
    language: str | None = None
    pages_count: int | None = None
    status: str
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True)
