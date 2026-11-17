import { useEffect } from 'react'
import { Link, useLocation } from 'react-router'
import { pillPrimary, pillSecondary } from '../components/PublicLayout'
import { focusRing, muted } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'

const surface = 'rounded-3xl bg-white p-5 dark:bg-slate-900'
const lead = 'text-slate-500 dark:text-slate-400'
const sectionTitle =
  'max-w-3xl text-[32px] leading-[1.08] font-[650] tracking-[-0.03em] sm:text-[44px]'

const FEATURES = ['search', 'chat', 'copilot', 'dashboard'] as const
const FEATURE_TAGS: Record<(typeof FEATURES)[number], string[]> = {
  search: ['서울', 'Python', '0–2', '정규직'],
  chat: ['English', "O'zbek", '한국어'],
  copilot: ['PDF', '자기소개서', '면접'],
  dashboard: ['Skills', 'Experience', 'Cities'],
}
const FAQ_COUNT = 7

function Heading({ title, rest }: { title: string; rest: string }) {
  return (
    <h2 className={sectionTitle}>
      {title} <span className={`font-[550] ${lead}`}>{rest}</span>
    </h2>
  )
}

function Showcase() {
  const { t } = useI18n()
  return (
    <div
      aria-hidden="true"
      className="mt-16 grid gap-4 rounded-[32px] bg-fill p-4 sm:p-6 lg:grid-cols-[1.2fr_1fr]"
    >
      <div className={`${surface} space-y-4`}>
        <p className="ml-auto w-fit max-w-[85%] rounded-2xl bg-ink px-4 py-2.5 text-sm text-white dark:bg-white dark:text-ink">
          {t('landing.mockQuery')}
        </p>
        <p className="text-sm leading-relaxed">{t('landing.mockAnswer')}</p>
        <ul className="grid gap-2 sm:grid-cols-2">
          {[
            ['가', '백엔드 개발자 (Python)', '가상랩 · 서울 강남구'],
            ['나', '주니어 서버 개발자', '나래소프트 · 서울 마포구'],
          ].map(([mark, title, meta], i) => (
            <li key={title} className="flex gap-3 rounded-2xl bg-fill p-3">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-fill-strong text-sm font-semibold">
                {mark}
              </span>
              <span className="min-w-0 text-sm">
                <span className="block truncate font-medium">
                  [{i + 1}] {title}
                </span>
                <span className={`block truncate text-xs ${muted}`}>{meta}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>
      <div className="grid gap-4">
        <div className={surface}>
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-medium">{t('landing.mockMatch')}</span>
            <span className="text-[28px] leading-none font-[650] tracking-tight">72%</span>
          </div>
          <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-fill-strong">
            <div className="h-full w-[72%] rounded-full bg-brand dark:bg-blue-400" />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
            <div>
              <p className={`mb-1.5 ${muted}`}>{t('landing.mockHave')}</p>
              <p className="flex flex-wrap gap-1">
                {['Python', 'FastAPI', 'Docker'].map((s) => (
                  <span
                    key={s}
                    className="rounded-md bg-green-50 px-2 py-0.5 text-green-800 dark:bg-green-950 dark:text-green-200"
                  >
                    ✓ {s}
                  </span>
                ))}
              </p>
            </div>
            <div>
              <p className={`mb-1.5 ${muted}`}>{t('landing.mockLearn')}</p>
              <p className="flex flex-wrap gap-1">
                {['Kubernetes', 'AWS'].map((s) => (
                  <span
                    key={s}
                    className="rounded-md bg-red-50 px-2 py-0.5 text-red-800 dark:bg-red-950 dark:text-red-200"
                  >
                    ✗ {s}
                  </span>
                ))}
              </p>
            </div>
          </div>
        </div>
        <div className={surface}>
          <p className="text-sm font-medium">{t('landing.mockLetter')}</p>
          <p className={`mt-1 text-xs ${muted}`}>{t('landing.mockLetterBody')}</p>
          <div className="mt-3 space-y-1.5">
            <div className="h-2 w-full rounded-full bg-fill-strong" />
            <div className="h-2 w-11/12 rounded-full bg-fill-strong" />
            <div className="h-2 w-4/5 rounded-full bg-fill-strong" />
          </div>
        </div>
      </div>
    </div>
  )
}

export default function LandingPage() {
  const { t } = useI18n()
  const { user } = useAuth()
  const { hash } = useLocation()

  useEffect(() => {
    if (!hash) return
    document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth' })
  }, [hash])

  const stats: [string, MessageKey][] = [
    ['200', 'landing.statPostings'],
    ['3', 'landing.statLanguages'],
    ['4', 'landing.statTools'],
    ['7', 'landing.statDays'],
  ]

  return (
    <>
      <title>{`JikUp | ${t('app.tagline')}`}</title>

      <section className="mx-auto max-w-6xl px-4 pt-16 pb-8 text-center sm:pt-24">
        <p className="mx-auto w-fit rounded-full bg-fill-strong px-4 py-1.5 text-sm font-medium text-slate-700 dark:text-slate-300">
          {user ? t('landing.welcomeBack', { email: user.email }) : t('landing.eyebrow')}
        </p>
        <h1 className="mx-auto mt-6 max-w-4xl text-[44px] leading-[1.02] font-[650] tracking-[-0.035em] sm:text-[64px] lg:text-[76px]">
          {t('landing.title')}{' '}
          <span className={`font-[550] ${lead}`}>{t('landing.titleLead')}</span>
        </h1>
        <p className={`mx-auto mt-6 max-w-2xl text-lg leading-relaxed ${muted}`}>
          {t('landing.subtitle')}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {user ? (
            <Link to="/search" className={`${pillPrimary} min-h-12 px-6 text-base`}>
              {t('auth.portal')}
            </Link>
          ) : (
            <Link to="/signup" className={`${pillPrimary} min-h-12 px-6 text-base`}>
              {t('landing.ctaStart')}
            </Link>
          )}
          <Link
            to={{ pathname: '/', hash: 'how' }}
            className={`${pillSecondary} min-h-12 px-6 text-base`}
          >
            {t('landing.ctaHow')}
          </Link>
        </div>
        <p className={`mt-5 text-xs ${muted}`}>{t('landing.demoNote')}</p>
        <Showcase />
        <dl className="mt-12 grid grid-cols-2 gap-6 text-left sm:grid-cols-4">
          {stats.map(([value, label]) => (
            <div key={label} className="flex flex-col-reverse">
              <dt className={`text-sm ${muted}`}>{t(label)}</dt>
              <dd className="text-[40px] leading-tight font-[650] tracking-[-0.03em]">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section id="about" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
        <Heading title={t('about.title')} rest={t('about.lead')} />
        <p className={`mt-5 max-w-2xl text-lg leading-relaxed ${muted}`}>{t('about.body')}</p>
        <ul className="mt-10 grid gap-4 sm:grid-cols-2">
          {FEATURES.map((key) => (
            <li key={key} className="flex flex-col rounded-[28px] bg-fill p-8">
              <h3 className="text-2xl font-[650] tracking-[-0.02em]">
                {t(`feature.${key}.title`)}
              </h3>
              <p className={`mt-2 leading-relaxed ${muted}`}>{t(`feature.${key}.body`)}</p>
              <p className="mt-6 flex flex-wrap gap-1.5" aria-hidden="true">
                {FEATURE_TAGS[key].map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-white px-3 py-1 text-xs font-medium dark:bg-slate-900"
                  >
                    {tag}
                  </span>
                ))}
              </p>
            </li>
          ))}
        </ul>
      </section>

      <section id="how" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
        <Heading title={t('steps.title')} rest={t('steps.lead')} />
        <ol className="mt-10 grid gap-4 md:grid-cols-3">
          {([1, 2, 3] as const).map((n) => (
            <li key={n} className="rounded-[28px] bg-fill p-8">
              <span className="flex size-10 items-center justify-center rounded-full bg-ink text-sm font-semibold text-white dark:bg-white dark:text-ink">
                {n}
              </span>
              <h3 className="mt-6 text-xl font-[650] tracking-[-0.02em]">
                {t(`steps.${n}.title`)}
              </h3>
              <p className={`mt-2 leading-relaxed ${muted}`}>{t(`steps.${n}.body`)}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="faq" className="mx-auto max-w-6xl scroll-mt-20 px-4 py-20">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.4fr]">
          <Heading title={t('faq.title')} rest={t('faq.lead')} />
          <ul>
            {Array.from({ length: FAQ_COUNT }, (_, i) => i + 1).map((n) => (
              <li key={n} className="border-b border-ink/10 dark:border-white/10">
                <details className="group">
                  <summary
                    className={`flex min-h-11 cursor-pointer list-none items-center justify-between gap-4 py-5 text-lg font-semibold ${focusRing}`}
                  >
                    {t(`faq.q${n}` as MessageKey)}
                    <span
                      aria-hidden="true"
                      className="flex size-8 shrink-0 items-center justify-center rounded-full bg-fill-strong text-lg transition-transform group-open:rotate-45"
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

      <section className="mx-auto max-w-6xl px-4 pt-8 pb-12">
        <div className="rounded-[32px] bg-ink px-6 py-16 text-center text-white dark:bg-white dark:text-ink">
          <h2 className="text-[32px] leading-tight font-[650] tracking-[-0.03em] sm:text-[44px]">
            {t('cta.title')}
          </h2>
          <p className="mx-auto mt-3 max-w-xl text-lg text-white/75 dark:text-ink/70">
            {t('cta.body')}
          </p>
          <Link
            to={user ? '/search' : '/signup'}
            className={`mt-8 inline-flex min-h-12 items-center rounded-full bg-white px-6 text-base font-semibold text-ink transition-colors hover:bg-white/85 dark:bg-ink dark:text-white dark:hover:bg-ink/85 ${focusRing}`}
          >
            {user ? t('auth.portal') : t('landing.ctaStart')}
          </Link>
        </div>
      </section>
    </>
  )
}
