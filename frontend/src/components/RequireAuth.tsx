import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router'
import { useAuth } from '../hooks/useAuth'
import { useI18n } from '../i18n/useI18n'
import { muted } from './ui'

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { t } = useI18n()
  const { user, isPending } = useAuth()
  const location = useLocation()
  if (isPending) {
    return (
      <p role="status" className={`p-8 text-center text-sm ${muted}`}>
        {t('auth.checking')}
      </p>
    )
  }
  if (!user) {
    const next = encodeURIComponent(location.pathname + location.search)
    return <Navigate to={`/login?next=${next}`} replace />
  }
  return children
}
