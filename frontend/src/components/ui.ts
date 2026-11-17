export const focusRing =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand dark:focus-visible:outline-blue-400'

const control = `inline-flex min-h-11 items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${focusRing}`

export const primaryButton = `${control} bg-ink text-white hover:bg-ink/85 dark:bg-white dark:text-ink dark:hover:bg-white/85`

export const secondaryButton = `${control} bg-fill-strong text-ink hover:bg-ink/12 dark:text-white dark:hover:bg-white/15`

export const iconButton = `inline-flex size-11 items-center justify-center rounded-lg text-slate-600 transition-colors hover:bg-fill-strong hover:text-ink dark:text-slate-300 dark:hover:text-white ${focusRing}`

export const navLink = (active: boolean) =>
  `flex min-h-11 items-center rounded-lg px-3 text-sm font-medium whitespace-nowrap transition-colors ${focusRing} ${
    active
      ? 'bg-fill-strong text-ink dark:text-white'
      : 'text-slate-600 hover:bg-fill hover:text-ink dark:text-slate-400 dark:hover:text-white'
  }`

export const muted = 'text-slate-600 dark:text-slate-400'

export const card = 'rounded-xl bg-fill'

export const chip = 'rounded-md px-2 py-0.5 text-xs'

export const link = `font-medium text-brand underline-offset-4 hover:underline dark:text-blue-300 ${focusRing}`
