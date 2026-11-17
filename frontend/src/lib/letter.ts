import type { CoverLetter } from '../api/types'

export const SECTIONS = ['motivation', 'competency', 'projects', 'aspiration'] as const
const HEADINGS: Record<(typeof SECTIONS)[number], string> = {
  motivation: '지원동기',
  competency: '직무 역량',
  projects: '프로젝트 경험',
  aspiration: '입사 후 포부',
}
export function letterText(letter: CoverLetter): string {
  return SECTIONS.map((key) => `[${HEADINGS[key]}]\n${letter[key].trim()}`).join('\n\n')
}

export function letterFilename(title: string): string {
  const cleaned = title
    .replace(/[\\/:*?"<>|]+/g, ' ')
    .trim()
    .slice(0, 60)
  return `자기소개서 - ${cleaned || 'JikUp'}.txt`
}
