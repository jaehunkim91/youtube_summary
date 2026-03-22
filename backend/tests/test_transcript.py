# backend/tests/test_transcript.py
from unittest.mock import patch, MagicMock
import pytest
from backend.services.transcript import get_transcript, TranscriptResult

def test_get_transcript_primary_success():
    mock_entries = [
        {"text": "Hello world", "start": 0.0},
        {"text": "This is a test", "start": 5.0},
    ]
    with patch("backend.services.transcript.YouTubeTranscriptApi.get_transcript", return_value=mock_entries):
        result = get_transcript("dQw4w9WgXcQ")
    assert isinstance(result, TranscriptResult)
    assert "Hello world" in result.text
    assert result.chapters is None  # no chapter metadata from basic transcript

def test_get_transcript_fallback_to_ytdlp():
    from youtube_transcript_api import TranscriptsDisabled
    with patch("backend.services.transcript.YouTubeTranscriptApi.get_transcript", side_effect=TranscriptsDisabled("id")):
        with patch("backend.services.transcript._get_transcript_yt_dlp", return_value=TranscriptResult(text="fallback text", chapters=None)):
            result = get_transcript("dQw4w9WgXcQ")
    assert result.text == "fallback text"

def test_get_transcript_both_fail():
    from youtube_transcript_api import TranscriptsDisabled
    from backend.services.transcript import TranscriptUnavailableError
    with patch("backend.services.transcript.YouTubeTranscriptApi.get_transcript", side_effect=TranscriptsDisabled("id")):
        with patch("backend.services.transcript._get_transcript_yt_dlp", side_effect=Exception("yt-dlp failed")):
            with pytest.raises(TranscriptUnavailableError):
                get_transcript("dQw4w9WgXcQ")

def test_extract_video_id_from_url():
    from backend.services.transcript import extract_video_id
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
