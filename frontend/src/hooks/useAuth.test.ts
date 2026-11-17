import { describe, expect, it } from 'vitest'
import { safeNext } from './useAuth'

describe('safeNext', () => {
  it('keeps same-site paths', () => {
    expect(safeNext('/copilot?job=3')).toBe('/copilot?job=3')
  })

  it.each([null, '', 'https://evil.example', '//evil.example', '/\\evil.example', 'search'])(
    'falls back to the landing page for %s',
    (next) => {
      expect(safeNext(next)).toBe('/')
    },
  )
})
