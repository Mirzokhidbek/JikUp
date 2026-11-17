import type { ReactNode } from 'react'
import { Link } from 'react-router'
import type { JobSummary } from '../api/types'
import { useI18n } from '../i18n/useI18n'
import { employmentLabel, experienceLabel, formatDate } from '../lib/format'
import { card, chip, link, muted, primaryButton } from './ui'

export function DemoBadge() {
  const { t } = useI18n()
  return (
    <span
      title={t('common.demoHint')}
      className="rounded-md bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-900 dark:bg-amber-400/15 dark:text-amber-200"
    >
      {t('common.demo')}
      <span className="sr-only">: {t('common.demoHint')}</span>
    </span>
  )
}

function CompanyMark({ name }: { name: string | null }) {
  const initial = (name ?? '?')
    .replace(/^\(주\)|㈜/, '')
    .trim()
    .charAt(0)
  return (
    <span
      aria-hidden="true"
      className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-fill-strong text-base font-semibold text-slate-700 dark:text-slate-200"
    >
      {initial || '?'}
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
    <article className={`${card} p-5`}>
      <div className="flex items-start gap-4">
        <CompanyMark name={job.company} />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <h2 className="leading-snug font-semibold">{job.title}</h2>
            {job.source === 'seed' && <DemoBadge />}
          </div>
          <p className={`mt-0.5 text-sm ${muted}`}>
            {job.company ?? '-'}
            <span aria-hidden="true"> · </span>
            {facts.join(' · ')}
          </p>
          {job.skills.length > 0 && (
            <ul className="mt-3 flex flex-wrap gap-1.5">
              {job.skills.map((skill) => (
                <li
                  key={skill.name}
                  className={
                    skill.required
                      ? `${chip} bg-fill-strong font-medium text-ink dark:text-white`
                      : `${chip} text-slate-600 ring-1 ring-ink/10 ring-inset dark:text-slate-400 dark:ring-white/10`
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
            <Link to={`/copilot?job=${job.id}`} className={primaryButton}>
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
        </div>
      </div>
    </article>
  )
}
