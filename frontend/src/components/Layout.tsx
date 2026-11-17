import { useEffect, useId, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { LanguageSelect, ThemeToggle } from './HeaderControls'
import Logo from './Logo'
import { iconButton, muted, navLink, secondaryButton } from './ui'

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
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  // Leave the portal first: once the session is cleared this layout unmounts.
  const signOut = () => {
    navigate('/', { replace: true })
    logout.mutate()
  }
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
          <Logo />
          <nav aria-label={t('nav.main')} className="hidden md:block">
            <NavItems />
          </nav>
          <div className="ml-auto flex items-center gap-2">
            <LanguageSelect />
            <ThemeToggle />
            {user && (
              <span
                className={`hidden max-w-48 truncate text-sm lg:inline ${muted}`}
                title={t('auth.signedInAs', { email: user.email })}
              >
                {user.email}
              </span>
            )}
            <button type="button" onClick={signOut} className={`${secondaryButton} max-md:hidden`}>
              {t('auth.logout')}
            </button>
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
          {user && <p className={`mt-3 truncate px-3 text-sm ${muted}`}>{user.email}</p>}
          <button type="button" onClick={signOut} className={`${secondaryButton} mt-2 w-full`}>
            {t('auth.logout')}
          </button>
        </nav>
      </header>
      <main id="main" className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
