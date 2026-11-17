import { Link, NavLink, Outlet, useLocation } from 'react-router'
import { useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { LanguageFlag, ThemeToggle } from './HeaderControls'
import Logo from './Logo'
import { focusRing, muted, primaryButton, secondaryButton } from './ui'

export const pillPrimary = `${primaryButton} min-h-12 px-6 text-base`
export const pillSecondary = `${secondaryButton} min-h-12 px-6 text-base`

const NAV: { to: string; label: MessageKey; hash?: string }[] = [
  { to: '/', label: 'nav.homeLink' },
  { to: '/search', label: 'nav.search' },
  { to: '/copilot', label: 'nav.copilot' },
  { to: '/chat', label: 'nav.chat' },
  { to: '/analytics', label: 'nav.dashboard' },
  { to: '/', label: 'nav.about', hash: 'about' },
]

const navItem = (active: boolean) =>
  `relative inline-flex min-h-11 items-center px-3 text-[17px] font-medium transition-colors ${focusRing} ${
    active
      ? 'text-brand after:absolute after:inset-x-1 after:-bottom-2 after:h-[2.5px] after:rounded-full after:bg-brand dark:text-blue-300 dark:after:bg-blue-300'
      : 'text-[#434965] hover:text-ink dark:text-slate-400 dark:hover:text-white'
  }`

export default function PublicLayout() {
  const { t } = useI18n()
  const { user, isPending } = useAuth()
  const { pathname, hash } = useLocation()

  return (
    <div className="relative flex min-h-screen flex-col overflow-x-clip bg-[#f9fafe] text-ink dark:bg-slate-950 dark:text-slate-100">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
      >
        {t('a11y.skip')}
      </a>
      <header className="absolute inset-x-0 top-0 z-30">
        <div className="mx-auto flex max-w-[1440px] items-center gap-2 px-4 py-5 sm:px-8 lg:py-6">
          <Logo responsive />
          <nav aria-label={t('nav.main')} className="mx-auto hidden xl:block">
            <ul className="flex items-center gap-4">
              {NAV.map(({ to, label, hash: target }) => {
                const active =
                  to === '/' && pathname === '/' && (hash || '') === (target ? `#${target}` : '')
                return (
                  <li key={label}>
                    {to === '/' ? (
                      <Link
                        to={{ pathname: '/', hash: target ?? '' }}
                        aria-current={active ? 'page' : undefined}
                        className={navItem(active)}
                      >
                        {t(label)}
                      </Link>
                    ) : (
                      <NavLink to={to} className={({ isActive }) => navItem(isActive)}>
                        {t(label)}
                      </NavLink>
                    )}
                  </li>
                )
              })}
            </ul>
          </nav>
          <div className="ml-auto flex items-center gap-2 sm:gap-3 xl:ml-0">
            <LanguageFlag />
            <span className="max-sm:hidden">
              <ThemeToggle />
            </span>
            {isPending ? null : user ? (
              <Link to="/dashboard" className={`${primaryButton} min-h-12 px-6 text-base`}>
                <span className="max-sm:hidden">{t('auth.portal')}</span>
                <span className="sm:hidden">{t('auth.portalShort')}</span>
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className={`${secondaryButton} min-h-12 px-6 text-base max-sm:hidden`}
                >
                  {t('auth.login')}
                </Link>
                <Link to="/signup" className={`${primaryButton} min-h-12 px-6 text-base`}>
                  {t('auth.signup')}
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main id="main" className="flex-1">
        <Outlet />
      </main>
      <footer className="mx-auto w-full max-w-[1440px] px-4 py-10 sm:px-8">
        <div
          className={`flex flex-col gap-3 text-sm sm:flex-row sm:items-center sm:justify-between ${muted}`}
        >
          <p>© 2026 JikUp · {t('footer.note')}</p>
          <ul className="flex gap-1">
            <li>
              <Link to={{ pathname: '/', hash: 'about' }} className={navItem(false)}>
                {t('nav.about')}
              </Link>
            </li>
            <li>
              <Link to={{ pathname: '/', hash: 'faq' }} className={navItem(false)}>
                {t('nav.faq')}
              </Link>
            </li>
          </ul>
        </div>
      </footer>
    </div>
  )
}
