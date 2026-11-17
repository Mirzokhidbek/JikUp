import { useCallback, useEffect, useState } from 'react'

export type Theme = 'system' | 'light' | 'dark'

const STORAGE_KEY = 'jikup.theme'
const ORDER: Theme[] = ['system', 'light', 'dark']
const darkQuery = () => window.matchMedia('(prefers-color-scheme: dark)')

function savedTheme(): Theme {
  const value = localStorage.getItem(STORAGE_KEY)
  return value === 'light' || value === 'dark' ? value : 'system'
}

function apply(theme: Theme) {
  const dark = theme === 'dark' || (theme === 'system' && darkQuery().matches)
  document.documentElement.classList.toggle('dark', dark)
}

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(savedTheme)

  useEffect(() => {
    apply(theme)
    if (theme === 'system') localStorage.removeItem(STORAGE_KEY)
    else localStorage.setItem(STORAGE_KEY, theme)
    if (theme !== 'system') return
    const query = darkQuery()
    const onChange = () => apply('system')
    query.addEventListener('change', onChange)
    return () => query.removeEventListener('change', onChange)
  }, [theme])

  const cycle = useCallback(
    () => setTheme((current) => ORDER[(ORDER.indexOf(current) + 1) % ORDER.length]),
    [],
  )
  return { theme, cycle }
}
