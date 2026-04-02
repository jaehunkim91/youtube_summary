import type { ChannelRequest } from '../api/client'

const fmt = (iso: string) =>
  new Date(iso).toLocaleString('ko-KR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false,
  })

export function RequestCard({ req }: { req: ChannelRequest }) {
  return (
    <div style={{
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '12px',
      background: '#fff',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <span style={{ fontWeight: 600, fontSize: '15px', color: '#1a1a1a' }}>
            📺 {req.channel_name}
          </span>
          <span style={{ marginLeft: '8px', fontSize: '13px', color: '#888' }}>
            by {req.nickname}
          </span>
        </div>
        <div style={{ color: '#888', fontSize: '12px', whiteSpace: 'nowrap', marginLeft: '12px' }}>
          {fmt(req.created_at)}
        </div>
      </div>
      {req.content && (
        <p style={{ margin: '8px 0 0', color: '#333', fontSize: '14px', lineHeight: '1.6' }}>
          {req.content}
        </p>
      )}
    </div>
  )
}
