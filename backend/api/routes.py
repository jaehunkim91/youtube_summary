# backend/api/routes.py
import json
import logging
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.database import get_db
from backend.db.models import StockVideo
from backend.api.schemas import (
    ChannelFeedItem,
    ChannelDetailResponse,
    VideoResponse,
    StockMentionResponse,
    RefreshResponse,
)
from backend.services.channel import load_channels, parse_channel_name
from backend.scheduler import run_fetch_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


def _dt_to_str(dt) -> Optional[str]:
    """Convert naive UTC datetime to ISO 8601 string with Z suffix."""
    return dt.isoformat() + "Z" if dt else None


@router.get("/feed", response_model=list[ChannelFeedItem])
def get_feed(db: Session = Depends(get_db)):
    try:
        channels = load_channels()
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"channels.json 파싱 실패: {e}")
    except Exception:
        channels = []

    result = []
    for channel_url in channels:
        channel_name = parse_channel_name(channel_url)

        latest = (
            db.query(StockVideo)
            .filter(func.lower(StockVideo.channel_name) == channel_name.lower())
            .order_by(StockVideo.published_at.desc())
            .first()
        )
        count = (
            db.query(func.count(StockVideo.id))
            .filter(func.lower(StockVideo.channel_name) == channel_name.lower())
            .scalar()
        )

        result.append(ChannelFeedItem(
            channel_name=channel_name,
            channel_url=channel_url,
            video_count=count or 0,
            latest_video_title=latest.video_title if latest else None,
            latest_video_at=_dt_to_str(latest.published_at) if latest else None,
        ))

    return result


@router.get("/feed/{channel_name}", response_model=ChannelDetailResponse)
def get_channel_feed(channel_name: str, db: Session = Depends(get_db)):
    videos = (
        db.query(StockVideo)
        .filter(func.lower(StockVideo.channel_name) == channel_name.lower())
        .order_by(StockVideo.published_at.desc())
        .limit(50)
        .all()
    )

    channel_url = videos[0].channel_url if videos else None
    actual_name = videos[0].channel_name if videos else channel_name

    video_responses = []
    for v in videos:
        stocks = [
            StockMentionResponse(
                name=m.stock_name,
                sentiment=m.sentiment,
                opinion=m.opinion,
            )
            for m in v.mentions
        ]
        video_responses.append(VideoResponse(
            video_id=v.video_id,
            title=v.video_title,
            published_at=_dt_to_str(v.published_at),
            summary=v.summary,
            stocks=stocks,
        ))

    return ChannelDetailResponse(
        channel_name=actual_name,
        channel_url=channel_url,
        videos=video_responses,
    )


@router.post("/refresh", status_code=202, response_model=RefreshResponse)
def refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch_job)
    return RefreshResponse(status="refresh started")
