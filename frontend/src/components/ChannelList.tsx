// frontend/src/components/ChannelList.tsx
import type { ChannelFeedItem } from '../api/client'

interface Props {
  channels: ChannelFeedItem[]
  selected: string | null
  onSelect: (name: string) => void
}

export function ChannelList({ channels, selected, onSelect }: Props) {
  if (channels.length === 0) {
    return (
      <div style={{ padding: '16px', color: '#888', fontSize: '13px' }}>
        channels.json에 채널을 추가하세요
      </div>
    )
  }

  return (
    <div>
      {channels.map((ch) => (
        <button
          key={ch.channel_url}
          onClick={() => onSelect(ch.channel_url)}
          style={{
            display: 'block',
            width: '100%',
            textAlign: 'left',
            padding: '12px 16px',
            border: 'none',
            borderBottom: '1px solid #eee',
            background: selected === ch.channel_url ? '#e8f0fe' : 'transparent',
            cursor: 'pointer',
            fontWeight: (selected === ch.channel_url ? 600 : 400) as number,
          }}
        >
          <div style={{ fontSize: '14px', color: '#1a1a1a' }}>{ch.channel_name}</div>
          <div style={{ fontSize: '12px', color: '#888', marginTop: '2px' }}>
            영상 {ch.video_count}개
          </div>
        </button>
      ))}
    </div>
  )
}
