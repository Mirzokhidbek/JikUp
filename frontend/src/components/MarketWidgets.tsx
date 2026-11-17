import type { ReactNode } from 'react'
import type { PublicStats } from '../api/types'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { BriefcaseBadge, ChipBadge, RocketBadge, TrendBadge } from './icons'
import { muted } from './ui'

export function StatTiles({ stats }: { stats: PublicStats | undefined }) {
  const { t, lang } = useI18n()
  const n = (v: number | undefined) => (v === undefined ? '—' : v.toLocaleString(lang))
  const tiles: { icon: ReactNode; value: string; label: MessageKey }[] = [
    { icon: <BriefcaseBadge size={40} />, value: n(stats?.active_jobs), label: 'home.total' },
    { icon: <ChipBadge size={38} />, value: n(stats?.ai_ml_jobs), label: 'home.aiml' },
    { icon: <RocketBadge size={38} />, value: n(stats?.junior_jobs), label: 'home.junior' },
    {
      icon: <TrendBadge size={38} />,
      value: stats ? `+${stats.new_this_week.toLocaleString(lang)}` : '—',
      label: 'home.week',
    },
  ]
  return (
    <ul className="grid grid-cols-2 gap-3.5 xl:grid-cols-4">
      {tiles.map(({ icon, value, label }) => (
        <li
          key={label}
          className="flex items-center gap-3.5 rounded-2xl bg-white px-4 py-5 shadow-[0_10px_30px_-16px_rgb(20_40_120/0.25)] ring-1 ring-[#eef1f8] dark:bg-slate-900 dark:ring-white/10"
        >
          <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-[#f3f6ff] dark:bg-white/5">
            {icon}
          </span>
          <span>
            <span className="block text-[22px] leading-tight font-bold text-ink dark:text-white">
              {value}
            </span>
            <span className={`block text-[14px] ${muted}`}>{t(label)}</span>
          </span>
        </li>
      ))}
    </ul>
  )
}

export function SkillBars({
  skills,
  height = 180,
}: {
  skills: PublicStats['top_skills']
  height?: number
}) {
  const { t } = useI18n()
  const sorted = [...skills].sort((a, b) => a.jobs - b.jobs)
  const max = Math.max(1, ...sorted.map((s) => s.jobs))
  return (
    <>
      <ol className="flex items-end gap-2.5 sm:gap-4" style={{ height }} aria-hidden="true">
        {sorted.map((s, i) => (
          <li key={s.name} className="group flex h-full flex-1 flex-col items-center justify-end">
            <span className="mb-1 text-[11px] font-semibold text-[#595a6e] opacity-0 transition-opacity group-hover:opacity-100 dark:text-slate-300">
              {s.share}%
            </span>
            <span
              title={`${s.name}: ${t('home.postings', { n: s.jobs })} (${s.share}%)`}
              className="w-full max-w-11 rounded-t-[10px] bg-gradient-to-b from-[#3f7bff] to-[#9cbcff] transition-[filter] group-hover:brightness-110"
              style={{
                height: `${Math.max(6, (s.jobs / max) * 100)}%`,
                opacity: 0.55 + (0.45 * (i + 1)) / sorted.length,
              }}
            />
          </li>
        ))}
      </ol>
      <ol className="mt-2 flex gap-2.5 sm:gap-4" aria-hidden="true">
        {sorted.map((s) => (
          <li
            key={s.name}
            className={`flex-1 overflow-hidden text-center text-[11px] text-ellipsis whitespace-nowrap ${muted}`}
          >
            {s.name}
          </li>
        ))}
      </ol>
      <table className="sr-only">
        <caption>{t('home.skillsHint')}</caption>
        <tbody>
          {[...skills].map((s) => (
            <tr key={s.name}>
              <th scope="row">{s.name}</th>
              <td>{t('home.postings', { n: s.jobs })}</td>
              <td>{s.share}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  )
}
