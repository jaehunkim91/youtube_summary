// frontend/src/api/client.ts

export interface StockMention {
  name: string
  sentiment: 'positive' | 'negative' | 'neutral'
  opinion: string
}

export interface Video {
  video_id: string
  title: string
  title_ko: string | null
  published_at: string
  analyzed_at: string
  summary: string | null
  stocks: StockMention[]
}

export interface ChannelFeedItem {
  channel_name: string
  channel_url: string
  video_count: number
  latest_video_title: string | null
  latest_video_title_ko: string | null
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

export async function getChannelFeed(channelUrl: string): Promise<ChannelDetail> {
  const resp = await fetch(`/api/feed/detail?url=${encodeURIComponent(channelUrl)}`)
  if (!resp.ok) throw new Error('채널 피드를 불러오지 못했습니다')
  return resp.json()
}

export interface StockFeedItem {
  name: string
  mention_count: number
  latest_mentioned_at: string | null
}

export interface StockOpinionItem {
  channel_name: string
  sentiment: 'positive' | 'negative' | 'neutral'
  opinion: string
  video_title: string
  video_title_ko: string | null
  published_at: string
}

export interface StockDetail {
  stock_name: string
  opinions: StockOpinionItem[]
}

export async function getStockFeed(): Promise<StockFeedItem[]> {
  const resp = await fetch('/api/stocks')
  if (!resp.ok) throw new Error('종목 목록을 불러오지 못했습니다')
  return resp.json()
}

export async function getStockDetail(name: string): Promise<StockDetail> {
  const resp = await fetch(`/api/stocks/detail?name=${encodeURIComponent(name)}`)
  if (!resp.ok) throw new Error('종목 상세를 불러오지 못했습니다')
  return resp.json()
}
