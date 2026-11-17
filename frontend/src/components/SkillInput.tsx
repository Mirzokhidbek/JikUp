import { useId, useState } from 'react'
import { useI18n } from '../i18n/useI18n'
import { focusRing } from './ui'

type Props = {
  label: string
  value: string[]
  suggestions: string[]
  onChange: (skills: string[]) => void
}

export const inputClass = `h-11 w-full rounded-lg bg-fill-strong px-3 text-sm placeholder:text-slate-500 dark:placeholder:text-slate-400 ${focusRing}`

export default function SkillInput({ label, value, suggestions, onChange }: Props) {
  const { t } = useI18n()
  const [draft, setDraft] = useState('')
  const inputId = useId()
  const listId = useId()

  const add = () => {
    const skill = draft.trim()
    if (skill && !value.some((s) => s.toLowerCase() === skill.toLowerCase())) {
      onChange([...value, skill])
    }
    setDraft('')
  }

  return (
    <div>
      <label
        htmlFor={inputId}
        className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        {label}
      </label>
      <input
        id={inputId}
        list={listId}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            add()
          }
        }}
        placeholder={t('search.skillsPlaceholder')}
        className={inputClass}
        autoComplete="off"
      />
      <datalist id={listId}>
        {suggestions.map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>
      {value.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {value.map((skill) => (
            <li key={skill}>
              <button
                type="button"
                onClick={() => onChange(value.filter((s) => s !== skill))}
                aria-label={t('search.removeSkill', { skill })}
                className={`inline-flex min-h-11 items-center gap-1 rounded-full bg-ink px-3 text-xs font-medium text-white hover:bg-ink/85 dark:bg-white dark:text-ink dark:hover:bg-white/85 ${focusRing}`}
              >
                {skill}
                <span aria-hidden="true">×</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
