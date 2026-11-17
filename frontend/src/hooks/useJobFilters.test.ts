import { describe, expect, it } from 'vitest'
import { readFilters, toQuery, writeFilters } from './useJobFilters'

describe('job filters in the URL', () => {
  it('round-trips through URL params', () => {
    const params = new URLSearchParams('city=서울&exp_max=2&skill=Python&skill=Go&page=3')
    const filters = readFilters(params)
    expect(filters).toEqual({
      q: '',
      city: '서울',
      exp_max: '2',
      employment_type: '',
      skill: ['Python', 'Go'],
      page: 3,
    })
    expect(writeFilters(filters).toString()).toBe(params.toString())
  })

  it('applies sequential patches without losing earlier ones', () => {
    let params = new URLSearchParams()
    for (const patch of [{ city: '서울' }, { exp_max: '2' }, { skill: ['Python'] }]) {
      params = writeFilters({ ...readFilters(params), page: 1, ...patch })
    }
    expect(readFilters(params)).toMatchObject({ city: '서울', exp_max: '2', skill: ['Python'] })
  })

  it('ignores invalid page and experience values', () => {
    const filters = readFilters(new URLSearchParams('page=-4&exp_max=abc'))
    expect(filters.page).toBe(1)
    expect(toQuery(filters).exp_max).toBeUndefined()
    expect(toQuery({ ...filters, exp_max: '0' }).exp_max).toBe(0)
  })
})
