import { useEffect, useId, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { useDebouncedValue } from '../hooks/useDebouncedValue'
import type { JobFilters } from '../hooks/useJobFilters'
import { useI18n } from '../i18n/useI18n'
import { CITIES, EMPLOYMENT_TYPES, EXPERIENCE_OPTIONS } from '../lib/constants'
import { employmentLabel } from '../lib/format'
import SkillInput, { inputClass } from './SkillInput'
import { link } from './ui'

type Props = {
  filters: JobFilters
  onChange: (patch: Partial<JobFilters>, replace?: boolean) => void
  onReset: () => void
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  options: { value: string; label: string }[]
}) {
  const { t } = useI18n()
  const id = useId()
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
      >
        {label}
      </label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputClass}
      >
        <option value="">{t('common.any')}</option>
        {options.map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  )
}

export default function SearchFilters({ filters, onChange, onReset }: Props) {
  const { t } = useI18n()
  const keywordId = useId()
  const [keyword, setKeyword] = useState(filters.q)
  const debounced = useDebouncedValue(keyword)
  const skills = useQuery({ queryKey: ['skills'], queryFn: api.getSkills, staleTime: 3_600_000 })

  useEffect(() => {
    if (debounced !== filters.q) onChange({ q: debounced }, true)
  }, [debounced, filters.q, onChange])

  const hasFilters =
    filters.q || filters.city || filters.exp_max || filters.employment_type || filters.skill.length

  return (
    <form
      aria-label={t('search.filters')}
      onSubmit={(e) => e.preventDefault()}
      className="space-y-5"
    >
      <div>
        <label
          htmlFor={keywordId}
          className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
        >
          {t('search.keyword')}
        </label>
        <input
          id={keywordId}
          type="search"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder={t('search.keywordPlaceholder')}
          maxLength={100}
          className={inputClass}
        />
      </div>
      <Select
        label={t('search.city')}
        value={filters.city}
        onChange={(city) => onChange({ city })}
        options={CITIES.map((c) => ({ value: c, label: c }))}
      />
      <Select
        label={t('search.experience')}
        value={filters.exp_max}
        onChange={(exp_max) => onChange({ exp_max })}
        options={EXPERIENCE_OPTIONS.map((n) => ({
          value: String(n),
          label: n === 0 ? t('search.experience.0') : t('search.experience.n', { n }),
        }))}
      />
      <Select
        label={t('search.employment')}
        value={filters.employment_type}
        onChange={(employment_type) => onChange({ employment_type })}
        options={EMPLOYMENT_TYPES.map((e) => ({ value: e, label: employmentLabel(e, t) ?? e }))}
      />
      <SkillInput
        label={t('search.skills')}
        value={filters.skill}
        suggestions={(skills.data ?? []).map((s) => s.name)}
        onChange={(skill) => onChange({ skill })}
      />
      {hasFilters ? (
        <button
          type="button"
          onClick={() => {
            setKeyword('')
            onReset()
          }}
          className={`inline-flex min-h-11 items-center text-sm ${link}`}
        >
          {t('search.reset')}
        </button>
      ) : null}
    </form>
  )
}
