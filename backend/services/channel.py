# backend/services/channel.py
import json
import logging
import os
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_RSS_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


@dataclass
class VideoInfo:
    video_id: str
    title: str
    published_at: Optional[datetime]


class ChannelFetchError(Exception):
    pass


def parse_channel_name(channel_url: str) -> str:
    """Extract handle from URL: https://www.youtube.com/@GODofIT -> GODofIT"""
    url = channel_url.rstrip("/")
    if "/@" in url:
        return url.split("/@")[-1]
    return url


def load_channels() -> list[dict]:
    """Read channels.json. Returns [] if file missing or empty. Raises JSONDecodeError on bad JSON.

    Supports both legacy format (list of URL strings) and new format (list of {url, name} objects).
    Always returns list of dicts with 'url' and 'name' keys.
    """
    env_val = os.getenv("CHANNELS_FILE")
    path = Path(env_val) if env_val else Path(__file__).parent.parent.parent / "channels.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        result = []
        for item in data:
            if isinstance(item, str):
                result.append({"url": item, "name": parse_channel_name(item)})
            elif isinstance(item, dict) and "url" in item:
                result.append({"url": item["url"], "name": item.get("name") or parse_channel_name(item["url"])})
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"channels.json 파싱 실패: {e}")
        raise


def _get_channel_id(channel_url: str) -> str:
    """Get YouTube channel ID (UCxxxx) via yt-dlp."""
    result = subprocess.run(
        [
            "yt-dlp",
            "--flat-playlist",
            "--playlist-end", "1",
            "--print", "%(playlist_channel_id)s",
            "--remote-components", "ejs:github",
            channel_url,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise ChannelFetchError(f"yt-dlp failed for {channel_url}: {result.stderr[:200]}")
    channel_id = result.stdout.strip().splitlines()[0].strip()
    if not channel_id or channel_id == "NA":
        raise ChannelFetchError(f"Could not get channel_id for {channel_url}")
    return channel_id


def _fetch_rss_videos(channel_id: str, max_count: int) -> list[VideoInfo]:
    """Fetch videos from YouTube RSS feed (max 15 per feed)."""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    videos = []
    for entry in root.findall("atom:entry", _RSS_NS):
        video_id_el = entry.find("yt:videoId", _RSS_NS)
        title_el = entry.find("atom:title", _RSS_NS)
        published_el = entry.find("atom:published", _RSS_NS)

        if video_id_el is None or title_el is None:
            continue

        published_at: Optional[datetime] = None
        if published_el is not None and published_el.text:
            try:
                published_at = datetime.fromisoformat(published_el.text).astimezone(timezone.utc).replace(tzinfo=None)
            except ValueError:
                pass

        videos.append(VideoInfo(
            video_id=video_id_el.text or "",
            title=title_el.text or "",
            published_at=published_at,
        ))
        if len(videos) >= max_count:
            break

    return videos


def fetch_recent_videos(channel_url: str, max_count: int = 5) -> list[VideoInfo]:
    """Fetch the most recent `max_count` videos from a channel using YouTube RSS feed."""
    channel_id = _get_channel_id(channel_url)
    return _fetch_rss_videos(channel_id, max_count)


def get_video_duration(video_id: str) -> Optional[int]:
    """Return video duration in seconds, or None on failure."""
    result = subprocess.run(
        [
            "yt-dlp",
            "--print", "%(duration)s",
            "--skip-download",
            "--remote-components", "ejs:github",
            f"https://www.youtube.com/watch?v={video_id}",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        return None
    try:
        return int(float(result.stdout.strip()))
    except (ValueError, IndexError):
        return None
