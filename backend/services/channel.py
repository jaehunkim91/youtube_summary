# backend/services/channel.py
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    video_id: str
    title: str
    published_at: datetime  # UTC


class ChannelFetchError(Exception):
    pass


def parse_channel_name(channel_url: str) -> str:
    """Extract handle from URL: https://www.youtube.com/@GODofIT -> GODofIT"""
    url = channel_url.rstrip("/")
    if "/@" in url:
        return url.split("/@")[-1]
    return url


def load_channels() -> list[str]:
    """Read channels.json. Returns [] if file missing or empty. Raises JSONDecodeError on bad JSON."""
    env_val = os.getenv("CHANNELS_FILE")
    path = Path(env_val) if env_val else Path(__file__).parent.parent.parent / "channels.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as e:
        logger.warning(f"channels.json 파싱 실패: {e}")
        raise


def fetch_recent_videos(channel_url: str, days: int = 1) -> list[VideoInfo]:
    """Fetch videos uploaded within the last `days` days from a channel."""
    dateafter = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)).strftime("%Y%m%d")

    result = subprocess.run(
        [
            "yt-dlp",
            "--flat-playlist",
            "--dateafter", dateafter,
            "--print", "%(id)s\t%(title)s\t%(upload_date)s",
            channel_url,
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        raise ChannelFetchError(f"yt-dlp failed for {channel_url}: {result.stderr[:200]}")

    videos = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        video_id, title, upload_date = parts[0], parts[1], parts[2]
        try:
            published_at = datetime.strptime(upload_date, "%Y%m%d")
        except ValueError:
            published_at = datetime.now(timezone.utc).replace(tzinfo=None)
        videos.append(VideoInfo(video_id=video_id, title=title, published_at=published_at))

    return videos
