import { describe, expect, it } from 'vitest'
import { parseAnswer, tokenizeInline } from './answerText'

describe('tokenizeInline', () => {
  it('splits bold text and job citations', () => {
    expect(tokenizeInline('Best: **Backend** role [job:12], also [job:7].')).toEqual([
      { type: 'text', value: 'Best: ' },
      { type: 'bold', children: [{ type: 'text', value: 'Backend' }] },
      { type: 'text', value: ' role ' },
      { type: 'job', id: 12 },
      { type: 'text', value: ', also ' },
      { type: 'job', id: 7 },
      { type: 'text', value: '.' },
    ])
  })

  it('finds citations inside bold text', () => {
    expect(tokenizeInline('**[job:113] 프론트엔드 개발자**')).toEqual([
      {
        type: 'bold',
        children: [
          { type: 'job', id: 113 },
          { type: 'text', value: ' 프론트엔드 개발자' },
        ],
      },
    ])
  })

  it('keeps HTML as plain text', () => {
    expect(tokenizeInline('<img src=x onerror=alert(1)>')).toEqual([
      { type: 'text', value: '<img src=x onerror=alert(1)>' },
    ])
  })

  it('ignores malformed citations and unclosed bold', () => {
    expect(tokenizeInline('[job:abc] **open')).toEqual([
      { type: 'text', value: '[job:abc] **open' },
    ])
  })
})

describe('parseAnswer', () => {
  it('detects list items and drops blank lines and heading marks', () => {
    const blocks = parseAnswer('## Top picks\n\n1. First [job:1]\n- Second\n* Third\nDone')
    expect(blocks.map((b) => b.type)).toEqual(['paragraph', 'item', 'item', 'item', 'paragraph'])
    expect(blocks[0].tokens).toEqual([{ type: 'text', value: 'Top picks' }])
    expect(blocks[1].tokens.at(-1)).toEqual({ type: 'job', id: 1 })
  })
})
