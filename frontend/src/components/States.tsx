import { ApiError } from '../api/client'
import { useI18n } from '../i18n/useI18n'
import { card, focusRing, muted } from './ui'

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  const { t } = useI18n()
  return (
    <div role="status" aria-label={t('common.loading')} className="space-y-3">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className={`${card} p-4 motion-safe:animate-pulse`}>
          <div className="h-4 w-2/3 rounded bg-fill-strong" />
          <div className="mt-3 h-3 w-1/3 rounded bg-fill-strong" />
          <div className="mt-4 flex gap-2">
            <div className="h-5 w-14 rounded bg-fill-strong" />
            <div className="h-5 w-16 rounded bg-fill-strong" />
          </div>
        </div>
      ))}
    </div>
  )
}

type ErrorProps = { message?: string; error?: Error | null; onRetry?: () => void }

export function ErrorState({ message, error, onRetry }: ErrorProps) {
  const { t } = useI18n()
  const text =
    error instanceof ApiError && error.status === 429
      ? t('common.rateLimited')
      : error instanceof ApiError && error.status === 503
        ? t('common.llmOff')
        : (error?.message ?? message)
  return (
    <div
      role="alert"
      className="rounded-xl bg-red-50 p-5 text-red-800 dark:bg-red-950/60 dark:text-red-200"
    >
      <p className="font-medium">{t('common.error')}</p>
      {text && <p className="mt-1 text-sm">{text}</p>}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className={`mt-3 min-h-11 rounded-lg bg-red-100 px-4 text-sm font-semibold hover:bg-red-200 dark:bg-red-900/60 dark:hover:bg-red-900 ${focusRing}`}
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
