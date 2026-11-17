import { useId, useState } from 'react'
import { useI18n } from '../i18n/useI18n'
import { focusRing } from './ui'

type Props = {
  label: string
  value: string[]
  suggestions: string[]
  onChange: (skills: string[]) => void
}

export const inputClass = `h-11 w-full rounded-md border border-slate-300 bg-white px-3 text-sm placeholder:text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:placeholder:text-slate-400 ${focusRing}`

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
      <label htmlFor={inputId} className="mb-1 block text-sm font-medium">
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
                className={`inline-flex min-h-11 items-center gap-1 rounded bg-blue-50 px-3 text-xs font-medium text-blue-800 hover:bg-blue-100 dark:bg-blue-950 dark:text-blue-200 dark:hover:bg-blue-900 ${focusRing}`}
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
