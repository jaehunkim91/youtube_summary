// frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react'
import { UrlInput } from './components/UrlInput'
import { SummaryView } from './components/SummaryView'
import { HistoryList } from './components/HistoryList'
import { summarize, getHistory, getHistoryDetail } from './api/client'
import type { SummaryResponse, HistoryItem } from './api/client'

type LoadingState = 'idle' | 'transcript' | 'summarizing'

export default function App() {
  const [loading, setLoading] = useState<LoadingState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<SummaryResponse | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const refreshHistory = useCallback(async () => {
    try {
      setHistory(await getHistory())
    } catch {
      // non-critical
    }
  }, [])

  useEffect(() => { refreshHistory() }, [refreshHistory])

  const handleSubmit = async (url: string) => {
    setError(null)
    setLoading('transcript')
    const timeout = setTimeout(() => {
      setError('요청 시간이 초과되었습니다 (60초)')
      setLoading('idle')
    }, 60000)

    try {
      setLoading('summarizing')
      const result = await summarize(url)
      setSummary(result)
      setSelectedId(result.id)
      await refreshHistory()
    } catch (e) {
      setError(e instanceof Error ? e.message : '알 수 없는 오류가 발생했습니다')
    } finally {
      clearTimeout(timeout)
      setLoading('idle')
    }
  }

  const handleHistorySelect = async (id: number) => {
    setSelectedId(id)
    setError(null)
    try {
      setSummary(await getHistoryDetail(id))
    } catch (e) {
      setError(e instanceof Error ? e.message : '불러오기 실패')
    }
  }

  const loadingText = loading === 'transcript' ? '자막 추출 중...' : loading === 'summarizing' ? '요약 생성 중...' : ''

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Sidebar */}
      <div style={{ width: '280px', borderRight: '1px solid #ddd', overflowY: 'auto', flexShrink: 0 }}>
        <HistoryList items={history} selectedId={selectedId} onSelect={handleHistorySelect} />
      </div>

      {/* Main area */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <h1 style={{ padding: '16px', margin: 0, borderBottom: '1px solid #eee' }}>YouTube 요약</h1>
        <UrlInput onSubmit={handleSubmit} isLoading={loading !== 'idle'} />

        {loading !== 'idle' && (
          <div style={{ padding: '16px', color: '#555' }}>⏳ {loadingText}</div>
        )}
        {error && (
          <div style={{ padding: '16px', color: '#c00', background: '#fff0f0', margin: '16px' }}>
            {error}
          </div>
        )}
        {summary && loading === 'idle' && !error && (
          <SummaryView summary={summary} />
        )}
      </div>
    </div>
  )
}
