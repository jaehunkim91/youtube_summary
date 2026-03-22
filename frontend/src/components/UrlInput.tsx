// frontend/src/components/UrlInput.tsx
import { useState } from 'react'

interface Props {
  onSubmit: (url: string) => void
  isLoading: boolean
}

export function UrlInput({ onSubmit, isLoading }: Props) {
  const [url, setUrl] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) onSubmit(url.trim())
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px', padding: '16px' }}>
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="YouTube URL을 입력하세요"
        disabled={isLoading}
        style={{ flex: 1, padding: '8px', fontSize: '16px' }}
      />
      <button type="submit" disabled={isLoading || !url.trim()}>
        {isLoading ? '처리 중...' : '요약하기'}
      </button>
    </form>
  )
}
