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
