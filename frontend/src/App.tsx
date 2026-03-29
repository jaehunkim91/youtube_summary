// frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react'
import { ChannelList } from './components/ChannelList'
import { StockList } from './components/StockList'
import { VideoCard } from './components/VideoCard'
import { StockDetailView } from './components/StockDetailView'
import { getFeed, getChannelFeed, getStockFeed, getStockDetail } from './api/client'
import type { ChannelFeedItem, ChannelDetail, StockFeedItem, StockDetail } from './api/client'

type Tab = 'channel' | 'stock'

const TAB_STYLE = (active: boolean): React.CSSProperties => ({
  flex: 1,
  padding: '8px 0',
  border: 'none',
  borderBottom: active ? '2px solid #1976d2' : '2px solid transparent',
  background: 'transparent',
  cursor: 'pointer',
  fontWeight: active ? 700 : 400,
  fontSize: '13px',
  color: active ? '#1976d2' : '#555',
})

export default function App() {
  const [tab, setTab] = useState<Tab>('channel')

  // Channel tab state
  const [channels, setChannels] = useState<ChannelFeedItem[]>([])
  const [selectedChannel, setSelectedChannel] = useState<string | null>(null)
  const [channelDetail, setChannelDetail] = useState<ChannelDetail | null>(null)

  // Stock tab state
  const [stocks, setStocks] = useState<StockFeedItem[]>([])
  const [selectedStock, setSelectedStock] = useState<string | null>(null)
  const [stockDetail, setStockDetail] = useState<StockDetail | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectChannel = async (url: string) => {
    setSelectedChannel(url)
    setLoading(true)
    setError(null)
    try {
      setChannelDetail(await getChannelFeed(url))
    } catch (e) {
      setError(e instanceof Error ? e.message : '채널 로드 실패')
    } finally {
      setLoading(false)
    }
  }

  const selectStock = async (name: string) => {
    setSelectedStock(name)
    setLoading(true)
    setError(null)
    try {
      setStockDetail(await getStockDetail(name))
    } catch (e) {
      setError(e instanceof Error ? e.message : '종목 로드 실패')
    } finally {
      setLoading(false)
    }
  }

  const loadFeed = useCallback(async () => {
    try {
      const data = await getFeed()
      setChannels(data)
      if (data.length > 0) selectChannel(data[0].channel_url)
    } catch (e) {
      setError(e instanceof Error ? e.message : '피드 로드 실패')
    }
  }, [])

  const loadStockFeed = useCallback(async () => {
    try {
      const data = await getStockFeed()
      setStocks(data)
      if (data.length > 0) selectStock(data[0].name)
    } catch (e) {
      setError(e instanceof Error ? e.message : '종목 피드 로드 실패')
    }
  }, [])

  useEffect(() => { loadFeed() }, [loadFeed])

  const handleTabChange = (t: Tab) => {
    setTab(t)
    setError(null)
    if (t === 'stock' && stocks.length === 0) {
      loadStockFeed()
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: '220px', borderRight: '1px solid #ddd', overflowY: 'auto', flexShrink: 0, background: '#fafafa', display: 'flex', flexDirection: 'column' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid #eee', flexShrink: 0 }}>
          <button style={TAB_STYLE(tab === 'channel')} onClick={() => handleTabChange('channel')}>채널</button>
          <button style={TAB_STYLE(tab === 'stock')} onClick={() => handleTabChange('stock')}>종목</button>
        </div>

        {tab === 'channel' ? (
          <ChannelList channels={channels} selected={selectedChannel} onSelect={selectChannel} />
        ) : (
          <StockList stocks={stocks} selected={selectedStock} onSelect={selectStock} />
        )}
      </div>

      {/* Main */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {/* Header */}
        <div style={{ padding: '16px', borderBottom: '1px solid #eee' }}>
          <h1 style={{ margin: 0, fontSize: '18px' }}>주식 유튜버 분석</h1>
        </div>

        {/* Content */}
        <div style={{ padding: '16px' }}>
          {error && (
            <div style={{ padding: '12px', color: '#c00', background: '#fff0f0', borderRadius: '6px', marginBottom: '12px' }}>
              {error}
            </div>
          )}

          {loading && <div style={{ color: '#555' }}>⏳ 불러오는 중...</div>}

          {!loading && tab === 'channel' && channelDetail && (
            <>
              <h2 style={{ margin: '0 0 16px', fontSize: '16px', color: '#555' }}>
                {channelDetail.channel_name} — 최근 영상 {channelDetail.videos.length}개
              </h2>
              {channelDetail.videos.length === 0 ? (
                <div style={{ color: '#888' }}>분석된 영상이 없습니다.</div>
              ) : (
                channelDetail.videos.map((v) => <VideoCard key={v.video_id} video={v} />)
              )}
            </>
          )}

          {!loading && tab === 'stock' && stockDetail && (
            <StockDetailView detail={stockDetail} />
          )}

          {!loading && tab === 'channel' && !channelDetail && channels.length === 0 && (
            <div style={{ color: '#888' }}>channels.json에 채널을 추가해주세요.</div>
          )}
        </div>
      </div>
    </div>
  )
}
