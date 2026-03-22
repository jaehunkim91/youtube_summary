# backend/api/schemas.py
import re
from datetime import datetime
from pydantic import BaseModel, field_validator

YOUTUBE_URL_RE = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?.*v=|youtu\.be/)[\w-]+"
)

class SummarizeRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_youtube_url(cls, v: str) -> str:
        if not YOUTUBE_URL_RE.search(v):
            raise ValueError("유효한 YouTube URL이 아닙니다")
        return v

class ChapterResponse(BaseModel):
    id: int
    title: str
    timestamp: str
    content: str
    order: int

    model_config = {"from_attributes": True}

class SummaryResponse(BaseModel):
    id: int
    video_title: str
    video_id: str
    youtube_url: str
    created_at: datetime
    chapters: list[ChapterResponse]

    model_config = {"from_attributes": True}

class HistoryItemResponse(BaseModel):
    id: int
    video_title: str
    video_id: str
    youtube_url: str
    created_at: datetime
    chapter_count: int

    model_config = {"from_attributes": True}
