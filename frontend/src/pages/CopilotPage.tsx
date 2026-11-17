import { useQuery } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { useSearchParams } from 'react-router'
import { api } from '../api/client'
import type { AgentResult, AgentStep, JobSummary } from '../api/types'
import AgentTimeline from '../components/copilot/AgentTimeline'
import JobPicker from '../components/copilot/JobPicker'
import ResultTabs from '../components/copilot/ResultTabs'
import ResumePanel from '../components/copilot/ResumePanel'
import Page from '../components/Page.tsx'
import { ErrorState } from '../components/States'
import { card, focusRing, muted } from '../components/ui'
import { useEventStream } from '../hooks/useEventStream'
import { useResume } from '../hooks/useResume'
import { useI18n } from '../i18n/useI18n'

function Step({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className={`${card} min-w-0 p-5`} aria-label={title}>
      <h2 className="mb-4 font-semibold">{title}</h2>
      {children}
    </section>
  )
}

export default function CopilotPage() {
  const { t, lang } = useI18n()
  const resumeState = useResume()
  const [params, setParams] = useSearchParams()
  const jobParam = Number(params.get('job'))
  const linkedJob = useQuery({
    queryKey: ['job', jobParam],
    queryFn: () => api.getJob(jobParam),
    enabled: Number.isInteger(jobParam) && jobParam > 0,
  })
  const [picked, setPicked] = useState<JobSummary | null | undefined>(undefined)
  const job = picked === undefined ? (linkedJob.data ?? null) : picked

  const stream = useEventStream()
  const [steps, setSteps] = useState<AgentStep[]>([])
  const [result, setResult] = useState<AgentResult | null>(null)
  const [failed, setFailed] = useState(false)
  const running = stream.status === 'streaming'
  const resume = resumeState.resume.data

  const clearRun = () => {
    setSteps([])
    setResult(null)
    setFailed(false)
  }

  const selectJob = (next: JobSummary | null) => {
    setPicked(next)
    setParams(next ? { job: String(next.id) } : {}, { replace: true })
    clearRun()
  }

  const run = () => {
    if (!resume || !job || running) return
    clearRun()
    void stream.start(
      '/agent/run',
      { resume_id: resume.id, job_id: job.id, language: lang },
      ({ event, data }) => {
        if (event === 'step') setSteps((all) => [...all, data as AgentStep])
        else if (event === 'result') setResult(data as AgentResult)
        else if (event === 'error') setFailed(true)
      },
    )
  }

  return (
    <Page title={t('nav.copilot')}>
      <p className={`mt-1 ${muted}`}>{t('copilot.subtitle')}</p>
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Step title={t('copilot.step1')}>
          <ResumePanel state={resumeState} />
        </Step>
        <Step title={t('copilot.step2')}>
          <JobPicker selected={job} onSelect={selectJob} />
        </Step>
      </div>

      <div className="mt-6">
        <Step title={t('copilot.step3')}>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={run}
              disabled={!resume || !job || running}
              className={`inline-flex min-h-11 items-center rounded-md bg-brand px-5 font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 ${focusRing}`}
            >
              {running ? t('copilot.running') : t('copilot.run')}
            </button>
            <p className={`text-sm ${muted}`}>
              {resume && job ? t('copilot.runHint') : t('copilot.needBoth')}
            </p>
          </div>
          {resume && (running || steps.length > 0) && (
            <div className="mt-5" aria-live="polite">
              <AgentTimeline steps={steps} running={running} />
            </div>
          )}
          {(failed || stream.status === 'error') && (
            <div className="mt-5">
              <ErrorState message={stream.error ?? t('copilot.failed')} onRetry={run} />
            </div>
          )}
          {result && job && resume && (
            <div className="mt-6">
              <ResultTabs result={result} jobTitle={job.title} />
            </div>
          )}
        </Step>
      </div>
    </Page>
  )
}
