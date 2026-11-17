import { useId, useState, type DragEvent, type ReactNode } from 'react'
import type { ResumeOut } from '../../api/types'
import type { useResume } from '../../hooks/useResume'
import { useI18n } from '../../i18n/useI18n'
import { formatDate } from '../../lib/format'
import ConfirmDialog from '../ConfirmDialog'
import { ErrorState } from '../States'
import { focusRing, muted } from '../ui'

const MAX_BYTES = 5 * 1024 * 1024
const tag = 'rounded bg-slate-100 px-2 py-0.5 text-xs dark:bg-slate-800'

function Dropzone({ onFile, busy }: { onFile: (file: File) => void; busy: boolean }) {
  const { t } = useI18n()
  const inputId = useId()
  const [error, setError] = useState<string | null>(null)
  const [over, setOver] = useState(false)

  const accept = (file: File | undefined) => {
    if (!file) return
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf'))
      return setError(t('copilot.notPdf'))
    if (file.size > MAX_BYTES) return setError(t('copilot.tooLarge'))
    setError(null)
    onFile(file)
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setOver(false)
    accept(e.dataTransfer.files[0])
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault()
        setOver(true)
      }}
      onDragLeave={() => setOver(false)}
      onDrop={onDrop}
      className={`rounded-lg border-2 border-dashed p-6 text-center ${
        over ? 'border-brand bg-blue-50 dark:bg-blue-950' : 'border-slate-300 dark:border-slate-700'
      }`}
    >
      <p className="font-medium">{busy ? t('copilot.uploading') : t('copilot.drop')}</p>
      <p className={`mt-1 text-sm ${muted}`}>{t('copilot.dropHint')}</p>
      <label
        htmlFor={inputId}
        className={`mt-4 inline-flex min-h-11 cursor-pointer items-center rounded-md bg-brand px-4 text-sm font-medium text-white hover:bg-blue-700 has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-offset-2 has-[:focus-visible]:outline-brand ${busy ? 'pointer-events-none opacity-50' : ''}`}
      >
        {t('copilot.choose')}
        <input
          id={inputId}
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          disabled={busy}
          onChange={(e) => {
            accept(e.target.files?.[0])
            e.target.value = ''
          }}
        />
      </label>
      {error && (
        <p role="alert" className="mt-3 text-sm text-red-700 dark:text-red-300">
          {error}
        </p>
      )}
    </div>
  )
}

function Summary({ resume }: { resume: ResumeOut }) {
  const { t } = useI18n()
  const { parsed } = resume
  const languages = [
    parsed.languages?.korean,
    parsed.languages?.english,
    ...(parsed.languages?.other ?? []),
  ]
    .filter(Boolean)
    .join(', ')
  const rows: [string, ReactNode][] = [
    [
      t('copilot.skills'),
      parsed.skills?.length ? (
        <ul className="flex flex-wrap gap-1">
          {parsed.skills.map((s) => (
            <li key={s} className={tag}>
              {s}
            </li>
          ))}
        </ul>
      ) : (
        t('copilot.none')
      ),
    ],
    [t('copilot.otherSkills'), parsed.other_skills?.join(', ') || t('copilot.none')],
    [
      t('copilot.years'),
      parsed.years_experience != null
        ? t('copilot.yearsValue', { n: parsed.years_experience })
        : t('copilot.none'),
    ],
    [t('copilot.languages'), languages || t('copilot.none')],
    [t('copilot.projects'), parsed.projects?.map((p) => p.title).join(', ') || t('copilot.none')],
  ]
  return (
    <dl className="grid gap-x-4 gap-y-2 text-sm sm:grid-cols-[8rem_1fr]">
      {rows.map(([label, value]) => (
        <div key={label} className="contents">
          <dt className={muted}>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  )
}

export default function ResumePanel({ state }: { state: ReturnType<typeof useResume> }) {
  const { t, lang } = useI18n()
  const [confirming, setConfirming] = useState(false)
  const { resume, upload, remove } = state

  if (resume.data) {
    return (
      <div className="space-y-4">
        <p className="font-medium">{resume.data.filename}</p>
        <Summary resume={resume.data} />
        <p className={`text-xs ${muted}`}>
          {t('copilot.expires', { date: formatDate(resume.data.expires_at, lang) ?? '' })}
        </p>
        <button
          type="button"
          onClick={() => setConfirming(true)}
          className={`inline-flex min-h-11 items-center text-sm text-red-700 underline-offset-4 hover:underline dark:text-red-300 ${focusRing}`}
        >
          {t('copilot.delete')}
        </button>
        <ConfirmDialog
          open={confirming}
          title={t('copilot.deleteTitle')}
          body={t('copilot.deleteBody')}
          confirmLabel={t('copilot.confirmDelete')}
          onClose={() => setConfirming(false)}
          onConfirm={() => {
            setConfirming(false)
            remove.mutate(resume.data.id)
          }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <Dropzone onFile={(file) => upload.mutate(file)} busy={upload.isPending} />
      {upload.isError && <ErrorState message={upload.error.message} />}
      {resume.isError && state.resumeId && <ErrorState message={resume.error.message} />}
    </div>
  )
}
