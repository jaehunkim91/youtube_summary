# backend/tests/test_channel.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.services.channel import (
    fetch_recent_videos,
    load_channels,
    parse_channel_name,
    ChannelFetchError,
    VideoInfo,
)


def _mock_run(stdout="", returncode=0, stderr=""):
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    m.stderr = stderr
    return m


def test_fetch_recent_videos_success():
    stdout = "abc123\t오늘 장 분석\t20260323\nxyz789\t주목 종목\t20260322\n"
    with patch("backend.services.channel.subprocess.run", return_value=_mock_run(stdout=stdout)):
        videos = fetch_recent_videos("https://www.youtube.com/@GODofIT")
    assert len(videos) == 2
    assert videos[0].video_id == "abc123"
    assert videos[0].title == "오늘 장 분석"
    assert videos[0].published_at == datetime(2026, 3, 23)


def test_fetch_recent_videos_empty():
    with patch("backend.services.channel.subprocess.run", return_value=_mock_run(stdout="")):
        videos = fetch_recent_videos("https://www.youtube.com/@GODofIT")
    assert videos == []


def test_fetch_recent_videos_failure():
    with patch("backend.services.channel.subprocess.run", return_value=_mock_run(returncode=1, stderr="yt-dlp error")):
        with pytest.raises(ChannelFetchError):
            fetch_recent_videos("https://www.youtube.com/@GODofIT")


def test_parse_channel_name():
    assert parse_channel_name("https://www.youtube.com/@GODofIT") == "GODofIT"
    assert parse_channel_name("https://www.youtube.com/@myChannel/") == "myChannel"


def test_load_channels_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "nonexistent.json"))
    channels = load_channels()
    assert channels == []


def test_load_channels_success(tmp_path, monkeypatch):
    f = tmp_path / "channels.json"
    f.write_text('["https://www.youtube.com/@GODofIT"]')
    monkeypatch.setenv("CHANNELS_FILE", str(f))
    channels = load_channels()
    assert channels == ["https://www.youtube.com/@GODofIT"]


def test_load_channels_invalid_json(tmp_path, monkeypatch):
    import json
    f = tmp_path / "channels.json"
    f.write_text("not valid json")
    monkeypatch.setenv("CHANNELS_FILE", str(f))
    with pytest.raises(json.JSONDecodeError):
        load_channels()
