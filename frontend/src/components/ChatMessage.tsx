import { Link } from 'react-router'
import type { ParsedQuery, SearchHit } from '../api/types'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { employmentLabel, experienceLabel } from '../lib/format'
import AnswerText from './AnswerText'
import { DemoBadge } from './JobCard'
import { card, focusRing, link, muted } from './ui'

export type ChatTurn = {
  id: number
  question: string
  filters?: ParsedQuery & { relaxed: string[] }
  sources?: SearchHit[]
  answer: string
  status: 'searching' | 'answering' | 'done' | 'stopped' | 'error'
  error?: string
}

const chipClass =
  'rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700 dark:bg-slate-800 dark:text-slate-300'

function FilterChips({ filters }: { filters: NonNullable<ChatTurn['filters']> }) {
  const { t } = useI18n()
  const chips = [
    filters.city,
    ...(filters.skills ?? []),
    filters.experience_max != null && t('chat.expMax', { n: filters.experience_max }),
    employmentLabel(filters.employment_type, t),
  ].filter((chip): chip is string => Boolean(chip))
  const relaxed = filters.relaxed.map((field) => t(`chat.field.${field}` as MessageKey)).join(', ')

  return (
    <div className="space-y-1">
      {chips.length > 0 && (
        <p className={`flex flex-wrap items-center gap-1.5 text-xs ${muted}`}>
          <span>{t('chat.filters')}:</span>
          {chips.map((chip) => (
            <span key={chip} className={chipClass}>
              {chip}
            </span>
          ))}
        </p>
      )}
      {relaxed && (
        <p className="text-xs text-amber-800 dark:text-amber-300">
          {t('chat.relaxed', { fields: relaxed })}
        </p>
      )}
    </div>
  )
}

function Sources({ sources, anchorPrefix }: { sources: SearchHit[]; anchorPrefix: string }) {
  const { t } = useI18n()
  if (sources.length === 0) return <p className={`text-sm ${muted}`}>{t('chat.noSources')}</p>
  return (
    <section>
      <h3 className={`mb-2 text-xs font-medium tracking-wide uppercase ${muted}`}>
        {t('chat.sources')}
      </h3>
      <ol className="grid gap-2 sm:grid-cols-2">
        {sources.map(({ job }, i) => (
          <li
            key={job.id}
            id={`${anchorPrefix}-${job.id}`}
            className={`${card} scroll-mt-24 p-3 text-sm target:ring-2 target:ring-brand`}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="font-medium">
                <span className={muted}>[{i + 1}]</span> {job.title}
              </p>
              {job.source === 'seed' && <DemoBadge />}
            </div>
            <p className={`mt-0.5 ${muted}`}>
              {[job.company, job.location_city, experienceLabel(job, t)]
                .filter(Boolean)
                .join(' · ')}
            </p>
            <Link
              to={`/copilot?job=${job.id}`}
              className={`mt-1 inline-flex min-h-11 items-center ${link} ${focusRing}`}
            >
              {t('job.analyze')}
            </Link>
          </li>
        ))}
      </ol>
    </section>
  )
}

export default function ChatMessage({ turn }: { turn: ChatTurn }) {
  const { t } = useI18n()
  const anchorPrefix = `turn-${turn.id}-job`
  const busy = turn.status === 'searching' || turn.status === 'answering'

  return (
    <li className="space-y-3">
      <div className="ml-auto max-w-[85%] rounded-lg bg-brand px-4 py-2 text-white">
        <span className="sr-only">{t('chat.you')}: </span>
        <p className="whitespace-pre-wrap">{turn.question}</p>
      </div>
      <article className={`${card} space-y-4 p-4`} aria-busy={busy}>
        <span className="sr-only">{t('chat.assistant')}:</span>
        {turn.filters && <FilterChips filters={turn.filters} />}
        {turn.status === 'searching' && (
          <p className={`text-sm ${muted} motion-safe:animate-pulse`}>{t('chat.thinking')}</p>
        )}
        {turn.answer && (
          <AnswerText text={turn.answer} sources={turn.sources ?? []} anchorPrefix={anchorPrefix} />
        )}
        {turn.status === 'stopped' && <p className={`text-sm ${muted}`}>{t('chat.stopped')}</p>}
        {turn.status === 'error' && (
          <p role="alert" className="text-sm text-red-700 dark:text-red-300">
            {turn.error ?? t('chat.answerFailed')}
          </p>
        )}
        {turn.sources && <Sources sources={turn.sources} anchorPrefix={anchorPrefix} />}
      </article>
    </li>
  )
}
