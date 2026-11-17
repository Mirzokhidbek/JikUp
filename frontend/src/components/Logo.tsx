import { useId } from 'react'
import { Link } from 'react-router'
import { useI18n } from '../i18n/useI18n'
import { focusRing } from './ui'

/** The J-arrow mark: a rising swoosh that ends in an arrow, with a dot for the "i". */
export function LogoMark({ size = 40 }: { size?: number }) {
  // Unique per instance: a shared id breaks when the first copy sits in a hidden subtree.
  const gradient = useId()
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden="true">
      <defs>
        <linearGradient id={gradient} x1="0" y1="0.6" x2="1" y2="0.2">
          <stop offset="0" stopColor="#5b95ff" />
          <stop offset="0.5" stopColor="#2a62f5" />
          <stop offset="1" stopColor="#1443e2" />
        </linearGradient>
      </defs>
      <circle cx="19" cy="24" r="6.5" fill="#7aa8ff" />
      <path
        d="M7 41c3 10 11 15 19 13 9-2 15-11 18-26"
        fill="none"
        stroke={`url(#${gradient})`}
        strokeWidth="12.5"
        strokeLinecap="round"
      />
      <path d="M48 2 62 27l-13-3.6-12.6 4.4z" fill="#1747e8" />
    </svg>
  )
}

export function Wordmark({ size = 'text-[28px]' }: { size?: string }) {
  return (
    <span className={`${size} leading-none font-bold tracking-[-0.03em] text-ink dark:text-white`}>
      JikUp
    </span>
  )
}

export default function Logo({
  compact = false,
  responsive = false,
}: {
  compact?: boolean
  responsive?: boolean
}) {
  const { t } = useI18n()
  return (
    <Link
      to="/"
      aria-label={t('nav.home')}
      className={`inline-flex min-h-11 shrink-0 items-center gap-2 rounded-md ${focusRing}`}
    >
      <span className={responsive ? 'contents max-sm:hidden' : 'contents'}>
        <LogoMark size={compact ? 34 : 58} />
        <Wordmark size={compact ? 'text-[22px]' : 'text-[34px]'} />
      </span>
      {responsive && (
        <span className="contents sm:hidden">
          <LogoMark size={36} />
          <Wordmark size="text-[24px]" />
        </span>
      )}
    </Link>
  )
}
