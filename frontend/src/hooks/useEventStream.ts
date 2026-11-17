import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client'
import { streamSse, type SseEvent } from '../api/sse'

export type StreamStatus = 'idle' | 'streaming' | 'done' | 'error' | 'stopped'

export function useEventStream() {
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
        setError(err instanceof ApiError ? err.message : 'Connection lost')
        setStatus('error')
      }
    },
    [],
  )

  const stop = useCallback(() => controller.current?.abort(), [])

  useEffect(() => () => controller.current?.abort(), [])

  return { status, error, start, stop }
}
