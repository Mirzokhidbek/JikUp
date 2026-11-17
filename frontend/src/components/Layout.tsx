import { NavLink, Outlet } from 'react-router'

const NAV_ITEMS = [
  { to: '/search', label: 'Search' },
  { to: '/chat', label: 'Chat' },
  { to: '/copilot', label: 'Copilot' },
  { to: '/dashboard', label: 'Dashboard' },
]

const focusRing =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand'

export default function Layout() {
  return (
    <div className="min-h-screen bg-white text-ink">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
      >
        Skip to content
      </a>
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
          <NavLink to="/" aria-label="JikUp home" className={`shrink-0 rounded-md ${focusRing}`}>
            <img src="/logo.png" alt="JikUp" width={480} height={164} className="h-9 w-auto" />
          </NavLink>
          <nav aria-label="Main" className="flex gap-1 overflow-x-auto">
            {NAV_ITEMS.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `rounded-md px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors ${focusRing} ${
                    isActive
                      ? 'bg-brand/10 text-brand'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-ink'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main id="main" className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
