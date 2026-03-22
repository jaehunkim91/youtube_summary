import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.db.models import Base, Summary, Chapter

def test_create_summary_and_chapters():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        summary = Summary(
            youtube_url="https://youtube.com/watch?v=abc123",
            video_title="Test Video",
            video_id="abc123",
        )
        session.add(summary)
        session.flush()
        chapter = Chapter(
            summary_id=summary.id,
            title="Intro",
            timestamp="00:00",
            content="Introduction content",
            order=0,
        )
        session.add(chapter)
        session.commit()
        assert summary.id is not None
        assert len(summary.chapters) == 1
        assert summary.chapters[0].title == "Intro"

def test_unique_youtube_url():
    from sqlalchemy.exc import IntegrityError
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        s1 = Summary(youtube_url="https://youtube.com/watch?v=abc", video_title="T", video_id="abc")
        s2 = Summary(youtube_url="https://youtube.com/watch?v=abc", video_title="T", video_id="abc")
        session.add(s1)
        session.flush()
        session.add(s2)
        with pytest.raises(IntegrityError):
            session.flush()
