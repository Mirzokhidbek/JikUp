import type { AgentStep } from '../../api/types'
import type { MessageKey } from '../../i18n/en'
import { useI18n } from '../../i18n/useI18n'
import { muted } from '../ui'

const TOOLS = [
  'get_resume',
  'get_job',
  'compute_skill_gap',
  'draft_cover_letter',
  'generate_interview_questions',
] as const

export default function AgentTimeline({
  steps,
  running,
}: {
  steps: AgentStep[]
  running: boolean
}) {
  const { t } = useI18n()
  const done = new Map<string, AgentStep>()
  for (const step of steps) if (step.ok) done.set(step.tool, step)
  const failed = steps.filter((s) => !s.ok).length
  const current = running ? TOOLS.find((tool) => !done.has(tool)) : undefined

  return (
    <ol className="space-y-2" aria-label={t('copilot.step3')}>
      {TOOLS.map((tool) => {
        const step = done.get(tool)
        const state = step ? 'done' : tool === current ? 'active' : 'waiting'
        return (
          <li key={tool} className="flex items-center gap-3 text-sm">
            <span
              aria-hidden="true"
              className={`flex size-6 shrink-0 items-center justify-center rounded-full text-xs ${
                state === 'done'
                  ? 'bg-green-700 text-white'
                  : state === 'active'
                    ? 'border-2 border-brand motion-safe:animate-pulse'
                    : 'border border-slate-300 dark:border-slate-700'
              }`}
            >
              {state === 'done' ? '✓' : ''}
            </span>
            <span className={state === 'waiting' ? muted : ''}>
              {t(`copilot.tool.${tool}` as MessageKey)}
              <span className="sr-only">
                {state === 'done' ? ' ✓' : state === 'active' ? ` (${t('copilot.running')})` : ''}
              </span>
            </span>
            {step && (
              <span className={`ml-auto text-xs ${muted}`}>
                {(step.ms / 1000).toFixed(1)}s{step.fallback ? ` · ${t('copilot.fallback')}` : ''}
              </span>
            )}
          </li>
        )
      })}
      {failed > 0 && <li className={`text-xs ${muted}`}>↻ {failed}</li>}
    </ol>
  )
}
