# backend/services/transcript.py
import re
import subprocess
import json
import logging
import tempfile
import os
from dataclasses import dataclass
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

@dataclass
class ChapterMeta:
    title: str
    timestamp: str
    start_seconds: float

@dataclass
class TranscriptResult:
    text: str
    chapters: Optional[list[ChapterMeta]]

class TranscriptUnavailableError(Exception):
    pass

def extract_video_id(url: str) -> str:
    patterns = [
        r"youtube\.com/watch\?.*v=([\w-]+)",
        r"youtu\.be/([\w-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Cannot extract video ID from URL: {url}")

def get_transcript(video_id: str) -> TranscriptResult:
    # Primary: yt-dlp (Chrome 쿠키 + JS challenge solver로 IP 차단 우회)
    try:
        return _get_transcript_yt_dlp(video_id)
    except Exception as e:
        logger.warning(f"yt-dlp transcript failed for {video_id}: {e}")

    # Fallback: youtube-transcript-api (IP 차단 없는 환경용)
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=["ko", "en"])
        entries = fetched.to_raw_data()
        text = " ".join(e["text"] for e in entries)
        return TranscriptResult(text=text, chapters=None)
    except Exception as e:
        logger.warning(f"youtube-transcript-api fallback failed for {video_id}: {e}")
        raise TranscriptUnavailableError("이 영상의 자막을 가져올 수 없습니다") from e

COOKIES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cookies.txt")

def _get_transcript_yt_dlp(video_id: str) -> TranscriptResult:
    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Get video metadata (chapters) and download subtitle files
        cmd = [
                "yt-dlp",
                "--write-auto-sub", "--write-sub",
                "--sub-lang", "ko,en",
                "--sub-format", "json3",
                "--skip-download",
                "--print-json",
                "--impersonate", "chrome",
                "--remote-components", "ejs:github",
                "--ignore-errors",
                "-o", os.path.join(tmpdir, "%(id)s"),
        ]
        if os.path.exists(COOKIES_PATH):
            cmd.extend(["--cookies", COOKIES_PATH])
        cmd.append(url)

        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed: {result.stderr}")

        info = json.loads(result.stdout.split("\n")[0])

        # Extract chapter metadata
        chapters = None
        if info.get("chapters"):
            chapters = [
                ChapterMeta(
                    title=c["title"],
                    timestamp=_seconds_to_timestamp(c["start_time"]),
                    start_seconds=c["start_time"],
                )
                for c in info["chapters"]
            ]

        # Find and parse downloaded subtitle file
        text = _read_subtitle_file(tmpdir, video_id)
        if not text:
            raise RuntimeError("No subtitle text extracted")

    return TranscriptResult(text=text, chapters=chapters)

def _read_subtitle_file(directory: str, video_id: str) -> str:
    """Read downloaded subtitle files and return plain text."""
    for lang in ["ko", "en"]:
        for suffix in [f".{lang}.json3", f".{lang}-orig.json3"]:
            path = os.path.join(directory, f"{video_id}{suffix}")
            if os.path.exists(path):
                return _parse_json3_subtitle(path)
    # Fallback: try any .json3 file in the directory
    for fname in os.listdir(directory):
        if fname.endswith(".json3"):
            return _parse_json3_subtitle(os.path.join(directory, fname))
    return ""

def _parse_json3_subtitle(path: str) -> str:
    """Parse yt-dlp json3 subtitle format to plain text."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    parts = []
    for event in data.get("events", []):
        for seg in event.get("segs", []):
            t = seg.get("utf8", "").strip()
            if t and t != "\n":
                parts.append(t)
    return " ".join(parts)

def _seconds_to_timestamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
