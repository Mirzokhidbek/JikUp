import { describe, expect, it } from 'vitest'
import { marketGap } from './marketGap'

const MARKET = [
  { name: 'Python', share: 58 },
  { name: 'AWS', share: 33.5 },
  { name: 'Kubernetes', share: 29.5 },
  { name: 'React', share: 19 },
]

describe('marketGap', () => {
  it('splits market skills into owned and missing, missing by demand', () => {
    const { owned, missing } = marketGap(['python', 'React', 'FastAPI'], MARKET)
    expect(owned.map((s) => s.name)).toEqual(['Python', 'React'])
    expect(missing.map((s) => s.name)).toEqual(['AWS', 'Kubernetes'])
  })

  it('handles an empty resume', () => {
    expect(marketGap([], MARKET).missing).toHaveLength(4)
  })
})
