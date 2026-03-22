// frontend/src/App.tsx
import { useState, useEffect } from 'react'
import { ChannelList } from './components/ChannelList'
import { VideoCard } from './components/VideoCard'
import { getFeed, getChannelFeed, triggerRefresh } from './api/client'
import type { ChannelFeedItem, ChannelDetail } from './api/client'

export default function App() {
  const [channels, setChannels] = useState<ChannelFeedItem[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [detail, setDetail] = useState<ChannelDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const selectChannel = async (name: string) => {
    setSelected(name)
    setLoading(true)
    setError(null)
    try {
      setDetail(await getChannelFeed(name))
    } catch (e) {
      setError(e instanceof Error ? e.message : '채널 로드 실패')
    } finally {
      setLoading(false)
    }
  }

  const loadFeed = async () => {
    try {
      const data = await getFeed()
      setChannels(data)
      if (data.length > 0 && !selected) {
        selectChannel(data[0].channel_name)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '피드 로드 실패')
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    setError(null)
    try {
      await triggerRefresh()
      setTimeout(() => {
        loadFeed()
        if (selected) selectChannel(selected)
        setRefreshing(false)
      }, 2000)
    } catch (e) {
      setError(e instanceof Error ? e.message : '새로고침 실패')
      setRefreshing(false)
    }
  }

  useEffect(() => { loadFeed() }, [])

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: '220px', borderRight: '1px solid #ddd', overflowY: 'auto', flexShrink: 0, background: '#fafafa' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #eee', fontWeight: 700, fontSize: '14px' }}>
          채널 목록
        </div>
        <ChannelList channels={channels} selected={selected} onSelect={selectChannel} />
      </div>

      {/* Main */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px', borderBottom: '1px solid #eee' }}>
          <h1 style={{ margin: 0, fontSize: '18px' }}>주식 유튜버 분석</h1>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            style={{
              padding: '8px 16px',
              background: refreshing ? '#ccc' : '#1976d2',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: refreshing ? 'default' : 'pointer',
              fontSize: '14px',
            }}
          >
            {refreshing ? '새로고침 중...' : '새로고침'}
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '16px' }}>
          {error && (
            <div style={{ padding: '12px', color: '#c00', background: '#fff0f0', borderRadius: '6px', marginBottom: '12px' }}>
              {error}
            </div>
          )}

          {loading && <div style={{ color: '#555' }}>⏳ 불러오는 중...</div>}

          {!loading && detail && (
            <>
              <h2 style={{ margin: '0 0 16px', fontSize: '16px', color: '#555' }}>
                @{detail.channel_name} — 최근 영상 {detail.videos.length}개
              </h2>
              {detail.videos.length === 0 ? (
                <div style={{ color: '#888' }}>분석된 영상이 없습니다. 새로고침을 눌러주세요.</div>
              ) : (
                detail.videos.map((v) => <VideoCard key={v.video_id} video={v} />)
              )}
            </>
          )}

          {!loading && !detail && channels.length === 0 && (
            <div style={{ color: '#888' }}>
              channels.json에 채널을 추가하고 새로고침을 눌러주세요.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
