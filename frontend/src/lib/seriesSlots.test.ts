import { describe, expect, it } from 'vitest'
import { assignSlots } from './seriesSlots'

describe('assignSlots', () => {
  it('gives new series the lowest free slot', () => {
    expect(assignSlots({}, ['Python', 'Go', 'Java'])).toEqual({ Python: 0, Go: 1, Java: 2 })
  })

  it('keeps survivors on their slot when a series is removed', () => {
    const slots = assignSlots({}, ['Python', 'Go', 'Java'])
    expect(assignSlots(slots, ['Python', 'Java'])).toEqual({ Python: 0, Java: 2 })
  })

  it('reuses a freed slot for the next new series', () => {
    expect(assignSlots({ Python: 0, Java: 2 }, ['Python', 'Java', 'Rust'])).toEqual({
      Python: 0,
      Java: 2,
      Rust: 1,
    })
  })
})
