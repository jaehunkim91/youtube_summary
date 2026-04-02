# backend/api/routes.py
import json
import logging
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.db.database import get_db
from backend.db.models import StockVideo, StockMention, ChannelRequest
from backend.api.schemas import (
    ChannelFeedItem,
    ChannelDetailResponse,
    VideoResponse,
    StockMentionResponse,
    RefreshResponse,
    StockFeedItem,
    StockDetailResponse,
    StockOpinionItem,
    ChannelRequestCreate,
    ChannelRequestResponse,
)
from backend.services.channel import load_channels
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
    for entry in channels:
        channel_url = entry["url"]
        channel_name = entry["name"]

        latest = (
            db.query(StockVideo)
            .filter(StockVideo.channel_url == channel_url)
            .order_by(StockVideo.published_at.desc())
            .first()
        )
        count = (
            db.query(func.count(StockVideo.id))
            .filter(StockVideo.channel_url == channel_url)
            .scalar()
        )

        result.append(ChannelFeedItem(
            channel_name=channel_name,
            channel_url=channel_url,
            video_count=count or 0,
            latest_video_title=latest.video_title if latest else None,
            latest_video_title_ko=latest.video_title_ko if latest else None,
            latest_video_at=_dt_to_str(latest.published_at) if latest else None,
        ))

    return result


@router.get("/feed/detail", response_model=ChannelDetailResponse)
def get_channel_feed(url: str = Query(...), db: Session = Depends(get_db)):
    videos = (
        db.query(StockVideo)
        .filter(StockVideo.channel_url == url)
        .order_by(StockVideo.published_at.desc())
        .limit(50)
        .all()
    )

    channel_url = videos[0].channel_url if videos else url
    actual_name = videos[0].channel_name if videos else url

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
            title_ko=v.video_title_ko,
            published_at=_dt_to_str(v.published_at),
            analyzed_at=_dt_to_str(v.created_at),
            summary=v.summary,
            stocks=stocks,
        ))

    return ChannelDetailResponse(
        channel_name=actual_name,
        channel_url=channel_url,
        videos=video_responses,
    )


@router.get("/stocks", response_model=list[StockFeedItem])
def get_stocks(db: Session = Depends(get_db)):
    rows = (
        db.query(
            StockMention.stock_name,
            func.count(StockMention.id).label("mention_count"),
            func.max(StockVideo.published_at).label("latest_mentioned_at"),
        )
        .join(StockVideo, StockMention.stock_video_id == StockVideo.id)
        .group_by(StockMention.stock_name)
        .order_by(func.count(StockMention.id).desc())
        .all()
    )
    return [
        StockFeedItem(
            name=r.stock_name,
            mention_count=r.mention_count,
            latest_mentioned_at=_dt_to_str(r.latest_mentioned_at),
        )
        for r in rows
    ]


@router.get("/stocks/detail", response_model=StockDetailResponse)
def get_stock_detail(name: str = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.query(StockMention, StockVideo)
        .join(StockVideo, StockMention.stock_video_id == StockVideo.id)
        .filter(StockMention.stock_name == name)
        .order_by(StockVideo.published_at.desc())
        .all()
    )
    opinions = [
        StockOpinionItem(
            channel_name=video.channel_name,
            sentiment=mention.sentiment,
            opinion=mention.opinion,
            video_title=video.video_title,
            video_title_ko=video.video_title_ko,
            published_at=_dt_to_str(video.published_at),
        )
        for mention, video in rows
    ]
    return StockDetailResponse(stock_name=name, opinions=opinions)


@router.post("/refresh", status_code=202, response_model=RefreshResponse)
def refresh(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fetch_job)
    return RefreshResponse(status="refresh started")


@router.post("/channel-requests", status_code=201, response_model=ChannelRequestResponse)
def create_channel_request(body: ChannelRequestCreate, db: Session = Depends(get_db)):
    req = ChannelRequest(
        nickname=body.nickname.strip(),
        channel_name=body.channel_name.strip(),
        content=body.content.strip() if body.content else None,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return ChannelRequestResponse(
        id=req.id,
        nickname=req.nickname,
        channel_name=req.channel_name,
        content=req.content,
        created_at=_dt_to_str(req.created_at),
    )


@router.get("/channel-requests", response_model=list[ChannelRequestResponse])
def list_channel_requests(db: Session = Depends(get_db)):
    rows = (
        db.query(ChannelRequest)
        .order_by(ChannelRequest.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        ChannelRequestResponse(
            id=r.id,
            nickname=r.nickname,
            channel_name=r.channel_name,
            content=r.content,
            created_at=_dt_to_str(r.created_at),
        )
        for r in rows
    ]
