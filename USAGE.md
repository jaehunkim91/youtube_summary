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

1. YouTube 영상 URL을 입력창에 붙여넣기
2. **요약하기** 버튼 클릭
3. 자막 추출 → 요약 생성 순서로 진행 (영상 길이에 따라 10~30초 소요)
4. 챕터별 요약이 아코디언 형태로 표시됨 — 클릭하면 펼쳐짐
5. 왼쪽 사이드바에서 이전 요약 기록 확인 및 재열람 가능

> **같은 URL 재요청 시** 저장된 결과를 즉시 반환합니다 (Claude API 호출 없음)

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

| 오류 메시지 | 원인 | 해결 방법 |
|-------------|------|-----------|
| 자막을 가져올 수 없습니다 | 자막 없는 영상 또는 비공개 영상 | 자막이 있는 다른 영상 시도 |
| 요약 생성에 실패했습니다 | Claude API 오류 (키 문제 등) | `.env`의 API 키 확인 |
| 유효한 YouTube URL이 아닙니다 | 잘못된 URL 형식 | `youtube.com/watch?v=` 또는 `youtu.be/` 형식 사용 |
| 요청 시간이 초과되었습니다 | 네트워크 느림 또는 영상이 너무 긴 경우 | 잠시 후 재시도 |

---

## 지원 URL 형식

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
```

---

## 데이터 저장 위치

요약 결과는 `backend/youtube_summary.db` (SQLite 파일)에 저장됩니다.
삭제하면 히스토리가 초기화됩니다.
