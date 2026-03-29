# backend/tests/test_routes.py
import pytest
from unittest.mock import patch
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.models import StockVideo, StockMention


def _add_video(connection, video_id="v1", channel_name="GODofIT",
               channel_url="https://www.youtube.com/@GODofIT",
               title="테스트 영상", title_ko="테스트 영상 한글", summary="요약"):
    db = Session(bind=connection)
    video = StockVideo(
        channel_url=channel_url,
        channel_name=channel_name,
        video_id=video_id,
        video_title=title,
        video_title_ko=title_ko,
        published_at=datetime(2026, 3, 23, 0, 0, 0),
        summary=summary,
    )
    db.add(video)
    db.flush()
    db.add(StockMention(
        stock_video_id=video.id,
        stock_name="삼성전자",
        sentiment="positive",
        opinion="실적 기대",
    ))
    db.commit()
    db.close()


def test_get_feed_empty(client, tmp_path, monkeypatch):
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "channels.json"))
    (tmp_path / "channels.json").write_text('[]')
    resp = client.get("/api/feed")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_feed_with_channels(client, db_engine, tmp_path, monkeypatch):
    _, connection = db_engine
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "channels.json"))
    (tmp_path / "channels.json").write_text('[{"url": "https://www.youtube.com/@GODofIT", "name": "GODofIT"}]')
    _add_video(connection)

    resp = client.get("/api/feed")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["channel_name"] == "GODofIT"
    assert data[0]["video_count"] == 1
    assert data[0]["latest_video_title"] == "테스트 영상"
    assert data[0]["latest_video_title_ko"] == "테스트 영상 한글"


def test_get_feed_channel_detail(client, db_engine):
    _, connection = db_engine
    _add_video(connection)

    resp = client.get("/api/feed/detail?url=https://www.youtube.com/@GODofIT")
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel_name"] == "GODofIT"
    assert len(data["videos"]) == 1
    video = data["videos"][0]
    assert video["title"] == "테스트 영상"
    assert video["title_ko"] == "테스트 영상 한글"
    assert video["summary"] == "요약"
    assert "analyzed_at" in video
    assert "published_at" in video
    assert len(video["stocks"]) == 1
    assert video["stocks"][0]["name"] == "삼성전자"
    assert video["stocks"][0]["sentiment"] == "positive"


def test_get_feed_channel_not_found(client):
    resp = client.get("/api/feed/detail?url=https://www.youtube.com/@UnknownChannel")
    assert resp.status_code == 200
    data = resp.json()
    assert data["videos"] == []


def test_get_feed_invalid_channels_json(client, tmp_path, monkeypatch):
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "channels.json"))
    (tmp_path / "channels.json").write_text("not valid json")
    resp = client.get("/api/feed")
    assert resp.status_code == 500


def test_post_refresh(client, tmp_path, monkeypatch):
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "channels.json"))
    (tmp_path / "channels.json").write_text('[]')
    with patch("backend.api.routes.run_fetch_job"):
        resp = client.post("/api/refresh")
    assert resp.status_code == 202
    assert resp.json()["status"] == "refresh started"
