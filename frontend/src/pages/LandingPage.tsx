import { useQuery } from '@tanstack/react-query'
import { useEffect, type CSSProperties } from 'react'
import { Link, useLocation } from 'react-router'
import { api } from '../api/client'
import type { PublicStats } from '../api/types'
import avatarUrl from '../assets/landing/avatar.webp'
import palaceUrl from '../assets/landing/palace.webp'
import skylineUrl from '../assets/landing/skyline.webp'
import {
  AnalyticsIcon,
  ArrowRightIcon,
  BarsBadge,
  BriefcaseBadge,
  CheckBadge,
  ChevronDownIcon,
  CopilotIcon,
  HomeIcon,
  JobsIcon,
  PlayBadge,
  ResumeIcon,
  Sparkle,
} from '../components/icons'
import { LogoMark, Wordmark } from '../components/Logo'
import { pillPrimary, pillSecondary } from '../components/PublicLayout'
import { focusRing, muted } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { SkillBars, StatTiles } from '../components/MarketWidgets'
import { useI18n } from '../i18n/useI18n'

/** Search recall@10 from backend/eval/results (day 6 run on the original rules). */
const SEARCH_RECALL = '96.7%'

/** The design is 1672 x 941; decorations are placed in percent of that frame. */
const at = (x: number, y: number, w?: number): CSSProperties => ({
  left: `${(x / 1672) * 100}%`,
  top: `${(y / 941) * 100}%`,
  ...(w ? { width: `${(w / 1672) * 100}%` } : {}),
})

const floatCard =
  'absolute rounded-[22px] bg-white/95 shadow-[0_18px_40px_-18px_rgb(20_40_120/0.35)] ring-1 ring-white backdrop-blur dark:bg-slate-900/90 dark:ring-white/10'

const sectionTitle =
  'max-w-3xl text-[32px] leading-[1.1] font-bold tracking-[-0.03em] text-ink sm:text-[44px] dark:text-white'

function HeroArt({ stats }: { stats: PublicStats | undefined }) {
  const { t } = useI18n()
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none absolute inset-x-0 top-0 hidden aspect-[1672/941] lg:block"
    >
      <svg className="absolute inset-0 h-full w-full" viewBox="0 0 1672 941" fill="none">
        <circle cx="430" cy="560" r="420" stroke="#e3eaff" strokeWidth="1.5" />
        <circle cx="1330" cy="520" r="470" stroke="#e3eaff" strokeWidth="1.5" />
        <circle cx="836" cy="1350" r="760" fill="#eef3ff" fillOpacity=".55" />
      </svg>
      <img
        src={palaceUrl}
        alt=""
        className="absolute select-none dark:hidden"
        style={at(0, 440, 470)}
      />
      <img
        src={skylineUrl}
        alt=""
        className="absolute select-none dark:hidden"
        style={at(1090, 230, 582)}
      />
      <span className="absolute text-[#2f7bff]" style={at(1513, 186)}>
        <Sparkle size={30} />
      </span>
      <span className="absolute text-[#2f7bff]" style={at(147, 297)}>
        <Sparkle size={26} />
      </span>
      <span className="absolute size-2 rounded-full bg-[#9ec1ff]" style={at(160, 135)} />

      <div
        className={`${floatCard} flex -rotate-[7deg] items-center gap-4 px-6 py-5`}
        style={at(190, 180)}
      >
        <BriefcaseBadge size={54} />
        <div>
          <p className="text-[26px] leading-none font-bold text-ink dark:text-white">
            {stats ? stats.active_jobs.toLocaleString() : '—'}
          </p>
          <p className={`mt-1 text-[15px] ${muted}`}>{t('hero.activeJobs')}</p>
        </div>
      </div>
      <div
        className={`${floatCard} flex -rotate-[9deg] items-center gap-4 px-6 py-5`}
        style={at(70, 352)}
      >
        <BarsBadge size={44} />
        <div>
          <p className="text-[26px] leading-none font-bold text-ink dark:text-white">
            {SEARCH_RECALL}
          </p>
          <p className={`mt-1 text-[14px] ${muted}`}>{t('hero.recall')}</p>
        </div>
      </div>
      <ul className={`${floatCard} rotate-[8deg] space-y-3 px-6 py-5`} style={at(1405, 252)}>
        {(['hero.check1', 'hero.check2', 'hero.check3', 'hero.check4'] as const).map((key) => (
          <li
            key={key}
            className="flex items-center gap-3 text-[16px] font-medium text-[#2c2b3e] dark:text-slate-200"
          >
            <CheckBadge />
            {t(key)}
          </li>
        ))}
      </ul>
    </div>
  )
}

