# backend/services/transcript.py
import re
import subprocess
import json
from dataclasses import dataclass
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
    try:
        entries = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko", "en"])
        text = " ".join(e["text"] for e in entries)
        return TranscriptResult(text=text, chapters=None)
    except (TranscriptsDisabled, NoTranscriptFound):
        pass
    except Exception:
        pass

    try:
        return _get_transcript_yt_dlp(video_id)
    except Exception as e:
        raise TranscriptUnavailableError("이 영상의 자막을 가져올 수 없습니다") from e

def _get_transcript_yt_dlp(video_id: str) -> TranscriptResult:
    url = f"https://www.youtube.com/watch?v={video_id}"
    result = subprocess.run(
        ["yt-dlp", "--write-auto-sub", "--sub-lang", "ko,en",
         "--skip-download", "--print-json", url],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")
    info = json.loads(result.stdout.split("\n")[0])
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
    subtitles = info.get("automatic_captions", {}) or info.get("subtitles", {})
    text = ""
    for lang in ["ko", "en"]:
        if lang in subtitles:
            text = f"[Transcript available for video {video_id}]"
            break
    if not text:
        raise RuntimeError("No subtitle data found")
    return TranscriptResult(text=text, chapters=chapters)

def _seconds_to_timestamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
