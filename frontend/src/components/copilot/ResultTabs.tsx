import { useId, useRef, useState, type KeyboardEvent } from 'react'
import type { AgentResult } from '../../api/types'
import { useI18n } from '../../i18n/useI18n'
import { focusRing } from '../ui'
import CoverLetterTab from './CoverLetterTab'
import InterviewTab from './InterviewTab'
import SkillGapTab from './SkillGapTab'

const TABS = ['gap', 'letter', 'interview'] as const
type Tab = (typeof TABS)[number]

export default function ResultTabs({
  result,
  jobTitle,
}: {
  result: AgentResult
  jobTitle: string
}) {
  const { t } = useI18n()
  const base = useId()
  const [active, setActive] = useState<Tab>('gap')
  const refs = useRef<Record<Tab, HTMLButtonElement | null>>({
    gap: null,
    letter: null,
    interview: null,
  })
  const labels: Record<Tab, string> = {
    gap: t('copilot.tabGap'),
    letter: t('copilot.tabLetter'),
    interview: t('copilot.tabInterview'),
  }

  const onKeyDown = (e: KeyboardEvent) => {
    const index = TABS.indexOf(active)
    const next =
      e.key === 'ArrowRight'
        ? TABS[(index + 1) % TABS.length]
        : e.key === 'ArrowLeft'
          ? TABS[(index + TABS.length - 1) % TABS.length]
          : e.key === 'Home'
            ? TABS[0]
            : e.key === 'End'
              ? TABS[TABS.length - 1]
              : null
    if (!next) return
    e.preventDefault()
    setActive(next)
    refs.current[next]?.focus()
  }

  return (
    <div>
      <div
        role="tablist"
        aria-label={t('copilot.step3')}
        onKeyDown={onKeyDown}
        className="flex gap-1 border-b border-slate-200 dark:border-slate-800"
      >
        {TABS.map((tab) => (
          <button
            key={tab}
            ref={(el) => {
              refs.current[tab] = el
            }}
            id={`${base}-tab-${tab}`}
            role="tab"
            type="button"
            aria-selected={active === tab}
            aria-controls={`${base}-panel-${tab}`}
            tabIndex={active === tab ? 0 : -1}
            onClick={() => setActive(tab)}
            className={`-mb-px min-h-11 border-b-2 px-4 text-sm font-medium ${focusRing} ${
              active === tab
                ? 'border-brand text-blue-700 dark:border-blue-400 dark:text-blue-300'
                : 'border-transparent text-slate-600 hover:text-ink dark:text-slate-400 dark:hover:text-white'
            }`}
          >
            {labels[tab]}
          </button>
        ))}
      </div>
      {TABS.map((tab) => (
        <div
          key={tab}
          id={`${base}-panel-${tab}`}
          role="tabpanel"
          aria-labelledby={`${base}-tab-${tab}`}
          hidden={active !== tab}
          tabIndex={0}
          className={`pt-4 ${focusRing}`}
        >
          {tab === 'gap' && <SkillGapTab gap={result.gap} summary={result.summary} />}
          {tab === 'letter' && <CoverLetterTab letter={result.cover_letter} jobTitle={jobTitle} />}
          {tab === 'interview' && <InterviewTab questions={result.interview.questions} />}
        </div>
      ))}
    </div>
  )
}
