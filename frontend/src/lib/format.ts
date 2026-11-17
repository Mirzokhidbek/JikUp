import type { JobSummary } from '../api/types'
import type { Lang, Translate } from '../i18n/context'
import { EMPLOYMENT_TYPES, type EmploymentType } from './constants'

export function experienceLabel(
  job: Pick<JobSummary, 'experience_min' | 'experience_max'>,
  t: Translate,
) {
  const { experience_min: min, experience_max: max } = job
  if (min === null || min === undefined) return t('job.experienceAny')
  if (min === 0 && max === 0) return t('job.experienceNew')
  if (max !== null && max !== undefined) return t('job.experienceRange', { min, max })
  return t('job.experienceMin', { min })
}

export function employmentLabel(value: string | null | undefined, t: Translate) {
  if (!value) return null
  return (EMPLOYMENT_TYPES as readonly string[]).includes(value)
    ? t(`employment.${value as EmploymentType}`)
    : value
}

export function formatDate(value: string | null | undefined, lang: Lang) {
  if (!value) return null
  return new Intl.DateTimeFormat(lang, { month: 'short', day: 'numeric' }).format(new Date(value))
}
