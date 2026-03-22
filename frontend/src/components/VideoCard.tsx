// frontend/src/components/VideoCard.tsx
import type { Video } from '../api/client'
import { StockBadge } from './StockBadge'

interface Props {
  video: Video
}

export function VideoCard({ video }: Props) {
  const date = new Date(video.published_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })

  return (
    <div style={{
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '12px',
      background: '#fff',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <a
          href={`https://www.youtube.com/watch?v=${video.video_id}`}
          target="_blank"
          rel="noreferrer"
          style={{ fontWeight: 600, color: '#1a1a1a', textDecoration: 'none', fontSize: '15px' }}
        >
          📹 {video.title}
        </a>
        <span style={{ color: '#888', fontSize: '13px', whiteSpace: 'nowrap', marginLeft: '12px' }}>
          {date}
        </span>
      </div>

      {video.summary && (
        <p style={{ marginTop: '8px', marginBottom: '8px', color: '#333', fontSize: '14px', lineHeight: '1.6' }}>
          {video.summary}
        </p>
      )}

      {video.stocks.length > 0 && (
        <div style={{ marginTop: '8px', borderTop: '1px solid #f0f0f0', paddingTop: '8px' }}>
          {video.stocks.map((s) => (
            <StockBadge key={s.name} name={s.name} sentiment={s.sentiment} opinion={s.opinion} />
          ))}
        </div>
      )}
    </div>
  )
}
