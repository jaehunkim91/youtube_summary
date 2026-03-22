# backend/scheduler.py
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_fetch_job():
    """Fetch recent videos from all channels and analyze them."""
    from backend.db.database import SessionLocal
    from backend.db.models import StockVideo, StockMention
    from backend.services.channel import fetch_recent_videos, load_channels, parse_channel_name, ChannelFetchError
    from backend.services.transcript import get_transcript, TranscriptUnavailableError
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
        for channel_url in channels:
            channel_name = parse_channel_name(channel_url)
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

                try:
                    transcript = get_transcript(video.video_id)
                except (TranscriptUnavailableError, Exception) as e:
                    logger.warning(f"자막 추출 실패 {video.video_id}: {e}")
                    continue

                try:
                    result = analyze_video(transcript.text)
                except StockAnalyzerError as e:
                    logger.warning(f"분석 실패 {video.video_id}: {e}")
                    continue

                stock_video = StockVideo(
                    channel_url=channel_url,
                    channel_name=channel_name,
                    video_id=video.video_id,
                    video_title=video.title,
                    published_at=video.published_at,
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
    finally:
        db.close()
