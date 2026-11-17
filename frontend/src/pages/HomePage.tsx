import { useQuery } from '@tanstack/react-query'
import { useId } from 'react'
import { Link, useNavigate } from 'react-router'
import { api } from '../api/client'
import { ArrowRightIcon, ChevronDownIcon } from '../components/icons'
import Avatar from '../components/Avatar'
import { ErrorState } from '../components/States'
import { card, focusRing, link, muted } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { useI18n } from '../i18n/useI18n'
import { CITIES } from '../lib/constants'
import { displayName } from '../lib/user'
import { SkillBars, StatTiles } from '../components/MarketWidgets'

export default function HomePage() {
  const { t } = useI18n()
  const { user } = useAuth()
  const navigate = useNavigate()
  const cityId = useId()
  const stats = useQuery({
    queryKey: ['public-stats'],
    queryFn: api.publicStats,
    staleTime: 300_000,
  })
  const name = user ? displayName(user.email) : ''

  return (
    <>
      <title>{`${t('nav.overview')} | JikUp`}</title>
      <div className="flex flex-wrap items-center gap-4">
        {user && <Avatar email={user.email} size={60} />}
        <div className="min-w-0 flex-1">
          <h1 className="text-[26px] leading-tight font-bold tracking-[-0.02em] text-ink sm:text-[30px] dark:text-white">
            {t('home.hello', { name })}
          </h1>
          <p className="mt-1 text-[16px] text-[#33343a] dark:text-slate-300">
            {t('home.sub')} <span aria-hidden="true">✨</span>
          </p>
        </div>
        <label
          htmlFor={cityId}
          className="relative flex h-12 items-center gap-2 rounded-full bg-white pr-10 pl-4 text-[15px] font-medium shadow-[0_6px_18px_-10px_rgb(20_40_120/0.35)] ring-1 ring-line has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-brand dark:bg-slate-900 dark:ring-white/10"
        >
          <span aria-hidden="true">🇰🇷</span>
          <span className="sr-only">{t('home.city')}</span>
          <select
            id={cityId}
            defaultValue=""
            onChange={(e) =>
              e.target.value && navigate(`/search?city=${encodeURIComponent(e.target.value)}`)
            }
            className="h-11 cursor-pointer appearance-none bg-transparent pr-1 outline-none"
          >
            <option value="" disabled>
              {CITIES[0]}
            </option>
            {CITIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <ChevronDownIcon size={16} className="pointer-events-none absolute right-4" />
        </label>
      </div>

      {stats.isError ? (
        <div className="mt-6">
          <ErrorState error={stats.error} onRetry={() => void stats.refetch()} />
        </div>
      ) : (
        <>
          <div className="mt-7">
            <StatTiles stats={stats.data} />
          </div>
          <section aria-labelledby="skills-heading" className={`${card} mt-5 p-6`}>
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#eef1f8] pb-4 dark:border-white/10">
              <div>
                <h2 id="skills-heading" className="text-[18px] font-bold text-ink dark:text-white">
                  {t('home.skills')}
                </h2>
                <p className={`text-sm ${muted}`}>{t('home.skillsHint')}</p>
              </div>
              <Link
                to="/analytics"
                className={`inline-flex min-h-11 items-center gap-1 text-[15px] ${link} ${focusRing}`}
              >
                {t('home.details')} <ArrowRightIcon size={16} />
              </Link>
            </div>
            <div className="mt-6">
              {stats.data ? (
                <SkillBars skills={stats.data.top_skills} height={240} />
              ) : (
                <div className="h-[240px] motion-safe:animate-pulse rounded-xl bg-fill" />
              )}
            </div>
          </section>
        </>
      )}
    </>
  )
}
