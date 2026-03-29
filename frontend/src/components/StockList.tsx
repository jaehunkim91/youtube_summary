import type { StockFeedItem } from '../api/client'

interface Props {
  stocks: StockFeedItem[]
  selected: string | null
  onSelect: (name: string) => void
}

export function StockList({ stocks, selected, onSelect }: Props) {
  if (stocks.length === 0) {
    return (
      <div style={{ padding: '16px', color: '#888', fontSize: '13px' }}>
        분석된 종목이 없습니다
      </div>
    )
  }

  return (
    <div>
      {stocks.map((s) => (
        <button
          key={s.name}
          onClick={() => onSelect(s.name)}
          style={{
            display: 'block',
            width: '100%',
            textAlign: 'left',
            padding: '12px 16px',
            border: 'none',
            borderBottom: '1px solid #eee',
            background: selected === s.name ? '#e8f0fe' : 'transparent',
            cursor: 'pointer',
            fontWeight: (selected === s.name ? 600 : 400) as number,
          }}
        >
          <div style={{ fontSize: '14px', color: '#1a1a1a' }}>{s.name}</div>
          <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>
            언급 {s.mention_count}회
          </div>
        </button>
      ))}
    </div>
  )
}
