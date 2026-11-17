export const CITIES = [
  '서울',
  '경기',
  '인천',
  '부산',
  '대구',
  '대전',
  '광주',
  '울산',
  '세종',
  '강원',
  '충북',
  '충남',
  '전북',
  '전남',
  '경북',
  '경남',
  '제주',
] as const

export const EMPLOYMENT_TYPES = ['정규직', '계약직', '인턴'] as const
export type EmploymentType = (typeof EMPLOYMENT_TYPES)[number]

export const EXPERIENCE_OPTIONS = [0, 1, 2, 3, 5, 10] as const

export const PAGE_SIZE = 20
