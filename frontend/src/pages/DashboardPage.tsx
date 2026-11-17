import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useId, useMemo, useState } from 'react'
import { api } from '../api/client'
import type { Bucket } from '../api/types'
import BarList, { type BarDatum } from '../components/charts/BarList'
import ChartCard from '../components/charts/ChartCard'
import MarketGap from '../components/charts/MarketGap'
import StatTile from '../components/charts/StatTile'
import TrendChart from '../components/charts/TrendChart'
import Page from '../components/Page.tsx'
import SkillInput, { inputClass } from '../components/SkillInput'
import { ErrorState } from '../components/States'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { assignSlots, colorFor, type Slots } from '../lib/seriesSlots'

const PERIODS = [undefined, 30, 90] as const
const MAX_TREND_SKILLS = 5

export default function DashboardPage() {
  const { t, lang } = useI18n()
  const periodId = useId()
  const categoryId = useId()
  const coId = useId()
  const [days, setDays] = useState<number | undefined>(undefined)
  const [category, setCategory] = useState('')
  const [trendSkills, setTrendSkills] = useState<string[] | null>(null)
  const [slots, setSlots] = useState<Slots>({})
  const [coSkill, setCoSkill] = useState('Python')

  const keep = { placeholderData: keepPreviousData }
  const overview = useQuery({ queryKey: ['an', 'overview'], queryFn: api.analytics.overview })
  const skills = useQuery({
    queryKey: ['an', 'skills', days, category],
    queryFn: () => api.analytics.skills(days, category || undefined),
    ...keep,
  })
  const trends = useQuery({
    queryKey: ['an', 'trends', trendSkills],
    queryFn: () => api.analytics.trends(trendSkills ?? []),
    ...keep,
  })
  const experience = useQuery({
    queryKey: ['an', 'exp', days],
    queryFn: () => api.analytics.experience(days),
    ...keep,
  })
  const cities = useQuery({
    queryKey: ['an', 'cities', days],
    queryFn: () => api.analytics.cities(days),
    ...keep,
  })
  const co = useQuery({
    queryKey: ['an', 'co', coSkill],
    queryFn: () => api.analytics.cooccurrence(coSkill),
    ...keep,
  })
  const market = useQuery({
    queryKey: ['an', 'skills', undefined, ''],
    queryFn: () => api.analytics.skills(),
  })
  const allSkills = useQuery({ queryKey: ['skills'], queryFn: api.getSkills, staleTime: 3_600_000 })
  const known = useMemo(
    () => new Map((allSkills.data ?? []).map((s) => [s.name.toLowerCase(), s.name])),
    [allSkills.data],
  )

  const series = useMemo(() => trends.data?.series.map((s) => s.skill) ?? [], [trends.data])
  const currentSlots = useMemo(() => assignSlots(slots, series), [slots, series])
  const pct = (n: number) => `${n}%`
  const postings = t('dash.postings').toLowerCase()
  const formatWeek = (week: string) =>
    new Intl.DateTimeFormat(lang, { month: 'short', day: 'numeric' }).format(new Date(week))

  const changeTrendSkills = (next: string[]) => {
    const canonical = next.flatMap((s) => known.get(s.toLowerCase()) ?? [])
    const list = [...new Set(canonical)].slice(0, MAX_TREND_SKILLS)
    setSlots(assignSlots(currentSlots, list))
    setTrendSkills(list)
  }

  const bucketBars = (items: Bucket[] | undefined, label: (b: string) => string) =>
    (items ?? []).map((b) => ({
      bar: { label: label(b.label), value: b.share, detail: `${b.jobs} ${postings}` },
      row: [label(b.label), b.jobs, pct(b.share)] as (string | number)[],
    }))
  const exp = bucketBars(experience.data, (b) => t(`dash.exp.${b}` as MessageKey))
  const city = bucketBars(cities.data, (b) => (b === 'other' ? t('dash.other') : b))
  const shareBars = (items: { name: string; jobs: number; share: number }[] | undefined) =>
    (items ?? []).map((s) => ({
      bar: { label: s.name, value: s.share, detail: `${s.jobs} ${postings}` } as BarDatum,
      row: [s.name, s.jobs, pct(s.share)] as (string | number)[],
    }))
  const top = shareBars(skills.data?.skills)
  const related = shareBars(co.data?.related)
  const shareCols = [
    { header: t('dash.skill') },
    { header: t('dash.postings'), numeric: true },
    { header: t('dash.share'), numeric: true },
  ]
  const o = overview.data

  if (overview.isError) {
    return <ErrorState error={overview.error} onRetry={() => void overview.refetch()} />
  }

  return (
    <Page title={t('nav.dashboard')} lead={t('dash.subtitle')}>
      {o && o.demo_share > 0 && (
        <p className="mt-6 rounded-xl bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:bg-amber-400/10 dark:text-amber-100">
          {t('dash.demoNote', { share: o.demo_share })}
        </p>
      )}

      <div className="mt-8 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          label={t('dash.kpiActive')}
          value={o ? o.active_jobs.toLocaleString(lang) : '-'}
        />
        <StatTile label={t('dash.kpiNew')} value={o ? o.new_this_week.toLocaleString(lang) : '-'} />
        <StatTile
          label={t('dash.kpiTop')}
          value={
            o?.top_skill
              ? t('dash.kpiTopValue', { skill: o.top_skill.name, share: o.top_skill.share })
              : '-'
          }
        />
        <StatTile label={t('dash.kpiEntry')} value={o ? pct(o.entry_level_share) : '-'} />
      </div>

      {market.data && (
        <div className="mt-6">
          <MarketGap market={market.data.skills} />
        </div>
      )}

      <form
        aria-label={t('dash.filters')}
        onSubmit={(e) => e.preventDefault()}
        className="mt-8 flex flex-wrap gap-4"
      >
        <div className="w-full sm:w-56">
          <label
            htmlFor={periodId}
            className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            {t('dash.period')}
          </label>
          <select
            id={periodId}
            value={days ?? ''}
            onChange={(e) => setDays(e.target.value ? Number(e.target.value) : undefined)}
            className={inputClass}
          >
            {PERIODS.map((p) => (
              <option key={p ?? 'all'} value={p ?? ''}>
                {p ? t('dash.period.n', { n: p }) : t('dash.period.all')}
              </option>
            ))}
          </select>
        </div>
        <div className="w-full sm:w-56">
          <label
            htmlFor={categoryId}
            className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            {t('dash.category')}
          </label>
          <select
            id={categoryId}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className={inputClass}
          >
            <option value="">{t('common.any')}</option>
            {skills.data?.categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </form>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard
          title={t('dash.topSkills')}
          hint={t('dash.topSkillsHint')}
          busy={skills.isFetching}
          columns={shareCols}
          rows={top.map((x) => x.row)}
          className="lg:row-span-2"
        >
          <BarList data={top.map((x) => x.bar)} />
        </ChartCard>
        <ChartCard
          title={t('dash.experience')}
          busy={experience.isFetching}
          columns={shareCols}
          rows={exp.map((x) => x.row)}
        >
          <BarList data={exp.map((x) => x.bar)} />
        </ChartCard>
        <ChartCard
          title={t('dash.cities')}
          busy={cities.isFetching}
          columns={shareCols}
          rows={city.map((x) => x.row)}
        >
          <BarList data={city.map((x) => x.bar)} />
        </ChartCard>
      </div>

      <ChartCard
        title={t('dash.trend')}
        hint={t('dash.trendNote')}
        busy={trends.isFetching}
        columns={[{ header: t('dash.week') }, ...series.map((s) => ({ header: s, numeric: true }))]}
        rows={(trends.data?.weeks ?? []).map((w, i) => [
          formatWeek(w),
          ...(trends.data?.series ?? []).map((s) => s.counts[i]),
        ])}
        className="mt-6"
      >
        <div className="mb-4 max-w-md">
          <SkillInput
            label={t('dash.trendHint')}
            value={series}
            suggestions={(allSkills.data ?? []).map((s) => s.name)}
            onChange={changeTrendSkills}
          />
        </div>
        {trends.data && (
          <TrendChart
            report={trends.data}
            colorOf={(skill) => colorFor(currentSlots, skill)}
            formatWeek={formatWeek}
          />
        )}
      </ChartCard>

      <ChartCard
        title={t('dash.cooccurrence')}
        hint={
          co.data
            ? t('dash.cooccurrenceHint', { skill: co.data.skill, jobs: co.data.jobs })
            : undefined
        }
        busy={co.isFetching}
        columns={shareCols}
        rows={related.map((x) => x.row)}
        className="mt-6"
      >
        <div className="mb-4 w-full sm:w-56">
          <label
            htmlFor={coId}
            className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            {t('dash.skill')}
          </label>
          <select
            id={coId}
            value={coSkill}
            onChange={(e) => setCoSkill(e.target.value)}
            className={inputClass}
          >
            {(allSkills.data ?? []).slice(0, 30).map((s) => (
              <option key={s.name} value={s.name}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
        <BarList data={related.map((x) => x.bar)} />
      </ChartCard>
    </Page>
  )
}
