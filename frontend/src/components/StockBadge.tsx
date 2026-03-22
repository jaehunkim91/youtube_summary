// frontend/src/components/StockBadge.tsx
interface Props {
  name: string
  sentiment: 'positive' | 'negative' | 'neutral'
  opinion: string
}

const SENTIMENT_COLOR: Record<string, { bg: string; text: string; label: string }> = {
  positive: { bg: '#e8f5e9', text: '#2e7d32', label: '긍정' },
  negative: { bg: '#ffebee', text: '#c62828', label: '부정' },
  neutral:  { bg: '#f5f5f5', text: '#555555', label: '중립' },
}

export function StockBadge({ name, sentiment, opinion }: Props) {
  const colors = SENTIMENT_COLOR[sentiment] ?? SENTIMENT_COLOR.neutral
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', marginTop: '6px' }}>
      <span style={{
        padding: '2px 8px',
        borderRadius: '12px',
        background: colors.bg,
        color: colors.text,
        fontSize: '13px',
        fontWeight: 600,
        whiteSpace: 'nowrap',
      }}>
        {name} [{colors.label}]
      </span>
      <span style={{ fontSize: '13px', color: '#555', lineHeight: '1.4' }}>{opinion}</span>
    </div>
  )
}
