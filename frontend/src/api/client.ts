// frontend/src/api/client.ts

export interface StockMention {
  name: string
  sentiment: 'positive' | 'negative' | 'neutral'
  opinion: string
}

export interface Video {
  video_id: string
  title: string
  published_at: string
  summary: string | null
  stocks: StockMention[]
}

export interface ChannelFeedItem {
  channel_name: string
  channel_url: string
  video_count: number
  latest_video_title: string | null
  latest_video_at: string | null
}

export interface ChannelDetail {
  channel_name: string
  channel_url: string | null
  videos: Video[]
}

export async function getFeed(): Promise<ChannelFeedItem[]> {
  const resp = await fetch('/api/feed')
  if (!resp.ok) throw new Error('피드를 불러오지 못했습니다')
  return resp.json()
}

export async function getChannelFeed(channelName: string): Promise<ChannelDetail> {
  const resp = await fetch(`/api/feed/${encodeURIComponent(channelName)}`)
  if (!resp.ok) throw new Error('채널 피드를 불러오지 못했습니다')
  return resp.json()
}

export async function triggerRefresh(): Promise<void> {
  const resp = await fetch('/api/refresh', { method: 'POST' })
  if (!resp.ok) throw new Error('새로고침 요청에 실패했습니다')
}
