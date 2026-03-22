# backend/tests/test_stock_analyzer.py
import pytest
from unittest.mock import patch, MagicMock
from backend.services.stock_analyzer import (
    analyze_video,
    StockAnalyzerError,
    AnalysisResult,
    StockInfo,
)


def _mock_response(text: str):
    content = MagicMock()
    content.text = text
    response = MagicMock()
    response.content = [content]
    return response


def test_analyze_video_success():
    mock_json = '{"summary": "테스트 요약", "stocks": [{"name": "삼성전자", "sentiment": "positive", "opinion": "실적 기대"}]}'
    with patch("backend.services.stock_analyzer.Anthropic") as MockClaude:
        MockClaude.return_value.messages.create.return_value = _mock_response(mock_json)
        result = analyze_video("테스트 자막")

    assert isinstance(result, AnalysisResult)
    assert result.summary == "테스트 요약"
    assert len(result.stocks) == 1
    assert result.stocks[0].name == "삼성전자"
    assert result.stocks[0].sentiment == "positive"
    assert result.stocks[0].opinion == "실적 기대"


def test_analyze_video_no_stocks():
    mock_json = '{"summary": "테스트 요약", "stocks": []}'
    with patch("backend.services.stock_analyzer.Anthropic") as MockClaude:
        MockClaude.return_value.messages.create.return_value = _mock_response(mock_json)
        result = analyze_video("테스트 자막")

    assert result.stocks == []


def test_analyze_video_strips_markdown_fence():
    mock_text = '```json\n{"summary": "요약", "stocks": []}\n```'
    with patch("backend.services.stock_analyzer.Anthropic") as MockClaude:
        MockClaude.return_value.messages.create.return_value = _mock_response(mock_text)
        result = analyze_video("자막")

    assert result.summary == "요약"


def test_analyze_video_truncates_long_transcript():
    """Verify transcript longer than 12000 chars is truncated before sending to Claude."""
    mock_json = '{"summary": "요약", "stocks": []}'
    long_transcript = "X" * 20000
    with patch("backend.services.stock_analyzer.Anthropic") as MockClaude:
        MockClaude.return_value.messages.create.return_value = _mock_response(mock_json)
        analyze_video(long_transcript)

    call_args = MockClaude.return_value.messages.create.call_args
    content = call_args.kwargs["messages"][0]["content"]
    # The 12001st character of the original transcript must NOT appear in the prompt
    assert "X" * 12001 not in content


def test_analyze_video_invalid_json():
    with patch("backend.services.stock_analyzer.Anthropic") as MockClaude:
        MockClaude.return_value.messages.create.return_value = _mock_response("not valid json")
        with pytest.raises(StockAnalyzerError):
            analyze_video("자막")
