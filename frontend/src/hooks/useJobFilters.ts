import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useSearchParams } from 'react-router'
import type { JobQuery } from '../api/types'
import { PAGE_SIZE } from '../lib/constants'

export type JobFilters = {
  q: string
  city: string
  exp_max: string
  employment_type: string
  skill: string[]
  page: number
}

const KEYS = ['q', 'city', 'exp_max', 'employment_type'] as const

export function toQuery(filters: JobFilters): JobQuery {
  const exp = filters.exp_max === '' ? undefined : Number(filters.exp_max)
  return {
    q: filters.q.trim() || undefined,
    city: filters.city || undefined,
    exp_max: Number.isInteger(exp) ? exp : undefined,
    employment_type: filters.employment_type || undefined,
    skill: filters.skill.length ? filters.skill : undefined,
    limit: PAGE_SIZE,
    offset: (filters.page - 1) * PAGE_SIZE,
  }
}

export function readFilters(params: URLSearchParams): JobFilters {
  const page = Number(params.get('page'))
  return {
    q: params.get('q') ?? '',
    city: params.get('city') ?? '',
    exp_max: params.get('exp_max') ?? '',
    employment_type: params.get('employment_type') ?? '',
    skill: params.getAll('skill'),
    page: Number.isInteger(page) && page > 0 ? page : 1,
  }
}

export function writeFilters(filters: JobFilters): URLSearchParams {
  const out = new URLSearchParams()
  for (const key of KEYS) if (filters[key]) out.set(key, filters[key])
  for (const skill of filters.skill) out.append('skill', skill)
  if (filters.page > 1) out.set('page', String(filters.page))
  return out
}

export function useJobFilters() {
  const [params, setParams] = useSearchParams()
  const filters = useMemo(() => readFilters(params), [params])
  // Router navigation runs in a transition, so the URL can lag behind quick successive edits.
  const latest = useRef(params)

  useEffect(() => {
    latest.current = params
  }, [params])

  const update = useCallback(
    (patch: Partial<JobFilters>, replace = false) => {
      const next = writeFilters({ ...readFilters(latest.current), page: 1, ...patch })
      latest.current = next
      setParams(next, { replace })
    },
    [setParams],
  )

  const reset = useCallback(() => {
    latest.current = new URLSearchParams()
    setParams(latest.current)
  }, [setParams])

  return { filters, update, reset }
}
