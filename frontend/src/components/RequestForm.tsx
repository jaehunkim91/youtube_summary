import { useState } from 'react'
import { postChannelRequest } from '../api/client'

const fieldStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px',
  border: '1px solid #ddd',
  borderRadius: '4px',
  fontSize: '14px',
  boxSizing: 'border-box',
}

export function RequestForm({ onSubmitted }: { onSubmitted: () => void }) {
  const [nickname, setNickname] = useState('')
  const [channelName, setChannelName] = useState('')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<{ nickname?: string; channelName?: string }>({})

  const validate = () => {
    const errors: { nickname?: string; channelName?: string } = {}
    if (!nickname.trim()) errors.nickname = '닉네임을 입력해주세요'
    if (!channelName.trim()) errors.channelName = '유튜버 이름을 입력해주세요'
    return errors
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errors = validate()
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors)
      return
    }
    setFieldErrors({})
    setErrorMsg(null)
    setSubmitting(true)
    try {
      await postChannelRequest({
        nickname: nickname.trim(),
        channel_name: channelName.trim(),
        content: content.trim() || undefined,
      })
      setNickname('')
      setChannelName('')
      setContent('')
      setSuccessMsg('요청이 등록됐습니다!')
      onSubmitted()
      setTimeout(() => setSuccessMsg(null), 2000)
    } catch {
      setErrorMsg('제출에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '24px', background: '#fafafa', border: '1px solid #eee', borderRadius: '8px', padding: '16px' }}>
      <h3 style={{ margin: '0 0 12px', fontSize: '15px' }}>유튜버 추천하기</h3>

      <div style={{ marginBottom: '10px' }}>
        <label style={{ display: 'block', fontSize: '13px', marginBottom: '4px', color: '#555' }}>닉네임 *</label>
        <input
          value={nickname}
          onChange={e => setNickname(e.target.value)}
          maxLength={50}
          placeholder="홍길동"
          style={fieldStyle}
        />
        {fieldErrors.nickname && <div style={{ color: '#c00', fontSize: '12px', marginTop: '4px' }}>{fieldErrors.nickname}</div>}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <label style={{ display: 'block', fontSize: '13px', marginBottom: '4px', color: '#555' }}>유튜버 이름 *</label>
        <input
          value={channelName}
          onChange={e => setChannelName(e.target.value)}
          maxLength={50}
          placeholder="삼프로TV"
          style={fieldStyle}
        />
        {fieldErrors.channelName && <div style={{ color: '#c00', fontSize: '12px', marginTop: '4px' }}>{fieldErrors.channelName}</div>}
      </div>

      <div style={{ marginBottom: '12px' }}>
        <label style={{ display: 'block', fontSize: '13px', marginBottom: '4px', color: '#555' }}>하고 싶은 말 (선택)</label>
        <textarea
          value={content}
          onChange={e => setContent(e.target.value)}
          maxLength={500}
          rows={3}
          placeholder="이 채널을 추천하는 이유..."
          style={{ ...fieldStyle, resize: 'vertical' }}
        />
      </div>

      {errorMsg && <div style={{ color: '#c00', fontSize: '13px', marginBottom: '8px' }}>{errorMsg}</div>}
      {successMsg && <div style={{ color: '#2e7d32', fontSize: '13px', marginBottom: '8px' }}>{successMsg}</div>}

      <button
        type="submit"
        disabled={submitting}
        style={{
          padding: '8px 20px',
          background: submitting ? '#aaa' : '#1976d2',
          color: '#fff',
          border: 'none',
          borderRadius: '4px',
          cursor: submitting ? 'not-allowed' : 'pointer',
          fontSize: '14px',
        }}
      >
        {submitting ? '제출 중...' : '제출'}
      </button>
    </form>
  )
}
