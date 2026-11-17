import { API_BASE, ApiError, errorMessage } from './client'

export type SseEvent = { event: string; data: unknown }

function parseBlock(block: string): SseEvent | null {
  let event = 'message'
  const data: string[] = []
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''))
  }
  if (data.length === 0) return null
  const raw = data.join('\n')
  try {
    return { event, data: JSON.parse(raw) }
  } catch {
    return { event: 'parse_error', data: raw }
  }
}

export function createSseParser(onEvent: (event: SseEvent) => void) {
  let buffer = ''
  return (chunk: string) => {
    buffer += chunk.replace(/\r\n/g, '\n')
    let end = buffer.indexOf('\n\n')
    while (end !== -1) {
      const parsed = parseBlock(buffer.slice(0, end))
      buffer = buffer.slice(end + 2)
      if (parsed) onEvent(parsed)
      end = buffer.indexOf('\n\n')
    }
  }
}

export async function streamSse(
  path: string,
  body: unknown,
  signal: AbortSignal,
  onEvent: (event: SseEvent) => void,
): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(body),
    signal,
  })
  if (!res.ok || !res.body) throw new ApiError(res.status, await errorMessage(res))

  const push = createSseParser(onEvent)
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader()
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    push(value)
  }
}
