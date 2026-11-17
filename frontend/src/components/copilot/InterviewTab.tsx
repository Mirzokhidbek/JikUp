import type { InterviewQuestion } from '../../api/types'
import type { MessageKey } from '../../i18n/en'
import { useI18n } from '../../i18n/useI18n'
import { card, focusRing, muted } from '../ui'

const CATEGORY_STYLE: Record<string, string> = {
  technical: 'bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-200',
  behavioral: 'bg-violet-50 text-violet-800 dark:bg-violet-950 dark:text-violet-200',
  gap: 'bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
}

export default function InterviewTab({ questions }: { questions: InterviewQuestion[] }) {
  const { t } = useI18n()
  return (
    <ol className="space-y-2">
      {questions.map((q, i) => {
        const known = q.category in CATEGORY_STYLE
        return (
          <li key={i}>
            <details className={`${card} group`}>
              <summary
                className={`flex min-h-11 cursor-pointer list-none items-start gap-3 p-3 ${focusRing}`}
              >
                <span className={`mt-0.5 text-sm ${muted}`}>{i + 1}.</span>
                <span className="flex-1 text-sm" lang="ko">
                  {q.question}
                </span>
                <span
                  className={`shrink-0 rounded px-2 py-0.5 text-xs ${CATEGORY_STYLE[q.category] ?? ''}`}
                >
                  {known ? t(`copilot.category.${q.category}` as MessageKey) : q.category}
                </span>
              </summary>
              <div className="border-t border-slate-200 p-3 text-sm dark:border-slate-800">
                <p className="mb-1 font-medium">{t('copilot.direction')}</p>
                <p lang="ko" className={muted}>
                  {q.answer_direction}
                </p>
              </div>
            </details>
          </li>
        )
      })}
    </ol>
  )
}
