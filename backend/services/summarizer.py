# backend/services/summarizer.py
import json
import os
from dataclasses import dataclass
import anthropic
from dotenv import load_dotenv
from backend.services.transcript import TranscriptResult

load_dotenv()

@dataclass
class SummaryChapter:
    title: str
    timestamp: str
    content: str

class SummarizerError(Exception):
    pass

def summarize_transcript(transcript: TranscriptResult, video_title: str) -> list[SummaryChapter]:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    if transcript.chapters:
        chapter_info = "\n".join(
            f"- [{c.timestamp}] {c.title}" for c in transcript.chapters
        )
        prompt = f"""다음은 YouTube 영상 "{video_title}"의 자막입니다.
이 영상에는 다음과 같은 챕터가 있습니다:
{chapter_info}

각 챕터별로 3~5문장으로 요약해주세요.
반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
[
  {{"title": "챕터 제목", "timestamp": "00:00", "content": "요약 내용"}},
  ...
]

자막:
{transcript.text[:12000]}"""
    else:
        prompt = f"""다음은 YouTube 영상 "{video_title}"의 자막입니다.
이 내용을 논리적인 섹션으로 나누고 각 섹션을 3~5문장으로 요약해주세요.
반드시 다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
[
  {{"title": "섹션 제목", "timestamp": "00:00", "content": "요약 내용"}},
  ...
]
timestamp는 영상의 대략적인 시작 시간을 "MM:SS" 형식으로 추정해주세요.

자막:
{transcript.text[:12000]}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SummarizerError(f"Claude returned invalid JSON: {e}") from e

    return [
        SummaryChapter(
            title=item["title"],
            timestamp=item.get("timestamp", "00:00"),
            content=item["content"],
        )
        for item in data
    ]
