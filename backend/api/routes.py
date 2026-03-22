# backend/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db.database import get_db
from backend.db.models import Summary, Chapter
from backend.api.schemas import SummarizeRequest, SummaryResponse, HistoryItemResponse
from backend.services.transcript import get_transcript, extract_video_id, TranscriptUnavailableError
from backend.services.summarizer import summarize_transcript, SummarizerError
import httpx

router = APIRouter(prefix="/api")

def get_video_title(video_id: str) -> str:
    try:
        resp = httpx.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("title", "Unknown Title")
    except Exception:
        pass
    return "Unknown Title"

@router.post("/summarize", response_model=SummaryResponse)
def summarize(request: SummarizeRequest, db: Session = Depends(get_db)):
    try:
        video_id = extract_video_id(request.url)
    except ValueError:
        raise HTTPException(status_code=400, detail="유효한 YouTube URL이 아닙니다")

    # Return cached result if URL already exists
    existing = db.query(Summary).filter(Summary.youtube_url == request.url).first()
    if existing:
        return SummaryResponse.model_validate(existing)

    video_title = get_video_title(video_id)

    try:
        transcript = get_transcript(video_id)
    except TranscriptUnavailableError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        chapters = summarize_transcript(transcript, video_title)
    except SummarizerError as e:
        raise HTTPException(status_code=502, detail=f"요약 생성에 실패했습니다: {e}")

    summary = Summary(youtube_url=request.url, video_title=video_title, video_id=video_id)
    db.add(summary)
    db.flush()

    for i, ch in enumerate(chapters):
        db.add(Chapter(
            summary_id=summary.id,
            title=ch.title,
            timestamp=ch.timestamp,
            content=ch.content,
            order=i,
        ))
    db.commit()
    db.refresh(summary)

    return SummaryResponse.model_validate(summary)

@router.get("/history", response_model=list[HistoryItemResponse])
def get_history(db: Session = Depends(get_db)):
    summaries = db.query(Summary).order_by(Summary.created_at.desc()).limit(50).all()
    return [
        HistoryItemResponse(
            id=s.id,
            video_title=s.video_title,
            video_id=s.video_id,
            youtube_url=s.youtube_url,
            created_at=s.created_at,
            chapter_count=len(s.chapters),
        )
        for s in summaries
    ]

@router.get("/history/{summary_id}", response_model=SummaryResponse)
def get_history_detail(summary_id: int, db: Session = Depends(get_db)):
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=404, detail="요약을 찾을 수 없습니다")
    return SummaryResponse.model_validate(summary)
