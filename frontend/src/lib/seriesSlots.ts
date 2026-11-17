export const SERIES_COLORS = [
  'var(--series-1)',
  'var(--series-2)',
  'var(--series-3)',
  'var(--series-4)',
  'var(--series-5)',
]

export type Slots = Record<string, number>

/** Keeps every surviving series on its slot and gives new ones the lowest free slot. */
export function assignSlots(previous: Slots, series: string[]): Slots {
  const next: Slots = {}
  for (const name of series) if (name in previous) next[name] = previous[name]
  const used = new Set(Object.values(next))
  for (const name of series) {
    if (name in next) continue
    let slot = 0
    while (used.has(slot)) slot++
    next[name] = slot
    used.add(slot)
  }
  return next
}

export function colorFor(slots: Slots, name: string): string {
  return SERIES_COLORS[(slots[name] ?? 0) % SERIES_COLORS.length]
}
