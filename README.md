# YouTube 요약 웹앱

YouTube 영상의 자막을 자동으로 추출하고, Claude AI가 챕터별로 요약해주는 웹앱입니다.

## 기능

- YouTube URL 입력 → 챕터별 요약 자동 생성
- 명시적 챕터가 없는 영상도 AI가 섹션을 나눠 요약
- 이전 요약 히스토리 저장 및 조회
- 동일 URL 재요청 시 캐시된 결과 즉시 반환

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| 백엔드 | FastAPI, SQLAlchemy, SQLite |
| AI 요약 | Claude API (claude-sonnet-4-6) |
| 자막 추출 | youtube-transcript-api, yt-dlp |
| 프론트엔드 | React 18, TypeScript, Vite |

## 개발 환경 실행

### 1. 백엔드 설정
```bash
cd /path/to/youtube_summary
pip install -r backend/requirements.txt
```

프로젝트 루트의 `.env` 파일에 API 키 입력:
```
ANTHROPIC_API_KEY=sk-ant-...
```

백엔드 실행:
```bash
.venv/bin/python -m uvicorn backend.main:app --reload
```

### 2. 프론트엔드 실행 (별도 터미널)
```bash
cd frontend
npm install
npm run dev
```

브라우저에서 http://localhost:5173 열기

## 프로덕션 빌드

```bash
# 프론트엔드 빌드
cd frontend && npm run build

# 백엔드로 서빙 (http://localhost:8000)
.venv/bin/python -m uvicorn backend.main:app
```

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/summarize | YouTube URL 요약 생성 |
| GET | /api/history | 요약 히스토리 목록 (최근 50개) |
| GET | /api/history/{id} | 특정 요약 상세 조회 |
