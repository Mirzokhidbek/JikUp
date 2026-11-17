import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client'
import { streamSse, type SseEvent } from '../api/sse'
import { useI18n } from '../i18n/useI18n'

export type StreamStatus = 'idle' | 'streaming' | 'done' | 'error' | 'stopped'

export function useEventStream() {
  const { t } = useI18n()
  const [status, setStatus] = useState<StreamStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const controller = useRef<AbortController | null>(null)

  const start = useCallback(
    async (path: string, body: unknown, onEvent: (event: SseEvent) => void) => {
      controller.current?.abort()
      const current = new AbortController()
      controller.current = current
      setStatus('streaming')
      setError(null)
      try {
        await streamSse(path, body, current.signal, onEvent)
        if (!current.signal.aborted) setStatus('done')
      } catch (err) {
        if (current.signal.aborted) {
          setStatus('stopped')
          return
        }
        if (err instanceof ApiError) {
          const known = { 429: 'common.rateLimited', 503: 'common.llmOff' } as const
          const key = known[err.status as keyof typeof known]
          setError(key ? t(key) : err.message)
        } else {
          setError(t('common.error'))
        }
        setStatus('error')
      }
    },
    [t],
  )

  const stop = useCallback(() => controller.current?.abort(), [])

  useEffect(() => () => controller.current?.abort(), [])

  return { status, error, start, stop }
}
