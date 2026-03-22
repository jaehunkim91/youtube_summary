// frontend/src/api/client.ts

export interface Chapter {
  id: number
  title: string
  timestamp: string
  content: string
  order: number
}

export interface SummaryResponse {
  id: number
  video_title: string
  video_id: string
  youtube_url: string
  created_at: string
  chapters: Chapter[]
}

export interface HistoryItem {
  id: number
  video_title: string
  video_id: string
  youtube_url: string
  created_at: string
  chapter_count: number
}

export async function summarize(url: string): Promise<SummaryResponse> {
  const resp = await fetch('/api/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: '알 수 없는 오류가 발생했습니다' }))
    throw new Error(err.detail ?? '요약에 실패했습니다')
  }
  return resp.json()
}

export async function getHistory(): Promise<HistoryItem[]> {
  const resp = await fetch('/api/history')
  if (!resp.ok) throw new Error('히스토리를 불러오지 못했습니다')
  return resp.json()
}

export async function getHistoryDetail(id: number): Promise<SummaryResponse> {
  const resp = await fetch(`/api/history/${id}`)
  if (!resp.ok) throw new Error('요약을 불러오지 못했습니다')
  return resp.json()
}
