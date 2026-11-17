import type { components } from './schema'

type Schemas = components['schemas']

export type JobSummary = Schemas['JobSummary']
export type JobDetail = Schemas['JobDetail']
export type JobPage = Schemas['JobPage']
export type ParsedQuery = Schemas['ParsedQuery']
export type SearchHit = Schemas['SearchHit']
export type SearchResponse = Schemas['SearchResponse']
export type ResumeOut = Schemas['ResumeOut']
export type AgentRunOut = Schemas['AgentRunOut']
export type AgentStep = Schemas['AgentStep']
export type AgentResult = Schemas['AgentResultData']
export type SkillGap = Schemas['SkillGap']
export type CoverLetter = Schemas['CoverLetter']
export type InterviewQuestion = Schemas['InterviewQuestion']
export type SkillCount = Schemas['SkillCount']
export type Overview = Schemas['Overview']
export type SkillsReport = Schemas['SkillsReport']
export type TrendReport = Schemas['TrendReport']
export type Bucket = Schemas['Bucket']
export type SkillShare = Schemas['SkillShare']
export type CooccurrenceReport = Schemas['CooccurrenceReport']
export type Language = Schemas['AgentRunRequest']['language']

export type JobQuery = {
  city?: string
  skill?: string[]
  exp_max?: number
  employment_type?: string
  q?: string
  limit?: number
  offset?: number
}

export type UserOut = { id: string; email: string }

export type SkillShareOut = { name: string; jobs: number; share: number }
export type PublicStats = {
  active_jobs: number
  new_this_week: number
  ai_ml_jobs: number
  junior_jobs: number
  top_skills: SkillShareOut[]
}
