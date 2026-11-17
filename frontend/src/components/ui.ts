export const focusRing =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand dark:focus-visible:outline-blue-400'

const control = `inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 text-sm font-semibold whitespace-nowrap transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${focusRing}`

export const primaryButton = `${control} bg-brand text-white shadow-[0_8px_20px_-8px_rgb(20_67_226/0.6)] hover:bg-brand-strong dark:bg-blue-600 dark:hover:bg-blue-700 dark:shadow-none`

export const secondaryButton = `${control} bg-white text-ink ring-1 ring-line ring-inset hover:bg-brand-soft dark:bg-slate-900 dark:text-white dark:ring-white/15 dark:hover:bg-slate-800`

export const iconButton = `inline-flex size-11 items-center justify-center rounded-full text-slate-600 transition-colors hover:bg-brand-soft hover:text-brand dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white ${focusRing}`

export const navLink = (active: boolean) =>
  `flex min-h-11 items-center gap-3 rounded-xl px-3 text-[15px] font-medium whitespace-nowrap transition-colors ${focusRing} ${
    active
      ? 'bg-brand-soft text-brand dark:bg-blue-500/15 dark:text-blue-300'
      : 'text-[#4e5169] hover:bg-brand-soft/60 hover:text-ink dark:text-slate-400 dark:hover:bg-white/5 dark:hover:text-white'
  }`

export const muted = 'text-[#595a6e] dark:text-slate-400'

export const card =
  'rounded-2xl bg-white ring-1 ring-line shadow-[0_12px_32px_-18px_rgb(20_40_120/0.25)] dark:bg-slate-900 dark:ring-white/10 dark:shadow-none'

export const chip = 'rounded-md px-2 py-0.5 text-xs'

export const link = `font-medium text-brand underline-offset-4 hover:underline dark:text-blue-300 ${focusRing}`
