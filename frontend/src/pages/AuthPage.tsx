import { useId, useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router'
import { ApiError } from '../api/client'
import { inputClass } from '../components/SkillInput'
import { link, muted, primaryButton } from '../components/ui'
import { safeNext, useAuth } from '../hooks/useAuth'
import type { MessageKey } from '../i18n/en'
import { useI18n } from '../i18n/useI18n'

type Mode = 'login' | 'signup'

function errorKey(error: unknown, mode: Mode): MessageKey {
  if (!(error instanceof ApiError)) return 'auth.failed'
  if (error.status === 401) return 'auth.wrong'
  if (error.status === 409) return 'auth.taken'
  if (error.status === 422) return mode === 'login' ? 'auth.wrong' : 'auth.invalid'
  if (error.status === 429) return 'common.rateLimited'
  return 'auth.failed'
}

export default function AuthPage({ mode }: { mode: Mode }) {
  const { t } = useI18n()
  const { user, login, register } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const next = safeNext(params.get('next'))
  const emailId = useId()
  const passwordId = useId()
  const hintId = useId()
  const errorId = useId()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const action = mode === 'login' ? login : register

  if (user && !action.isPending) return <Navigate to={next} replace />

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    action.mutate({ email, password }, { onSuccess: () => navigate(next, { replace: true }) })
  }

  const isLogin = mode === 'login'
  const otherQuery = params.get('next') ? `?next=${encodeURIComponent(next)}` : ''

  return (
    <div className="mx-auto max-w-md px-4 py-16 sm:py-24">
      <title>{`${t(isLogin ? 'auth.login' : 'auth.signup')} | JikUp`}</title>
      <h1 className="text-[36px] leading-[1.05] font-[650] tracking-[-0.03em]">
        {t(isLogin ? 'auth.loginTitle' : 'auth.signupTitle')}.{' '}
        <span className="font-[550] text-slate-500 dark:text-slate-400">
          {t(isLogin ? 'auth.loginLead' : 'auth.signupLead')}
        </span>
      </h1>

      <form onSubmit={onSubmit} className="mt-10 space-y-5" noValidate={false}>
        <div>
          <label
            htmlFor={emailId}
            className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            {t('auth.email')}
          </label>
          <input
            id={emailId}
            type="email"
            required
            maxLength={254}
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={`${inputClass} h-12`}
            aria-describedby={action.isError ? errorId : undefined}
          />
        </div>
        <div>
          <label
            htmlFor={passwordId}
            className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
          >
            {t('auth.password')}
          </label>
          <input
            id={passwordId}
            type="password"
            required
            minLength={8}
            maxLength={128}
            autoComplete={isLogin ? 'current-password' : 'new-password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={`${inputClass} h-12`}
            aria-describedby={[isLogin ? '' : hintId, action.isError ? errorId : '']
              .filter(Boolean)
              .join(' ')}
          />
          {!isLogin && (
            <p id={hintId} className={`mt-1.5 text-xs ${muted}`}>
              {t('auth.passwordHint')}
            </p>
          )}
        </div>

        {action.isError && (
          <p
            id={errorId}
            role="alert"
            className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-800 dark:bg-red-950/60 dark:text-red-200"
          >
            {t(errorKey(action.error, mode))}
          </p>
        )}

        <button
          type="submit"
          disabled={action.isPending}
          className={`${primaryButton} min-h-12 w-full rounded-full text-base`}
        >
          {action.isPending
            ? t('auth.busy')
            : t(isLogin ? 'auth.submitLogin' : 'auth.submitSignup')}
        </button>
      </form>

      <p className={`mt-6 text-sm ${muted}`}>
        {t(isLogin ? 'auth.noAccount' : 'auth.haveAccount')}{' '}
        <Link
          to={`${isLogin ? '/signup' : '/login'}${otherQuery}`}
          className={`inline-flex min-h-11 items-center ${link}`}
        >
          {t(isLogin ? 'auth.signup' : 'auth.login')}
        </Link>
      </p>
      {!isLogin && <p className={`mt-2 text-xs ${muted}`}>{t('auth.privacy')}</p>}
    </div>
  )
}
