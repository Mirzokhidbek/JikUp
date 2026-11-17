import { useEffect, useId, useState } from 'react'
import { NavLink, Outlet } from 'react-router'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { LanguageSelect, ThemeToggle } from './HeaderControls'
import { focusRing, iconButton, navLink } from './ui'

const NAV_ITEMS: { to: string; label: MessageKey }[] = [
  { to: '/search', label: 'nav.search' },
  { to: '/chat', label: 'nav.chat' },
  { to: '/copilot', label: 'nav.copilot' },
  { to: '/dashboard', label: 'nav.dashboard' },
]

function NavItems({
  vertical = false,
  onNavigate,
}: {
  vertical?: boolean
  onNavigate?: () => void
}) {
  const { t } = useI18n()
  return (
    <ul className={vertical ? 'flex flex-col gap-1' : 'flex gap-1'}>
      {NAV_ITEMS.map(({ to, label }) => (
        <li key={to}>
          <NavLink to={to} onClick={onNavigate} className={({ isActive }) => navLink(isActive)}>
            {t(label)}
          </NavLink>
        </li>
      ))}
    </ul>
  )
}

export default function Layout() {
  const { t } = useI18n()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuId = useId()
  useEffect(() => {
    if (!menuOpen) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setMenuOpen(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [menuOpen])

  return (
    <div className="min-h-screen bg-white text-ink dark:bg-slate-950 dark:text-slate-100">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
      >
        {t('a11y.skip')}
      </a>
      <header className="sticky top-0 z-40 bg-white/85 backdrop-blur-md dark:bg-slate-950/85">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3">
          <NavLink
            to="/"
            aria-label={t('nav.home')}
            className={`inline-flex min-h-11 shrink-0 items-center rounded-md ${focusRing}`}
          >
            <img
              src="/logo-light.png"
              alt="JikUp"
              width={480}
              height={164}
              className="h-9 w-auto dark:hidden"
            />
            <img
              src="/logo-dark.png"
              alt="JikUp"
              width={480}
              height={164}
              className="hidden h-9 w-auto dark:block"
            />
          </NavLink>
          <nav aria-label={t('nav.main')} className="hidden md:block">
            <NavItems />
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <LanguageSelect />
            <ThemeToggle />
            <button
              type="button"
              className={`${iconButton} md:hidden`}
              aria-expanded={menuOpen}
              aria-controls={menuId}
              aria-label={t(menuOpen ? 'nav.closeMenu' : 'nav.openMenu')}
              onClick={() => setMenuOpen((open) => !open)}
            >
              <svg
                viewBox="0 0 24 24"
                className="size-5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                aria-hidden="true"
              >
                <path d={menuOpen ? 'M6 6l12 12M18 6 6 18' : 'M4 7h16M4 12h16M4 17h16'} />
              </svg>
            </button>
          </div>
        </div>
        <nav
          id={menuId}
          aria-label={t('nav.main')}
          hidden={!menuOpen}
          className="border-t border-ink/8 px-4 py-3 md:hidden dark:border-white/8"
        >
          <NavItems vertical onNavigate={() => setMenuOpen(false)} />
        </nav>
      </header>
      <main id="main" className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
