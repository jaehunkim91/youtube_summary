# backend/tests/test_db.py
import pytest
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from backend.db.models import StockVideo, StockMention


def test_stock_video_create(db_engine):
    _, connection = db_engine
    Session = sessionmaker(bind=connection)
    db = Session()

    video = StockVideo(
        channel_url="https://www.youtube.com/@GODofIT",
        channel_name="GODofIT",
        video_id="abc123",
        video_title="테스트 영상",
        published_at=datetime(2026, 3, 23, 0, 0, 0),
        summary="테스트 요약",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    assert video.id is not None
    assert video.created_at is not None
    assert video.mentions == []
    db.close()


def test_stock_mention_cascade_delete(db_engine):
    _, connection = db_engine
    Session = sessionmaker(bind=connection)
    db = Session()

    video = StockVideo(
        channel_url="https://www.youtube.com/@GODofIT",
        channel_name="GODofIT",
        video_id="xyz789",
        video_title="테스트 영상2",
        published_at=datetime(2026, 3, 23, 0, 0, 0),
    )
    db.add(video)
    db.flush()

    mention = StockMention(
        stock_video_id=video.id,
        stock_name="삼성전자",
        sentiment="positive",
        opinion="실적 기대",
    )
    db.add(mention)
    db.commit()

    db.delete(video)
    db.commit()

    assert db.query(StockMention).count() == 0
    db.close()


def test_video_id_unique_constraint(db_engine):
    _, connection = db_engine
    Session = sessionmaker(bind=connection)
    db = Session()
    from sqlalchemy.exc import IntegrityError

    video1 = StockVideo(
        channel_url="https://www.youtube.com/@GODofIT",
        channel_name="GODofIT",
        video_id="dup001",
        video_title="영상1",
        published_at=datetime(2026, 3, 23),
    )
    db.add(video1)
    db.commit()

    video2 = StockVideo(
        channel_url="https://www.youtube.com/@GODofIT",
        channel_name="GODofIT",
        video_id="dup001",  # same video_id
        video_title="영상1-dup",
        published_at=datetime(2026, 3, 23),
    )
    db.add(video2)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
    db.close()
