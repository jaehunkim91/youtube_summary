import { useState, useEffect, useCallback } from 'react'
import { getChannelRequests } from '../api/client'
import type { ChannelRequest } from '../api/client'
import { RequestForm } from './RequestForm'
import { RequestCard } from './RequestCard'

export function RequestPage() {
  const [requests, setRequests] = useState<ChannelRequest[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setRequests(await getChannelRequests())
    } catch (e) {
      setError(e instanceof Error ? e.message : '목록을 불러오지 못했습니다')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <div>
      <RequestForm onSubmitted={load} />

      {error && (
        <div style={{ padding: '12px', color: '#c00', background: '#fff0f0', borderRadius: '6px', marginBottom: '12px' }}>
          {error}
        </div>
      )}

      {loading && <div style={{ color: '#555' }}>⏳ 불러오는 중...</div>}

      {!loading && requests.length === 0 && (
        <div style={{ color: '#888' }}>아직 요청이 없습니다.</div>
      )}

      {requests.map(r => <RequestCard key={r.id} req={r} />)}
    </div>
  )
}
