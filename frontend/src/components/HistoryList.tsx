// frontend/src/components/HistoryList.tsx
import type { HistoryItem } from '../api/client'

interface Props {
  items: HistoryItem[]
  selectedId: number | null
  onSelect: (id: number) => void
}

export function HistoryList({ items, selectedId, onSelect }: Props) {
  if (items.length === 0) {
    return <div style={{ padding: '16px', color: '#888' }}>아직 요약한 영상이 없습니다</div>
  }

  return (
    <div>
      <h3 style={{ padding: '16px 16px 8px' }}>히스토리</h3>
      {items.map((item) => (
        <div
          key={item.id}
          onClick={() => onSelect(item.id)}
          style={{
            padding: '12px 16px',
            cursor: 'pointer',
            background: selectedId === item.id ? '#e8f0fe' : 'transparent',
            borderBottom: '1px solid #eee',
          }}
        >
          <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>
            {item.video_title}
          </div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            챕터 {item.chapter_count}개 · {new Date(item.created_at).toLocaleDateString('ko-KR')}
          </div>
        </div>
      ))}
    </div>
  )
}
