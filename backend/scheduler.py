# backend/scheduler.py
import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_fetch_job():
    """Fetch recent videos from all channels and analyze them."""
    from datetime import datetime, timezone
    from backend.db.database import SessionLocal
    from backend.db.models import StockVideo, StockMention
    from backend.services.channel import fetch_recent_videos, load_channels, parse_channel_name, ChannelFetchError, get_video_duration
    from backend.services.transcript import get_transcript
    from backend.services.stock_analyzer import analyze_video, StockAnalyzerError
    from sqlalchemy.exc import IntegrityError

    try:
        channels = load_channels()
    except Exception as e:
        logger.warning(f"channels.json 읽기 실패: {e}")
        return

    if not channels:
        logger.info("채널 목록이 비어 있습니다.")
        return

    db = SessionLocal()
    try:
        for entry in channels:
            channel_url = entry["url"]
            channel_name = entry["name"]
            try:
                videos = fetch_recent_videos(channel_url)
            except ChannelFetchError as e:
                logger.warning(f"채널 조회 실패 {channel_url}: {e}")
                continue

            for video in videos:
                # Skip if already analyzed
                existing = db.query(StockVideo).filter(StockVideo.video_id == video.video_id).first()
                if existing:
                    continue

                duration = get_video_duration(video.video_id)
                if duration is not None and (duration <= 60 or duration > 1800):
                    logger.info(f"영상 길이 필터링 스킵: {video.title} ({duration}초)")
                    continue

                try:
                    transcript = get_transcript(video.video_id)
                except Exception as e:
                    logger.warning(f"자막 추출 실패 {video.video_id}: {e}")
                    continue

                try:
                    result = analyze_video(transcript.text, video.title)
                except StockAnalyzerError as e:
                    logger.warning(f"분석 실패 {video.video_id}: {e}")
                    continue

                stock_video = StockVideo(
                    channel_url=channel_url,
                    channel_name=channel_name,
                    video_id=video.video_id,
                    video_title=video.title,
                    video_title_ko=result.title_ko or None,
                    published_at=video.published_at or datetime.now(timezone.utc).replace(tzinfo=None),
                    summary=result.summary,
                )
                db.add(stock_video)
                try:
                    db.flush()
                except IntegrityError:
                    db.rollback()
                    logger.info(f"중복 영상 스킵: {video.video_id}")
                    continue

                for stock in result.stocks:
                    db.add(StockMention(
                        stock_video_id=stock_video.id,
                        stock_name=stock.name,
                        sentiment=stock.sentiment,
                        opinion=stock.opinion,
                    ))

                db.commit()
                logger.info(f"분석 완료: {video.title} ({video.video_id})")
                time.sleep(3)  # YouTube rate limit 방지
    finally:
        db.close()


# .venv/bin/python -c "from backend.scheduler import run_fetch_job; run_fetch_job()"