const PREVIEW_NAV = [
  { icon: HomeIcon, label: 'nav.overview', active: true },
  { icon: JobsIcon, label: 'nav.search' },
  { icon: ResumeIcon, label: 'nav.resume' },
  { icon: CopilotIcon, label: 'nav.chat' },
  { icon: AnalyticsIcon, label: 'nav.dashboard' },
] as const

function DashboardPreview({ stats }: { stats: PublicStats | undefined }) {
  const { t } = useI18n()
  return (
    <figure className="relative mx-auto mt-14 w-full max-w-[1137px] rounded-[30px] bg-white/95 p-3 shadow-[0_30px_80px_-30px_rgb(20_40_120/0.35)] ring-1 ring-white backdrop-blur dark:bg-slate-900/95 dark:ring-white/10">
      <figcaption className="sr-only">
        {t('hero.preview', {
          jobs: stats?.active_jobs ?? '—',
          ai: stats?.ai_ml_jobs ?? '—',
          junior: stats?.junior_jobs ?? '—',
        })}
      </figcaption>
      <div aria-hidden="true" className="grid gap-3 text-left md:grid-cols-[200px_1fr]">
        <div className="hidden rounded-[22px] bg-white p-4 md:block dark:bg-slate-900">
          <div className="flex items-center gap-2 px-1 pt-2 pb-6">
            <LogoMark size={30} />
            <Wordmark size="text-[20px]" />
          </div>
          <ul className="space-y-1">
            {PREVIEW_NAV.map(({ icon: Icon, label, ...rest }) => (
              <li
                key={label}
                className={`flex h-10 items-center gap-3 rounded-xl px-3 text-[15px] ${
                  'active' in rest
                    ? 'bg-brand-soft font-semibold text-brand dark:bg-blue-500/15 dark:text-blue-300'
                    : 'text-[#4e5169] dark:text-slate-400'
                }`}
              >
                <Icon size={19} />
                {t(label)}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-[22px] p-3 sm:p-4">
          <div className="flex items-center gap-4">
            <img src={avatarUrl} alt="" width={56} height={56} className="size-14 rounded-full" />
            <div className="min-w-0 flex-1">
              <p className="text-[19px] font-bold text-ink dark:text-white">
                {t('home.hello', { name: t('hero.persona') })}
              </p>
              <p className="text-[15px] text-[#33343a] dark:text-slate-300">
                {t('home.sub')} <span className="text-amber-400">✨</span>
              </p>
            </div>
            <span className="hidden h-10 items-center gap-2 rounded-full bg-white px-4 text-[15px] font-medium shadow-[0_4px_14px_-6px_rgb(20_40_120/0.3)] ring-1 ring-line sm:flex dark:bg-slate-800 dark:ring-white/10">
              🇰🇷 서울 <ChevronDownIcon size={16} />
            </span>
          </div>
          <div className="mt-5">
            <StatTiles stats={stats} />
          </div>
          <div className="mt-4 rounded-2xl bg-white p-5 shadow-[0_10px_30px_-16px_rgb(20_40_120/0.25)] ring-1 ring-[#eef1f8] dark:bg-slate-900 dark:ring-white/10">
            <div className="flex items-center justify-between border-b border-[#eef1f8] pb-3 dark:border-white/10">
              <p className="text-[17px] font-bold text-ink dark:text-white">{t('home.skills')}</p>
              <span className="inline-flex items-center gap-1 text-[14px] font-medium text-[#2a65d8] dark:text-blue-300">
                {t('home.details')} <ArrowRightIcon size={15} />
              </span>
            </div>
            <div className="mt-4">
              {stats && <SkillBars skills={stats.top_skills} height={150} />}
            </div>
          </div>
        </div>
      </div>
    </figure>
  )
}

const FEATURES = ['search', 'chat', 'copilot', 'dashboard'] as const
const FEATURE_ICONS = {
  search: JobsIcon,
  chat: CopilotIcon,
  copilot: ResumeIcon,
  dashboard: AnalyticsIcon,
}
const FAQ_COUNT = 7

export default function LandingPage() {
  const { t } = useI18n()
  const { user } = useAuth()
  const { hash } = useLocation()
  const stats = useQuery({
    queryKey: ['public-stats'],
    queryFn: api.publicStats,
    staleTime: 300_000,
  })

  useEffect(() => {
    if (!hash) return
    document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' })
  }, [hash])

  const startTo = user ? '/dashboard' : '/signup'

  return (
    <>
      <title>{`JikUp | ${t('app.tagline')}`}</title>

      <section className="relative">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1100px] bg-[radial-gradient(120%_70%_at_50%_0%,#fdfdff_0%,#f6f8ff_45%,#eaf0ff_100%)] dark:bg-[radial-gradient(120%_70%_at_50%_0%,#0b1226_0%,#020617_70%)]" />
        <HeroArt stats={stats.data} />
        <div className="relative z-10 mx-auto max-w-[1440px] px-4 pt-32 text-center sm:px-8 lg:pt-[9.2vw] 2xl:pt-[150px]">
          <p className="mx-auto inline-flex max-w-full items-center gap-3 rounded-full bg-white/90 py-2 pr-2 pl-4 text-[15px] font-semibold text-ink shadow-[0_10px_30px_-14px_rgb(20_40_120/0.35)] ring-1 ring-white dark:bg-slate-900 dark:text-white dark:ring-white/10">
            <span aria-hidden="true" className="text-[20px]">
              🇰🇷
            </span>
            <span className="min-w-0 [overflow-wrap:anywhere]">
              {user ? t('landing.welcomeBack', { email: user.email }) : t('hero.badge')}
            </span>
            <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-[#e9f8ee] whitespace-nowrap px-2.5 py-1 text-[13px] font-semibold text-[#146c3a] dark:bg-green-500/15 dark:text-green-300">
              <span aria-hidden="true" className="size-2 rounded-full bg-[#3fb46a]" />
              {t('hero.beta')}
            </span>
          </p>
          <h1 className="mx-auto mt-5 max-w-[900px] text-[44px] leading-[1.04] font-bold tracking-[-0.035em] text-ink sm:text-[64px] xl:text-[80px] dark:text-white">
            {t('hero.title1')}
            <br />
            {t('hero.title2')}{' '}
            <span className="relative inline-block pr-3 italic">
              <span className="bg-gradient-to-r from-[#0f64fd] via-[#1d4cf2] to-[#1a2cf5] bg-clip-text text-transparent">
                JikUp
              </span>
              <svg
                aria-hidden="true"
                viewBox="0 0 240 24"
                className="absolute -bottom-2 left-[6%] w-[96%]"
                preserveAspectRatio="none"
              >
                <path
                  d="M4 18C70 8 150 5 222 10"
                  stroke="#3f7bff"
                  strokeOpacity=".55"
                  strokeWidth="5"
                  fill="none"
                  strokeLinecap="round"
                />
                <path d="m222 4 14 7-15 5z" fill="#1a2cf5" />
              </svg>
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-[20px] font-medium text-[#2d3751] sm:text-[24px] dark:text-slate-300">
            {t('hero.sub')}
          </p>
          <div className="mt-9 flex flex-wrap justify-center gap-5">
            <Link to={startTo} className={`${pillPrimary} min-h-[58px] px-8 text-[17px]`}>
              {t('hero.start')} <ArrowRightIcon size={18} />
            </Link>
            <Link
              to={{ pathname: '/', hash: 'how' }}
              className={`${pillSecondary} min-h-[58px] gap-3 px-8 text-[17px] ring-[1.5px] ring-brand/70 dark:ring-blue-400/60`}
            >
              <PlayBadge /> {t('hero.demo')}
            </Link>
          </div>
          <DashboardPreview stats={stats.data} />
          <p className={`mt-6 text-xs ${muted}`}>{t('landing.demoNote')}</p>
        </div>
      </section>

      <section id="about" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-24 sm:px-8">
        <h2 className={sectionTitle}>
          {t('about.title')}{' '}
          <span className="text-brand dark:text-blue-300">{t('about.lead')}</span>
        </h2>
        <p className={`mt-5 max-w-2xl text-lg leading-relaxed ${muted}`}>{t('about.body')}</p>
        <ul className="mt-10 grid gap-5 sm:grid-cols-2">
          {FEATURES.map((key) => {
            const Icon = FEATURE_ICONS[key]
            return (
              <li
                key={key}
                className="rounded-[26px] bg-white p-8 shadow-[0_18px_40px_-24px_rgb(20_40_120/0.3)] ring-1 ring-line dark:bg-slate-900 dark:ring-white/10"
              >
                <span className="flex size-12 items-center justify-center rounded-2xl bg-brand-soft text-brand dark:bg-blue-500/15 dark:text-blue-300">
                  <Icon size={24} />
                </span>
                <h3 className="mt-5 text-2xl font-bold tracking-[-0.02em]">
                  {t(`feature.${key}.title`)}
                </h3>
                <p className={`mt-2 leading-relaxed ${muted}`}>{t(`feature.${key}.body`)}</p>
              </li>
            )
          })}
        </ul>
      </section>

      <section id="how" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-20 sm:px-8">
        <h2 className={sectionTitle}>
          {t('steps.title')}{' '}
          <span className="text-brand dark:text-blue-300">{t('steps.lead')}</span>
        </h2>
        <ol className="mt-10 grid gap-5 md:grid-cols-3">
          {([1, 2, 3] as const).map((n) => (
            <li
              key={n}
              className="rounded-[26px] bg-white p-8 shadow-[0_18px_40px_-24px_rgb(20_40_120/0.3)] ring-1 ring-line dark:bg-slate-900 dark:ring-white/10"
            >
              <span className="flex size-11 items-center justify-center rounded-full bg-brand text-base font-bold text-white">
                {n}
              </span>
              <h3 className="mt-6 text-xl font-bold tracking-[-0.02em]">{t(`steps.${n}.title`)}</h3>
              <p className={`mt-2 leading-relaxed ${muted}`}>{t(`steps.${n}.body`)}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="faq" className="mx-auto max-w-6xl scroll-mt-24 px-4 py-20 sm:px-8">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.4fr]">
          <h2 className={sectionTitle}>
            {t('faq.title')} <span className="text-brand dark:text-blue-300">{t('faq.lead')}</span>
          </h2>
          <ul className="space-y-3">
            {Array.from({ length: FAQ_COUNT }, (_, i) => i + 1).map((n) => (
              <li
                key={n}
                className="rounded-2xl bg-white px-6 ring-1 ring-line dark:bg-slate-900 dark:ring-white/10"
              >
                <details className="group">
                  <summary
                    className={`flex min-h-11 cursor-pointer list-none items-center justify-between gap-4 py-5 text-lg font-semibold ${focusRing}`}
                  >
                    {t(`faq.q${n}` as MessageKey)}
                    <span
                      aria-hidden="true"
                      className="flex size-8 shrink-0 items-center justify-center rounded-full bg-brand-soft text-lg text-brand transition-transform group-open:rotate-45 dark:bg-blue-500/15 dark:text-blue-300"
                    >
                      +
                    </span>
                  </summary>
                  <p className={`pb-6 leading-relaxed ${muted}`}>{t(`faq.a${n}` as MessageKey)}</p>
                </details>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pt-8 pb-12 sm:px-8">
        <div className="relative overflow-hidden rounded-[32px] bg-gradient-to-br from-[#1443e2] to-[#2f6bff] px-6 py-16 text-center text-white">
          <span aria-hidden="true" className="absolute top-8 right-10 text-white/70">
            <Sparkle size={30} />
          </span>
          <h2 className="text-[32px] leading-tight font-bold tracking-[-0.03em] sm:text-[44px]">
            {t('cta.title')}
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-lg text-white/85">{t('cta.body')}</p>
          <Link
            to={startTo}
            className={`mt-8 inline-flex min-h-[58px] items-center gap-2 rounded-full bg-white px-8 text-[17px] font-semibold text-brand transition-colors hover:bg-white/90 ${focusRing}`}
          >
            {user ? t('auth.portal') : t('hero.start')} <ArrowRightIcon size={18} />
          </Link>
        </div>
      </section>
    </>
  )
}
