// frontend/src/components/SummaryView.tsx
import { useState } from 'react'
import type { SummaryResponse } from '../api/client'

interface Props {
  summary: SummaryResponse
}

export function SummaryView({ summary }: Props) {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  return (
    <div style={{ padding: '16px' }}>
      <h2>{summary.video_title}</h2>
      <a
        href={summary.youtube_url}
        target="_blank"
        rel="noopener noreferrer"
        style={{ fontSize: '14px', color: '#888' }}
      >
        {summary.youtube_url}
      </a>
      <div style={{ marginTop: '16px' }}>
        {summary.chapters.map((chapter, i) => (
          <div key={chapter.id} style={{ border: '1px solid #ddd', marginBottom: '8px', borderRadius: '4px' }}>
            <button
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
              style={{
                width: '100%', textAlign: 'left', padding: '12px',
                background: 'none', border: 'none', cursor: 'pointer',
                fontSize: '15px', fontWeight: 'bold',
              }}
            >
              [{chapter.timestamp}] {chapter.title}
            </button>
            {openIndex === i && (
              <div style={{ padding: '12px', borderTop: '1px solid #ddd' }}>
                {chapter.content}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
