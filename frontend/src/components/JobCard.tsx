import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { JobSummary } from '../api/types'
import { useI18n } from '../i18n/useI18n'
import { employmentLabel, experienceLabel, formatDate } from '../lib/format'
import { card, focusRing, link, muted } from './ui'

const chip = 'rounded px-2 py-0.5 text-xs'

export function DemoBadge() {
  const { t } = useI18n()
  return (
    <span
      title={t('common.demoHint')}
      className="rounded border border-amber-300 bg-amber-50 px-1.5 py-0.5 text-xs font-medium text-amber-800 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200"
    >
      {t('common.demo')}
      <span className="sr-only">: {t('common.demoHint')}</span>
    </span>
  )
}

export default function JobCard({ job, children }: { job: JobSummary; children?: ReactNode }) {
  const { t, lang } = useI18n()
  const location = [job.location_city, job.location_district].filter(Boolean).join(' ')
  const deadline = formatDate(job.deadline_at, lang)
  const facts = [
    location,
    experienceLabel(job, t),
    employmentLabel(job.employment_type, t),
    deadline && t('job.deadline', { date: deadline }),
  ].filter(Boolean)

  return (
    <article className={`${card} p-4`}>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="font-semibold leading-snug">{job.title}</h2>
          <p className={`mt-0.5 text-sm ${muted}`}>{job.company ?? '-'}</p>
        </div>
        {job.source === 'seed' && <DemoBadge />}
      </div>
      <p className={`mt-2 text-sm ${muted}`}>{facts.join(' · ')}</p>
      {job.skills.length > 0 && (
        <ul className="mt-3 flex flex-wrap gap-1.5">
          {job.skills.map((skill) => (
            <li
              key={skill.name}
              className={
                skill.required
                  ? `${chip} bg-blue-50 font-medium text-blue-800 dark:bg-blue-950 dark:text-blue-200`
                  : `${chip} bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300`
              }
            >
              {skill.name}
              {skill.required && <span className="sr-only"> ({t('job.required')})</span>}
            </li>
          ))}
        </ul>
      )}
      {children}
      <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
        <Link
          to={`/copilot?job=${job.id}`}
          className={`inline-flex min-h-11 items-center rounded-md bg-brand px-4 font-medium text-white hover:bg-blue-700 ${focusRing}`}
        >
          {t('job.analyze')}
        </Link>
        {job.url && (
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex min-h-11 items-center ${link}`}
          >
            {t('job.source')}
          </a>
        )}
      </div>
    </article>
  )
}
