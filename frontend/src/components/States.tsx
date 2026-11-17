import { useI18n } from '../i18n/useI18n'
import { card, focusRing, muted } from './ui'

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  const { t } = useI18n()
  return (
    <div role="status" aria-label={t('common.loading')} className="space-y-3">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className={`${card} p-4 motion-safe:animate-pulse`}>
          <div className="h-4 w-2/3 rounded bg-slate-200 dark:bg-slate-800" />
          <div className="mt-3 h-3 w-1/3 rounded bg-slate-200 dark:bg-slate-800" />
          <div className="mt-4 flex gap-2">
            <div className="h-5 w-14 rounded bg-slate-200 dark:bg-slate-800" />
            <div className="h-5 w-16 rounded bg-slate-200 dark:bg-slate-800" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  const { t } = useI18n()
  return (
    <div
      role="alert"
      className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-200"
    >
      <p className="font-medium">{t('common.error')}</p>
      {message && <p className="mt-1 text-sm">{message}</p>}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className={`mt-3 min-h-11 rounded-md border border-current px-4 text-sm font-medium hover:bg-red-100 dark:hover:bg-red-900 ${focusRing}`}
        >
          {t('common.retry')}
        </button>
      )}
    </div>
  )
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className={`${card} p-8 text-center`}>
      <p className="font-medium">{title}</p>
      {hint && <p className={`mt-1 text-sm ${muted}`}>{hint}</p>}
    </div>
  )
}
