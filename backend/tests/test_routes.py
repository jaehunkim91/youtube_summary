# backend/tests/test_routes.py
from unittest.mock import patch
from backend.services.summarizer import SummaryChapter
from backend.services.transcript import TranscriptResult, TranscriptUnavailableError

MOCK_TRANSCRIPT = TranscriptResult(text="transcript text", chapters=None)
MOCK_CHAPTERS = [
    SummaryChapter(title="소개", timestamp="00:00", content="소개 내용"),
    SummaryChapter(title="결론", timestamp="05:00", content="결론 내용"),
]

def test_summarize_success(client):
    with patch("backend.api.routes.extract_video_id", return_value="abc123"), \
         patch("backend.api.routes.get_transcript", return_value=MOCK_TRANSCRIPT), \
         patch("backend.api.routes.summarize_transcript", return_value=MOCK_CHAPTERS), \
         patch("backend.api.routes.get_video_title", return_value="Test Video"):
        resp = client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["video_title"] == "Test Video"
    assert len(data["chapters"]) == 2
    assert data["chapters"][0]["title"] == "소개"

def test_summarize_duplicate_url_returns_cached(client):
    with patch("backend.api.routes.extract_video_id", return_value="abc123"), \
         patch("backend.api.routes.get_transcript", return_value=MOCK_TRANSCRIPT), \
         patch("backend.api.routes.summarize_transcript", return_value=MOCK_CHAPTERS), \
         patch("backend.api.routes.get_video_title", return_value="Test Video"):
        resp1 = client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
        resp2 = client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["id"] == resp2.json()["id"]

def test_summarize_transcript_unavailable(client):
    with patch("backend.api.routes.extract_video_id", return_value="abc123"), \
         patch("backend.api.routes.get_transcript", side_effect=TranscriptUnavailableError("없음")), \
         patch("backend.api.routes.get_video_title", return_value="Test Video"):
        resp = client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
    assert resp.status_code == 422

def test_summarize_invalid_url(client):
    resp = client.post("/api/summarize", json={"url": "https://google.com"})
    assert resp.status_code == 422

def test_history_empty(client):
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert resp.json() == []

def test_history_after_summarize(client):
    with patch("backend.api.routes.extract_video_id", return_value="abc123"), \
         patch("backend.api.routes.get_transcript", return_value=MOCK_TRANSCRIPT), \
         patch("backend.api.routes.summarize_transcript", return_value=MOCK_CHAPTERS), \
         patch("backend.api.routes.get_video_title", return_value="Test Video"):
        client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["chapter_count"] == 2

def test_history_detail(client):
    with patch("backend.api.routes.extract_video_id", return_value="abc123"), \
         patch("backend.api.routes.get_transcript", return_value=MOCK_TRANSCRIPT), \
         patch("backend.api.routes.summarize_transcript", return_value=MOCK_CHAPTERS), \
         patch("backend.api.routes.get_video_title", return_value="Test Video"):
        create_resp = client.post("/api/summarize", json={"url": "https://youtube.com/watch?v=abc123"})
    summary_id = create_resp.json()["id"]
    resp = client.get(f"/api/history/{summary_id}")
    assert resp.status_code == 200
    assert len(resp.json()["chapters"]) == 2

def test_history_detail_not_found(client):
    resp = client.get("/api/history/9999")
    assert resp.status_code == 404
