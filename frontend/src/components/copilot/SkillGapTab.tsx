import type { SkillGap } from '../../api/types'
import type { MessageKey } from '../../i18n/en'
import { useI18n } from '../../i18n/useI18n'
import { muted } from '../ui'

function SkillList({
  title,
  skills,
  have,
}: {
  title: MessageKey
  skills: string[]
  have: boolean
}) {
  const { t } = useI18n()
  if (skills.length === 0) return null
  return (
    <section>
      <h3 className="mb-1.5 text-sm font-medium">{t(title)}</h3>
      <ul className="flex flex-wrap gap-1.5">
        {skills.map((skill) => (
          <li
            key={skill}
            className={`rounded px-2 py-0.5 text-sm ${
              have
                ? 'bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200'
                : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
            }`}
          >
            <span aria-hidden="true">{have ? '✓ ' : '✗ '}</span>
            {skill}
          </li>
        ))}
      </ul>
    </section>
  )
}

export default function SkillGapTab({ gap, summary }: { gap: SkillGap; summary: string }) {
  const { t } = useI18n()
  const percent = gap.match_percent
  const have = gap.experience_years
  const need = gap.experience_required

  return (
    <div className="space-y-5">
      {percent == null ? (
        <p className={muted}>{t('copilot.matchNone')}</p>
      ) : (
        <div>
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-medium">{t('copilot.match')}</span>
            <span className="text-2xl font-semibold">{percent}%</span>
          </div>
          <div
            role="progressbar"
            aria-label={t('copilot.match')}
            aria-valuenow={percent}
            aria-valuemin={0}
            aria-valuemax={100}
            className="mt-2 h-2.5 overflow-hidden rounded bg-slate-200 dark:bg-slate-800"
          >
            <div className="h-full bg-brand dark:bg-blue-400" style={{ width: `${percent}%` }} />
          </div>
        </div>
      )}
      <SkillList title="copilot.requiredMissing" skills={gap.required_missing} have={false} />
      <SkillList title="copilot.requiredHave" skills={gap.required_matched} have />
      <SkillList title="copilot.preferredMissing" skills={gap.preferred_missing} have={false} />
      <SkillList title="copilot.preferredHave" skills={gap.preferred_matched} have />
      {need != null && have != null && (
        <p className="text-sm">
          {gap.experience_gap
            ? t('copilot.expGap', { have, need })
            : t('copilot.expOk', { have, need })}
        </p>
      )}
      {summary && (
        <section className="rounded-md bg-slate-50 p-4 dark:bg-slate-900">
          <h3 className="mb-1 text-sm font-medium">{t('copilot.summary')}</h3>
          <p className="text-sm leading-relaxed whitespace-pre-line">{summary}</p>
        </section>
      )}
    </div>
  )
}
