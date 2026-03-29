# 사용 가이드

## 최초 설정 (처음 한 번만)

### 1. API 키 설정

프로젝트 루트의 `.env` 파일을 열어 실제 Anthropic API 키로 교체합니다:

```
ANTHROPIC_API_KEY=sk-ant-여기에실제키입력
```

> Anthropic API 키는 https://console.anthropic.com 에서 발급받을 수 있습니다.

### 2. 의존성 설치

```bash
# 백엔드
cd backend
pip install -r requirements.txt

# 프론트엔드
cd ../frontend
npm install
```

### 3. 채널 목록 설정

프로젝트 루트의 `channels.json` 파일에 분석할 YouTube 채널 URL을 추가합니다:

```json
[
  "https://www.youtube.com/@GODofIT",
  "https://www.youtube.com/@another_channel"
]
```

> `@핸들` 형식의 URL만 지원합니다. 채널 추가/삭제는 이 파일을 직접 편집하면 됩니다.

---

## 매일 사용하기

### 개발 모드 실행 (터미널 2개 필요)

**터미널 1 — 백엔드:**
```bash
cd /Users/sujin/PycharmProjects/youtube_summary
.venv/bin/python -m uvicorn backend.main:app --reload
```

**터미널 2 — 프론트엔드:**
```bash
cd /Users/sujin/PycharmProjects/youtube_summary/frontend
npm run dev
```

브라우저에서 **http://localhost:5173** 열기

### 사용 방법

1. 왼쪽 사이드바에서 채널 클릭
2. 오른쪽 패널에서 최근 영상 목록 확인
3. 각 영상 카드에서 AI 요약 및 언급 종목(긍정/부정/중립) 확인
4. **새로고침** 버튼 클릭 시 즉시 최신 영상 수집 및 분석 실행

> **자동 수집:** 매일 09:00 KST에 `channels.json`에 등록된 채널의 최근 1일 영상을 자동으로 수집·분석합니다.

> **중복 방지:** 동일한 영상은 재분석하지 않습니다.

---

## 프로덕션 빌드 (단일 서버로 실행)

프론트엔드를 빌드하면 백엔드 하나만으로 서비스할 수 있습니다:

```bash
# 프론트엔드 빌드
cd /Users/sujin/PycharmProjects/youtube_summary/frontend
npm run build

# 백엔드 단독 실행 (http://localhost:8000)
cd /Users/sujin/PycharmProjects/youtube_summary
.venv/bin/python -m uvicorn backend.main:app
```

브라우저에서 **http://localhost:8000** 열기

---

## 오류 대처

| 오류 상황 | 원인 | 해결 방법 |
|-----------|------|-----------|
| 채널이 목록에 표시되지 않음 | `channels.json` 파일 없거나 비어있음 | `channels.json`에 채널 URL 추가 |
| 영상이 없다고 표시됨 | 최근 1일 이내 업로드된 영상 없음 | 정상 상태. 다음 날 재확인 |
| 새로고침 후에도 영상 없음 | yt-dlp 오류 또는 채널 URL 형식 오류 | `@핸들` 형식인지 확인, 서버 로그 확인 |
| 종목 분석이 비어있음 | 영상에서 종목 언급 없음 | 정상 상태 (요약만 표시됨) |
| Claude API 오류 | API 키 문제 | `.env`의 `ANTHROPIC_API_KEY` 확인 |

---

## 지원 채널 URL 형식

```
https://www.youtube.com/@채널핸들
```

예시:
```
https://www.youtube.com/@GODofIT
```

> `/channel/UCxxxx` 형식은 지원하지 않습니다.

---

## 데이터 저장 위치

분석 결과는 `backend/youtube_summary.db` (SQLite 파일)에 저장됩니다.
삭제하면 모든 분석 히스토리가 초기화됩니다.
