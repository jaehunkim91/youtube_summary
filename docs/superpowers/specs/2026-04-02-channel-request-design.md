# Channel Request Feature Design

**Date:** 2026-04-02
**Status:** Approved

## Overview

유튜버 추천 요청 게시판. 방문자가 닉네임과 원하는 유튜버 이름(+ 선택적 메모)을 남기면, 앱 관리자가 나중에 채널 목록에 반영한다.

---

## Data Model

### New Table: `channel_requests`

| Column       | Type             | Constraints             | Description          |
|--------------|------------------|-------------------------|----------------------|
| id           | Integer          | PK, auto-increment      |                      |
| nickname     | String(50)       | NOT NULL                | 요청자 닉네임         |
| channel_name | String(50)       | NOT NULL                | 원하는 유튜버 이름    |
| content      | Text             | nullable                | 자유 메모 (선택)      |
| created_at   | DateTime         | default UTC now         | 제출 시각             |

**Validation:**
- `nickname`: 필수, 공백 불가, 최대 50자
- `channel_name`: 필수, 공백 불가, 최대 50자
- `content`: 선택, 최대 500자

---

## API

### `POST /api/channel-requests`
요청 제출.

**Request body:**
```json
{
  "nickname": "홍길동",
  "channel_name": "삼프로TV",
  "content": "경제 방송인데 퀄리티가 좋아요"  // optional
}
```

**Response (201):**
```json
{
  "id": 1,
  "nickname": "홍길동",
  "channel_name": "삼프로TV",
  "content": "경제 방송인데 퀄리티가 좋아요",
  "created_at": "2026-04-02T10:00:00Z"
}
```

**Errors:**
- 422: 유효성 검사 실패 (빈 필드, 길이 초과)

### `GET /api/channel-requests`
전체 요청 목록 조회 (최신순).

**Response (200):**
```json
[
  {
    "id": 1,
    "nickname": "홍길동",
    "channel_name": "삼프로TV",
    "content": "경제 방송인데 퀄리티가 좋아요",
    "created_at": "2026-04-02T10:00:00Z"
  }
]
```

---

## Frontend

### Navigation
기존 앱에 상단 탭 네비게이션 추가:
- **채널** (기존 ChannelList)
- **종목** (기존 StockList)
- **요청** (신규)

`App.tsx`에서 탭 상태 관리, 각 탭 클릭 시 해당 컴포넌트 렌더링.

### New Components

**`RequestPage.tsx`** — 요청 페이지 컨테이너
- 폼 + 목록을 합친 페이지 컴포넌트
- 제출 후 목록 자동 갱신

**`RequestForm.tsx`** — 입력 폼
- 닉네임 (필수), 유튜버 이름 (필수), 하고 싶은 말 (선택) 입력 필드
- 제출 버튼 (로딩 상태 포함)
- 제출 성공 시 폼 초기화

**`RequestCard.tsx`** — 요청 카드
- 닉네임, 유튜버 이름, 내용(있을 경우), 제출 시각 표시
- 기존 `VideoCard`와 동일한 스타일 (border, borderRadius, padding)

### API Client
`api/client.ts`에 타입 + 함수 추가:
- `ChannelRequest` 타입
- `getChannelRequests(): Promise<ChannelRequest[]>`
- `postChannelRequest(data): Promise<ChannelRequest>`

---

## File Changes Summary

| File | Change |
|------|--------|
| `backend/db/models.py` | `ChannelRequest` 모델 추가 |
| `backend/api/schemas.py` | `ChannelRequestCreate`, `ChannelRequestResponse` 스키마 추가 |
| `backend/api/routes.py` | `POST /api/channel-requests`, `GET /api/channel-requests` 라우트 추가 |
| `frontend/src/api/client.ts` | `ChannelRequest` 타입, API 함수 2개 추가 |
| `frontend/src/App.tsx` | 탭 네비게이션 추가, `RequestPage` 렌더링 |
| `frontend/src/components/RequestPage.tsx` | 신규 |
| `frontend/src/components/RequestForm.tsx` | 신규 |
| `frontend/src/components/RequestCard.tsx` | 신규 |
