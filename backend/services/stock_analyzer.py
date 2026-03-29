# backend/services/stock_analyzer.py
import json
import logging
import os
import re
from dataclasses import dataclass, field
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """다음은 YouTube 주식 관련 영상의 자막입니다.

[영상 제목]
{title}

[자막 내용]
{transcript}

다음 JSON 형식으로만 응답하세요. 마크다운 코드블록 없이 순수 JSON만 출력하세요:
{{
  "title_ko": "영상 제목을 한국어로 번역 (이미 한국어면 그대로)",
  "summary": "영상 내용을 3-5문장으로 한국어로 요약",
  "stocks": [
    {{
      "name": "종목명 (예: 삼성전자)",
      "sentiment": "positive 또는 negative 또는 neutral",
      "opinion": "해당 종목에 대한 발언자의 주요 의견을 한 문장으로"
    }}
  ]
}}

영상에서 언급된 종목이 없으면 stocks는 빈 배열로 반환하세요."""


@dataclass
class StockInfo:
    name: str
    sentiment: str  # positive / negative / neutral
    opinion: str


@dataclass
class AnalysisResult:
    summary: str
    title_ko: str = ""
    stocks: list[StockInfo] = field(default_factory=list)


class StockAnalyzerError(Exception):
    pass


def analyze_video(transcript: str, title: str = "") -> AnalysisResult:
    """Analyze a video transcript with Claude. Returns title_ko + summary + stock mentions."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    truncated = transcript[:12000]

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(transcript=truncated, title=title)}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw)
    raw = re.sub(r'\n?```$', '', raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise StockAnalyzerError(f"Claude 응답 JSON 파싱 실패: {e}") from e

    stocks = [
        StockInfo(
            name=s["name"],
            sentiment=s.get("sentiment", "neutral"),
            opinion=s.get("opinion", ""),
        )
        for s in data.get("stocks", [])
    ]

    return AnalysisResult(
        title_ko=data.get("title_ko", ""),
        summary=data.get("summary", ""),
        stocks=stocks,
    )
