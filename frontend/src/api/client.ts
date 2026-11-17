import type {
  AgentRunOut,
  Bucket,
  CooccurrenceReport,
  JobDetail,
  JobPage,
  JobQuery,
  Overview,
  ResumeOut,
  SearchResponse,
  SkillCount,
  SkillsReport,
  TrendReport,
} from './types'

export const API_BASE = '/api'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function errorMessage(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json()
    if (body && typeof body === 'object' && 'detail' in body && typeof body.detail === 'string') {
      return body.detail
    }
  } catch {
    // Body was not JSON; fall through to the generic message.
  }
  return `Request failed (${res.status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init)
  if (!res.ok) throw new ApiError(res.status, await errorMessage(res))
  return (res.status === 204 ? undefined : await res.json()) as T
}

function jsonPost(body: unknown): RequestInit {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }
}

export function queryString(query: Record<string, string | number | string[] | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === '') continue
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, String(item))
  }
  const text = params.toString()
  return text ? `?${text}` : ''
}

export const api = {
  getJobs: (query: JobQuery) => request<JobPage>(`/jobs${queryString(query)}`),
  getJob: (id: number) => request<JobDetail>(`/jobs/${id}`),
  getSkills: () => request<SkillCount[]>('/skills'),
  search: (query: string, limit = 10) =>
    request<SearchResponse>('/search', jsonPost({ query, limit })),
  uploadResume: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<ResumeOut>('/resumes', { method: 'POST', body: form })
  },
  getResume: (id: string) => request<ResumeOut>(`/resumes/${id}`),
  deleteResume: (id: string) => request<void>(`/resumes/${id}`, { method: 'DELETE' }),
  getAgentRun: (id: string) => request<AgentRunOut>(`/agent/runs/${id}`),
  analytics: {
    overview: () => request<Overview>('/analytics/overview'),
    skills: (days?: number, category?: string) =>
      request<SkillsReport>(`/analytics/skills${queryString({ days, category, limit: 15 })}`),
    trends: (skills: string[], weeks = 12) =>
      request<TrendReport>(
        `/analytics/trends${queryString({ skills: skills.join(',') || undefined, weeks })}`,
      ),
    experience: (days?: number) =>
      request<Bucket[]>(`/analytics/experience${queryString({ days })}`),
    cities: (days?: number) => request<Bucket[]>(`/analytics/cities${queryString({ days })}`),
    cooccurrence: (skill: string) =>
      request<CooccurrenceReport>(`/analytics/cooccurrence${queryString({ skill })}`),
  },
}
