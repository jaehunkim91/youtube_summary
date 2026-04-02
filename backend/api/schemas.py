# backend/api/schemas.py
from typing import Optional
from pydantic import BaseModel, field_validator


class StockMentionResponse(BaseModel):
    name: str
    sentiment: str
    opinion: str


class VideoResponse(BaseModel):
    video_id: str
    title: str
    title_ko: Optional[str]
    published_at: str   # 업로드 시각 (ISO 8601 UTC)
    analyzed_at: str    # 분석 완료 시각 (ISO 8601 UTC)
    summary: Optional[str]
    stocks: list[StockMentionResponse]


class ChannelFeedItem(BaseModel):
    channel_name: str
    channel_url: str
    video_count: int
    latest_video_title: Optional[str]
    latest_video_title_ko: Optional[str]
    latest_video_at: Optional[str]  # ISO 8601 UTC string


class ChannelDetailResponse(BaseModel):
    channel_name: str
    channel_url: Optional[str]
    videos: list[VideoResponse]


class RefreshResponse(BaseModel):
    status: str


class StockFeedItem(BaseModel):
    name: str
    mention_count: int
    latest_mentioned_at: Optional[str]


class StockOpinionItem(BaseModel):
    channel_name: str
    sentiment: str
    opinion: str
    video_title: str
    video_title_ko: Optional[str]
    published_at: str


class StockDetailResponse(BaseModel):
    stock_name: str
    opinions: list[StockOpinionItem]


class ChannelRequestCreate(BaseModel):
    nickname: str
    channel_name: str
    content: Optional[str] = None

    @field_validator('nickname', 'channel_name')
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('공백만 입력할 수 없습니다')
        return v


class ChannelRequestResponse(BaseModel):
    id: int
    nickname: str
    channel_name: str
    content: Optional[str]
    created_at: str
