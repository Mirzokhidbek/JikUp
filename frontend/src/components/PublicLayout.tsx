import { Link, Outlet } from 'react-router'
import { useAuth } from '../hooks/useAuth'
import { useI18n } from '../i18n/useI18n'
import { LanguageSelect, ThemeToggle } from './HeaderControls'
import Logo from './Logo'
import { focusRing, muted } from './ui'

const pill = `inline-flex min-h-11 items-center justify-center rounded-full px-5 text-sm font-semibold whitespace-nowrap transition-colors ${focusRing}`
export const pillPrimary = `${pill} bg-ink text-white hover:bg-ink/85 dark:bg-white dark:text-ink dark:hover:bg-white/85`
export const pillSecondary = `${pill} bg-fill-strong text-ink hover:bg-ink/12 dark:text-white dark:hover:bg-white/15`
const textLink = `inline-flex min-h-11 items-center rounded-full px-3 text-sm font-medium text-slate-600 transition-colors hover:text-ink dark:text-slate-400 dark:hover:text-white ${focusRing}`

export default function PublicLayout() {
  const { t } = useI18n()
  const { user, isPending } = useAuth()

  return (
    <div className="flex min-h-screen flex-col bg-white text-ink dark:bg-slate-950 dark:text-slate-100">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
      >
        {t('a11y.skip')}
      </a>
      <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-md dark:bg-slate-950/85">
        <div className="mx-auto flex max-w-6xl items-center gap-1 px-4 py-3 sm:gap-2">
          <Logo />
          <nav aria-label={t('nav.main')} className="ml-4 hidden md:block">
            <ul className="flex gap-1">
              <li>
                <Link to={{ pathname: '/', hash: 'about' }} className={textLink}>
                  {t('nav.about')}
                </Link>
              </li>
              <li>
                <Link to={{ pathname: '/', hash: 'faq' }} className={textLink}>
                  {t('nav.faq')}
                </Link>
              </li>
            </ul>
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <LanguageSelect />
            <ThemeToggle />
            {isPending ? null : user ? (
              <>
                <Link to="/search" className={`${pillPrimary} max-sm:hidden`}>
                  {t('auth.portal')}
                </Link>
                <Link to="/search" className={`${textLink} font-semibold text-ink sm:hidden`}>
                  {t('auth.portalShort')}
                </Link>
              </>
            ) : (
              <>
                <Link to="/login" className={textLink}>
                  {t('auth.login')}
                </Link>
                <Link to="/signup" className={`${pillPrimary} max-sm:hidden`}>
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
      <footer className="mx-auto w-full max-w-6xl px-4 py-10">
        <div
          className={`flex flex-col gap-3 text-sm sm:flex-row sm:items-center sm:justify-between ${muted}`}
        >
          <p>© 2026 JikUp · {t('footer.note')}</p>
          <ul className="flex gap-1">
            <li>
              <Link to={{ pathname: '/', hash: 'about' }} className={textLink}>
                {t('nav.about')}
              </Link>
            </li>
            <li>
              <Link to={{ pathname: '/', hash: 'faq' }} className={textLink}>
                {t('nav.faq')}
              </Link>
            </li>
          </ul>
        </div>
      </footer>
    </div>
  )
}
