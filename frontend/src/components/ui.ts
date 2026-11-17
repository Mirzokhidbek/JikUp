export const focusRing =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand dark:focus-visible:outline-blue-400'

export const iconButton = `inline-flex size-11 items-center justify-center rounded-md text-slate-600 transition-colors hover:bg-slate-100 hover:text-ink dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white ${focusRing}`

export const navLink = (active: boolean) =>
  `flex min-h-11 items-center rounded-md px-3 text-sm font-medium whitespace-nowrap transition-colors ${focusRing} ${
    active
      ? 'bg-brand/10 text-blue-700 dark:bg-blue-400/15 dark:text-blue-300'
      : 'text-slate-600 hover:bg-slate-100 hover:text-ink dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
  }`

export const muted = 'text-slate-600 dark:text-slate-400'

export const card =
  'rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900'

export const link = `font-medium text-brand underline-offset-4 hover:underline dark:text-blue-300 ${focusRing}`
