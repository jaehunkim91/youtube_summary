# backend/api/schemas.py
from typing import Optional
from pydantic import BaseModel


class StockMentionResponse(BaseModel):
    name: str
    sentiment: str
    opinion: str


class VideoResponse(BaseModel):
    video_id: str
    title: str
    published_at: str  # ISO 8601 UTC string — always constructed manually, not from ORM
    summary: Optional[str]
    stocks: list[StockMentionResponse]


class ChannelFeedItem(BaseModel):
    channel_name: str
    channel_url: str
    video_count: int
    latest_video_title: Optional[str]
    latest_video_at: Optional[str]  # ISO 8601 UTC string


class ChannelDetailResponse(BaseModel):
    channel_name: str
    channel_url: Optional[str]
    videos: list[VideoResponse]


class RefreshResponse(BaseModel):
    status: str
