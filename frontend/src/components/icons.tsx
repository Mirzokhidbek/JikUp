import { useId, type SVGProps } from 'react'

type IconProps = SVGProps<SVGSVGElement> & { size?: number }

function Icon({ size = 20, children, ...rest }: IconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      {children}
    </svg>
  )
}

export const HomeIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z" />
  </Icon>
)
export const JobsIcon = (p: IconProps) => (
  <Icon {...p}>
    <rect x="3" y="4" width="18" height="16" rx="5" />
    <path d="M8.5 12.5c1 1.4 2.2 2 3.5 2s2.5-.6 3.5-2M9 9.5h.01M15 9.5h.01" />
  </Icon>
)
export const ResumeIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
    <path d="M14 3v5h5M9 13h6M9 17h4" />
  </Icon>
)
export const CopilotIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="m15.5 8.5-2 5-5 2 2-5z" />
  </Icon>
)
export const AnalyticsIcon = (p: IconProps) => (
  <Icon {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M8.5 15v-3M12 15V9M15.5 15v-5" />
  </Icon>
)
export const ArrowRightIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M5 12h14M13 6l6 6-6 6" />
  </Icon>
)
export const ChevronDownIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="m6 9 6 6 6-6" />
  </Icon>
)
export const LogoutIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l5-5-5-5M15 12H3" />
  </Icon>
)

/** Filled, colored icons used in stat tiles and hero cards. */
export function BriefcaseBadge({ size = 44 }: { size?: number }) {
  const gradient = useId()
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id={gradient} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#3f7bff" />
          <stop offset="1" stopColor="#1443e2" />
        </linearGradient>
      </defs>
      <path
        d="M17 13a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2h-3.5v-2a.5.5 0 0 0-.5-.5h-6a.5.5 0 0 0-.5.5v2H17z"
        fill="#1443e2"
      />
      <rect x="6" y="15" width="36" height="25" rx="6" fill={`url(#${gradient})`} />
      <path
        d="M6 24c11 4 25 4 36 0"
        stroke="#fff"
        strokeOpacity=".35"
        strokeWidth="2"
        fill="none"
      />
      <rect x="21" y="23" width="6" height="5" rx="1.5" fill="#fff" />
    </svg>
  )
}

export function BarsBadge({ size = 44 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <rect x="6" y="26" width="8" height="16" rx="2" fill="#7aa5ff" />
      <rect x="18" y="18" width="8" height="24" rx="2" fill="#3f7bff" />
      <rect x="30" y="8" width="8" height="34" rx="2" fill="#1443e2" />
    </svg>
  )
}

export function ChipBadge({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <path
        d="M14 4v5M20 4v5M26 4v5M14 31v5M20 31v5M26 31v5M4 14h5M4 20h5M4 26h5M31 14h5M31 20h5M31 26h5"
        stroke="#1443e2"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <rect x="9" y="9" width="22" height="22" rx="5" fill="#1443e2" />
      <rect
        x="14"
        y="14"
        width="12"
        height="12"
        rx="2.5"
        fill="none"
        stroke="#fff"
        strokeWidth="2.2"
      />
    </svg>
  )
}

export function RocketBadge({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <path d="M13 27c-3 0-6 3-6 7 4 0 7-3 7-6z" fill="#f59e0b" />
      <path d="M33 5c-9 0-15 6-19 14l7 7c8-4 14-10 14-19 0-1-1-2-2-2z" fill="#1443e2" />
      <path d="M14 19h-6l5-6h7zM21 26v6l6-5v-7z" fill="#3f7bff" />
      <circle cx="25" cy="15" r="3" fill="#fff" />
    </svg>
  )
}

export function TrendBadge({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <path
        d="M5 28l10-10 6 6 13-13M25 11h9v9"
        stroke="#3fb46a"
        strokeWidth="3.2"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function CheckBadge({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="11" fill="#3fb46a" />
      <path
        d="m7 12.5 3.2 3L17 9"
        stroke="#fff"
        strokeWidth="2.4"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function Sparkle({ size = 28, className = '' }: { size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" className={className}>
      <path
        d="M12 0c.6 6.4 2.6 10.4 12 12-9.4 1.6-11.4 5.6-12 12-.6-6.4-2.6-10.4-12-12 9.4-1.6 11.4-5.6 12-12z"
        fill="currentColor"
      />
    </svg>
  )
}

export function PlayBadge({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 26 26" aria-hidden="true">
      <circle cx="13" cy="13" r="13" fill="#1443e2" />
      <path d="M10.5 8.5v9l7.5-4.5z" fill="#fff" />
    </svg>
  )
}
