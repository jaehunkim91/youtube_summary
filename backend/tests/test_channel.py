# backend/tests/test_channel.py
import json
import textwrap
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from backend.services.channel import (
    fetch_recent_videos,
    load_channels,
    parse_channel_name,
    ChannelFetchError,
    VideoInfo,
    _get_channel_id,
    _fetch_rss_videos,
)


def _mock_run(stdout="", returncode=0, stderr=""):
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    m.stderr = stderr
    return m


RSS_FEED = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:yt="http://www.youtube.com/xml/schemas/2015"
          xmlns:media="http://search.yahoo.com/mrss/">
      <entry>
        <yt:videoId>abc123</yt:videoId>
        <title>오늘 장 분석</title>
        <published>2026-03-24T09:00:00+00:00</published>
      </entry>
      <entry>
        <yt:videoId>xyz789</yt:videoId>
        <title>주목 종목</title>
        <published>2026-03-23T09:00:00+00:00</published>
      </entry>
    </feed>
""")


def _mock_resp(text="", status_code=200):
    m = MagicMock()
    m.content = text.encode()
    m.status_code = status_code
    m.raise_for_status = MagicMock()
    return m


# --- _get_channel_id ---

def test_get_channel_id_success():
    with patch("backend.services.channel.subprocess.run",
               return_value=_mock_run(stdout="UCz2jey-5FAhTWSTFkLjSCMw\n")) as mock_run:
        cid = _get_channel_id("https://www.youtube.com/@GODofIT")
    assert cid == "UCz2jey-5FAhTWSTFkLjSCMw"
    cmd = mock_run.call_args[0][0]
    assert "--flat-playlist" in cmd
    assert "%(playlist_channel_id)s" in cmd


def test_get_channel_id_failure():
    with patch("backend.services.channel.subprocess.run",
               return_value=_mock_run(returncode=1, stderr="yt-dlp error")):
        with pytest.raises(ChannelFetchError):
            _get_channel_id("https://www.youtube.com/@GODofIT")


def test_get_channel_id_na():
    with patch("backend.services.channel.subprocess.run",
               return_value=_mock_run(stdout="NA\n")):
        with pytest.raises(ChannelFetchError):
            _get_channel_id("https://www.youtube.com/@GODofIT")


# --- _fetch_rss_videos ---

def test_fetch_rss_videos_success():
    with patch("backend.services.channel.requests.get", return_value=_mock_resp(RSS_FEED)):
        videos = _fetch_rss_videos("UCz2jey-5FAhTWSTFkLjSCMw", max_count=5)
    assert len(videos) == 2
    assert videos[0].video_id == "abc123"
    assert videos[0].title == "오늘 장 분석"
    assert videos[0].published_at == datetime(2026, 3, 24, 9, 0, 0)


def test_fetch_rss_videos_max_count():
    with patch("backend.services.channel.requests.get", return_value=_mock_resp(RSS_FEED)):
        videos = _fetch_rss_videos("UCz2jey-5FAhTWSTFkLjSCMw", max_count=1)
    assert len(videos) == 1


def test_fetch_rss_videos_empty():
    empty_feed = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    with patch("backend.services.channel.requests.get", return_value=_mock_resp(empty_feed)):
        videos = _fetch_rss_videos("UCz2jey-5FAhTWSTFkLjSCMw", max_count=5)
    assert videos == []


# --- fetch_recent_videos (integration) ---

def test_fetch_recent_videos_success():
    with patch("backend.services.channel._get_channel_id", return_value="UCz2jey-5FAhTWSTFkLjSCMw"), \
         patch("backend.services.channel.requests.get", return_value=_mock_resp(RSS_FEED)):
        videos = fetch_recent_videos("https://www.youtube.com/@GODofIT", max_count=2)
    assert len(videos) == 2
    assert videos[0].published_at is not None  # RSS provides real dates


def test_fetch_recent_videos_channel_id_failure():
    with patch("backend.services.channel._get_channel_id", side_effect=ChannelFetchError("no id")):
        with pytest.raises(ChannelFetchError):
            fetch_recent_videos("https://www.youtube.com/@GODofIT")


def test_fetch_recent_videos_custom_max():
    with patch("backend.services.channel._get_channel_id", return_value="UCz2jey-5FAhTWSTFkLjSCMw"), \
         patch("backend.services.channel._fetch_rss_videos", return_value=[]) as mock_rss:
        fetch_recent_videos("https://www.youtube.com/@GODofIT", max_count=5)
    mock_rss.assert_called_once_with("UCz2jey-5FAhTWSTFkLjSCMw", 5)


# --- parse_channel_name ---

def test_parse_channel_name():
    assert parse_channel_name("https://www.youtube.com/@GODofIT") == "GODofIT"
    assert parse_channel_name("https://www.youtube.com/@myChannel/") == "myChannel"


# --- load_channels ---

def test_load_channels_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CHANNELS_FILE", str(tmp_path / "nonexistent.json"))
    channels = load_channels()
    assert channels == []


def test_load_channels_success(tmp_path, monkeypatch):
    f = tmp_path / "channels.json"
    f.write_text('[{"url": "https://www.youtube.com/@GODofIT", "name": "신의 IT"}]')
    monkeypatch.setenv("CHANNELS_FILE", str(f))
    channels = load_channels()
    assert channels == [{"url": "https://www.youtube.com/@GODofIT", "name": "신의 IT"}]


def test_load_channels_legacy_string_format(tmp_path, monkeypatch):
    """Legacy format (list of strings) should still work."""
    f = tmp_path / "channels.json"
    f.write_text('["https://www.youtube.com/@GODofIT"]')
    monkeypatch.setenv("CHANNELS_FILE", str(f))
    channels = load_channels()
    assert channels == [{"url": "https://www.youtube.com/@GODofIT", "name": "GODofIT"}]


def test_load_channels_invalid_json(tmp_path, monkeypatch):
    f = tmp_path / "channels.json"
    f.write_text("not valid json")
    monkeypatch.setenv("CHANNELS_FILE", str(f))
    with pytest.raises(json.JSONDecodeError):
        load_channels()
