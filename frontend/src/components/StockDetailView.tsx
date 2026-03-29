import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer } from 'recharts'
import type { StockDetail } from '../api/client'

const SENTIMENT_COLOR: Record<string, { bg: string; text: string; label: string; bar: string }> = {
  positive: { bg: '#e8f5e9', text: '#2e7d32', label: '긍정', bar: '#2e7d32' },
  negative: { bg: '#ffebee', text: '#c62828', label: '부정', bar: '#c62828' },
  neutral:  { bg: '#f5f5f5', text: '#555555', label: '중립', bar: '#9e9e9e' },
}

interface Props {
  detail: StockDetail
}

export function StockDetailView({ detail }: Props) {
  const counts = { positive: 0, negative: 0, neutral: 0 }
  for (const op of detail.opinions) {
    if (op.sentiment in counts) counts[op.sentiment as keyof typeof counts]++
  }
  const total = detail.opinions.length

  const chartData = (['positive', 'negative', 'neutral'] as const).map((s) => ({
    name: SENTIMENT_COLOR[s].label,
    count: counts[s],
    pct: total > 0 ? Math.round((counts[s] / total) * 100) : 0,
    color: SENTIMENT_COLOR[s].bar,
  }))

  return (
    <>
      <h2 style={{ margin: '0 0 16px', fontSize: '16px', color: '#555' }}>
        {detail.stock_name} — {total}개 의견
      </h2>

      {total > 0 && (
        <div style={{ marginBottom: '24px', background: '#fff', border: '1px solid #eee', borderRadius: '8px', padding: '16px' }}>
          <div style={{ fontSize: '13px', color: '#888', marginBottom: '8px' }}>감정 분포</div>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 40, top: 4, bottom: 4 }}>
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={32} tick={{ fontSize: 13 }} axisLine={false} tickLine={false} />
              <Tooltip formatter={(v, _, entry) => [`${v}명 (${(entry as { payload: { pct: number } }).payload.pct}%)`, '']} />
              <Bar dataKey="count" radius={4} barSize={20}>
                {chartData.map((d) => (
                  <Cell key={d.name} fill={d.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {total === 0 ? (
        <div style={{ color: '#888' }}>의견이 없습니다.</div>
      ) : (
        detail.opinions.map((op, i) => {
          const colors = SENTIMENT_COLOR[op.sentiment] ?? SENTIMENT_COLOR.neutral
          const date = op.published_at
            ? new Date(op.published_at).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
            : ''
          return (
            <div key={i} style={{ border: '1px solid #eee', borderRadius: '8px', padding: '14px 16px', marginBottom: '10px', background: '#fff' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, fontSize: '14px' }}>{op.channel_name}</span>
                <span style={{
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: colors.bg,
                  color: colors.text,
                  fontSize: '12px',
                  fontWeight: 600,
                }}>
                  {colors.label}
                </span>
                <span style={{ fontSize: '12px', color: '#aaa', marginLeft: 'auto' }}>{date}</span>
              </div>
              <div style={{ fontSize: '13px', color: '#333', lineHeight: '1.5', marginBottom: '6px' }}>{op.opinion}</div>
              <div style={{ fontSize: '12px', color: '#888' }}>
                {op.video_title_ko || op.video_title}
              </div>
            </div>
          )
        })
      )}
    </>
  )
}
