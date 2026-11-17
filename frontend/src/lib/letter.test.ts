import { describe, expect, it } from 'vitest'
import { letterFilename, letterText } from './letter'

describe('cover letter export', () => {
  it('joins sections with Korean headings in order', () => {
    const text = letterText({
      motivation: ' 동기 ',
      competency: '역량',
      projects: '경험',
      aspiration: '포부',
    })
    expect(text).toBe(
      '[지원동기]\n동기\n\n[직무 역량]\n역량\n\n[프로젝트 경험]\n경험\n\n[입사 후 포부]\n포부',
    )
  })

  it('makes a safe file name', () => {
    expect(letterFilename('백엔드/서버 개발자 <Python>')).toBe(
      '자기소개서 - 백엔드 서버 개발자  Python.txt',
    )
    expect(letterFilename('   ')).toBe('자기소개서 - JikUp.txt')
  })
})
