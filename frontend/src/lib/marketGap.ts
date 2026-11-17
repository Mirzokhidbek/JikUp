export type MarketSkill = { name: string; share: number }

export function marketGap(resumeSkills: string[], market: MarketSkill[]) {
  const have = new Set(resumeSkills.map((s) => s.toLowerCase()))
  const owned = market.filter((s) => have.has(s.name.toLowerCase()))
  const missing = market
    .filter((s) => !have.has(s.name.toLowerCase()))
    .sort((a, b) => b.share - a.share)
  return { owned, missing }
}
