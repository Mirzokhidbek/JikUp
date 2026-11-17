import { describe, expect, it } from 'vitest'
import { queryString } from './client'
import { createSseParser, type SseEvent } from './sse'

function collect() {
  const events: SseEvent[] = []
  return { events, push: createSseParser((event) => events.push(event)) }
}

describe('createSseParser', () => {
  it('parses an event split across chunks', () => {
    const { events, push } = collect()
    push('event: tok')
    push('en\ndata: "안녕')
    push('하세요"\n\n')
    expect(events).toEqual([{ event: 'token', data: '안녕하세요' }])
  })

  it('parses several events in one chunk and keeps the remainder', () => {
    const { events, push } = collect()
    push('event: filters\ndata: {"city":"서울"}\n\nevent: done\ndata: {}\n\nevent: tok')
    expect(events.map((e) => e.event)).toEqual(['filters', 'done'])
    expect(events[0].data).toEqual({ city: '서울' })
    push('en\ndata: "x"\n\n')
    expect(events.at(-1)).toEqual({ event: 'token', data: 'x' })
  })

  it('handles CRLF line endings', () => {
    const { events, push } = collect()
    push('event: step\r\ndata: {"tool":"get_job"}\r\n\r\n')
    expect(events).toEqual([{ event: 'step', data: { tool: 'get_job' } }])
  })

  it('reports invalid JSON instead of throwing', () => {
    const { events, push } = collect()
    push('event: token\ndata: not-json\n\n')
    expect(events).toEqual([{ event: 'parse_error', data: 'not-json' }])
  })

  it('ignores blocks without data', () => {
    const { events, push } = collect()
    push(': keep-alive\n\n')
    expect(events).toEqual([])
  })
})

describe('queryString', () => {
  it('repeats list params and skips empty values', () => {
    expect(queryString({ city: '서울', skill: ['Python', 'Go'], q: '', exp_max: 0 })).toBe(
      '?city=%EC%84%9C%EC%9A%B8&skill=Python&skill=Go&exp_max=0',
    )
    expect(queryString({})).toBe('')
  })
})
