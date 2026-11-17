import { useEffect, useId, useState, type ComponentType } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router'
import { useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'
import { displayName } from '../lib/user'
import Avatar from './Avatar'
import { LanguageFlag, ThemeToggle } from './HeaderControls'
import { AnalyticsIcon, CopilotIcon, HomeIcon, JobsIcon, LogoutIcon, ResumeIcon } from './icons'
import Logo from './Logo'
import { iconButton, muted, navLink } from './ui'

type NavItem = { to: string; label: MessageKey; icon: ComponentType<{ size?: number }> }

const NAV_ITEMS: NavItem[] = [
  { to: '/dashboard', label: 'nav.overview', icon: HomeIcon },
  { to: '/search', label: 'nav.search', icon: JobsIcon },
  { to: '/copilot', label: 'nav.resume', icon: ResumeIcon },
  { to: '/chat', label: 'nav.chat', icon: CopilotIcon },
  { to: '/analytics', label: 'nav.dashboard', icon: AnalyticsIcon },
]

function NavItems({ onNavigate }: { onNavigate?: () => void }) {
  const { t } = useI18n()
  return (
    <ul className="space-y-1">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <li key={to}>
          <NavLink to={to} onClick={onNavigate} className={({ isActive }) => navLink(isActive)}>
            <Icon size={20} />
            {t(label)}
          </NavLink>
        </li>
      ))}
    </ul>
  )
}

function Account({ onSignOut }: { onSignOut: () => void }) {
  const { t } = useI18n()
  const { user } = useAuth()
  if (!user) return null
  return (
    <div className="flex items-center gap-3 rounded-2xl bg-page p-3 dark:bg-white/5">
      <Avatar email={user.email} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-ink dark:text-white">
          {displayName(user.email)}
        </p>
        <p
          className={`truncate text-xs ${muted}`}
          title={t('auth.signedInAs', { email: user.email })}
        >
          {user.email}
        </p>
      </div>
      <button
        type="button"
        onClick={onSignOut}
        className={iconButton}
        aria-label={t('auth.logout')}
        title={t('auth.logout')}
      >
        <LogoutIcon size={19} />
      </button>
    </div>
  )
}

export default function Layout() {
  const { t } = useI18n()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuId = useId()
  const { logout } = useAuth()
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
    <div className="min-h-screen bg-page text-ink lg:grid lg:grid-cols-[272px_minmax(0,1fr)] dark:bg-slate-950 dark:text-slate-100">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
      >
        {t('a11y.skip')}
      </a>

      <aside className="sticky top-0 hidden h-screen p-4 lg:block">
        <div className="flex h-full flex-col rounded-[26px] bg-white p-4 shadow-[0_20px_50px_-30px_rgb(20_40_120/0.35)] ring-1 ring-line dark:bg-slate-900 dark:ring-white/10">
          <div className="px-2 pt-2 pb-8">
            <Logo compact />
          </div>
          <nav aria-label={t('nav.main')}>
            <NavItems />
          </nav>
          <div className="mt-auto space-y-3">
            <div className="flex items-center gap-2 px-1">
              <LanguageFlag />
              <ThemeToggle />
            </div>
            <Account onSignOut={signOut} />
          </div>
        </div>
      </aside>

      <header className="sticky top-0 z-40 bg-page/90 backdrop-blur-md lg:hidden dark:bg-slate-950/90">
        <div className="flex items-center gap-2 px-4 py-3">
          <Logo compact />
          <div className="ml-auto flex items-center gap-2">
            <LanguageFlag />
            <button
              type="button"
              className={`${iconButton} bg-white ring-1 ring-line dark:bg-slate-900 dark:ring-white/10`}
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
          className="mx-4 mb-3 space-y-3 rounded-2xl bg-white p-3 ring-1 ring-line dark:bg-slate-900 dark:ring-white/10"
        >
          <NavItems onNavigate={() => setMenuOpen(false)} />
          <div className="flex items-center gap-2 px-1">
            <ThemeToggle />
          </div>
          <Account onSignOut={signOut} />
        </nav>
      </header>

      <main id="main" className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        <Outlet />
      </main>
    </div>
  )
}
