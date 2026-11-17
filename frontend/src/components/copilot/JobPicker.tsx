import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useId, useState } from 'react'
import { api } from '../../api/client'
import type { JobSummary } from '../../api/types'
import { useDebouncedValue } from '../../hooks/useDebouncedValue'
import { useI18n } from '../../i18n/useI18n'
import { experienceLabel } from '../../lib/format'
import { DemoBadge } from '../JobCard'
import { inputClass } from '../SkillInput'
import { card, focusRing, link, muted } from '../ui'

type Props = { selected: JobSummary | null; onSelect: (job: JobSummary | null) => void }

function JobLine({ job }: { job: JobSummary }) {
  const { t } = useI18n()
  return (
    <div className="min-w-0 text-left">
      <p className="flex items-center gap-2 font-medium">
        <span className="truncate">{job.title}</span>
        {job.source === 'seed' && <DemoBadge />}
      </p>
      <p className={`text-sm ${muted}`}>
        {[job.company, job.location_city, experienceLabel(job, t)].filter(Boolean).join(' · ')}
      </p>
    </div>
  )
}

export default function JobPicker({ selected, onSelect }: Props) {
  const { t } = useI18n()
  const inputId = useId()
  const [q, setQ] = useState('')
  const query = useDebouncedValue(q.trim())
  const jobs = useQuery({
    queryKey: ['jobs', { q: query, limit: 8 }],
    queryFn: () => api.getJobs({ q: query || undefined, limit: 8 }),
    placeholderData: keepPreviousData,
    enabled: selected === null,
  })

  if (selected) {
    return (
      <div className="space-y-2">
        <div className={`${card} p-3`}>
          <JobLine job={selected} />
        </div>
        <button
          type="button"
          onClick={() => onSelect(null)}
          className={`inline-flex min-h-11 items-center text-sm ${link}`}
        >
          {t('copilot.change')}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div>
        <label
          htmlFor={inputId}
          className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          {t('copilot.jobSearch')}
        </label>
        <input
          id={inputId}
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={t('copilot.jobSearchPlaceholder')}
          maxLength={100}
          className={inputClass}
        />
      </div>
      {jobs.data?.items.length === 0 ? (
        <p className={`text-sm ${muted}`}>{t('copilot.noJobs')}</p>
      ) : (
        <ul className="max-h-96 space-y-2 overflow-y-auto">
          {jobs.data?.items.map((job) => (
            <li key={job.id}>
              <button
                type="button"
                onClick={() => onSelect(job)}
                aria-label={`${t('copilot.select')}: ${job.title}`}
                className={`${card} flex min-h-11 w-full items-center justify-between gap-3 p-3 text-left transition-colors hover:bg-fill-strong ${focusRing}`}
              >
                <JobLine job={job} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
