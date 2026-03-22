# backend/tests/test_summarizer.py
from unittest.mock import patch, MagicMock
import pytest
from backend.services.summarizer import summarize_transcript, SummaryChapter
from backend.services.transcript import TranscriptResult, ChapterMeta

def _make_claude_response(content: str):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text=content)]
    return mock_resp

SAMPLE_JSON = '''[
  {"title": "소개", "timestamp": "00:00", "content": "영상 소개입니다."},
  {"title": "본론", "timestamp": "02:30", "content": "핵심 내용입니다."}
]'''

def test_summarize_without_chapters():
    transcript = TranscriptResult(text="긴 텍스트...", chapters=None)
    with patch("backend.services.summarizer.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_claude_response(SAMPLE_JSON)
        result = summarize_transcript(transcript, "Test Video")
    assert len(result) == 2
    assert result[0].title == "소개"
    assert result[0].timestamp == "00:00"
    assert result[1].title == "본론"

def test_summarize_with_existing_chapters():
    chapters = [
        ChapterMeta(title="Intro", timestamp="00:00", start_seconds=0),
        ChapterMeta(title="Main", timestamp="03:00", start_seconds=180),
    ]
    transcript = TranscriptResult(text="긴 텍스트...", chapters=chapters)
    with patch("backend.services.summarizer.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_claude_response(SAMPLE_JSON)
        result = summarize_transcript(transcript, "Test Video")
    # Should pass chapter titles to Claude
    call_args = mock_client.messages.create.call_args
    prompt = call_args.kwargs["messages"][0]["content"]
    assert "Intro" in prompt or "Main" in prompt
    assert len(result) == 2

def test_summarize_invalid_json_raises():
    from backend.services.summarizer import SummarizerError
    transcript = TranscriptResult(text="text", chapters=None)
    with patch("backend.services.summarizer.anthropic.Anthropic") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_claude_response("not valid json")
        with pytest.raises(SummarizerError):
            summarize_transcript(transcript, "Test Video")
