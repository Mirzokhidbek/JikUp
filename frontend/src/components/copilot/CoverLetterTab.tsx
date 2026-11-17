import { useId, useState } from 'react'
import type { CoverLetter } from '../../api/types'
import { SECTIONS, letterFilename, letterText } from '../../lib/letter'
import type { MessageKey } from '../../i18n/en'
import { useI18n } from '../../i18n/useI18n'
import { focusRing, muted } from '../ui'

const button = `inline-flex min-h-11 items-center rounded-md border border-slate-300 px-4 text-sm font-medium hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800 ${focusRing}`

export default function CoverLetterTab({
  letter,
  jobTitle,
}: {
  letter: CoverLetter
  jobTitle: string
}) {
  const { t } = useI18n()
  const base = useId()
  const [draft, setDraft] = useState<CoverLetter>(letter)
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    await navigator.clipboard.writeText(letterText(draft))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const download = () => {
    const url = URL.createObjectURL(
      new Blob([letterText(draft)], { type: 'text/plain;charset=utf-8' }),
    )
    const a = document.createElement('a')
    a.href = url
    a.download = letterFilename(jobTitle)
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4">
      <p className={`text-sm ${muted}`}>{t('copilot.letterNote')}</p>
      {SECTIONS.map((key) => (
        <div key={key}>
          <div className="mb-1 flex items-baseline justify-between">
            <label htmlFor={`${base}-${key}`} className="text-sm font-medium">
              {t(`copilot.letter.${key}` as MessageKey)}
            </label>
            <span className={`text-xs ${muted}`} aria-live="polite">
              {t('copilot.chars', { n: draft[key].length })}
            </span>
          </div>
          <textarea
            id={`${base}-${key}`}
            lang="ko"
            value={draft[key]}
            onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
            rows={7}
            className={`w-full resize-y rounded-md border border-slate-300 bg-white p-3 text-sm leading-relaxed dark:border-slate-700 dark:bg-slate-900 ${focusRing}`}
          />
        </div>
      ))}
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={() => void copy()} className={button}>
          <span aria-live="polite">{copied ? t('copilot.copied') : t('copilot.copy')}</span>
        </button>
        <button type="button" onClick={download} className={button}>
          {t('copilot.download')}
        </button>
      </div>
    </div>
  )
}
