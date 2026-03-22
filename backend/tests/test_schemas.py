from backend.api.schemas import SummarizeRequest, ChapterResponse, SummaryResponse, HistoryItemResponse

def test_summarize_request_valid():
    req = SummarizeRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert req.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def test_summarize_request_invalid():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        SummarizeRequest(url="https://www.google.com")

def test_summary_response_shape():
    from datetime import datetime, timezone
    r = SummaryResponse(
        id=1, video_title="T", video_id="abc", youtube_url="https://youtube.com/watch?v=abc",
        created_at=datetime.now(timezone.utc),
        chapters=[ChapterResponse(id=1, title="Intro", timestamp="00:00", content="...", order=0)]
    )
    assert len(r.chapters) == 1
