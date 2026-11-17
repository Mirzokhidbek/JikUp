import type { ReactNode } from 'react'

type PageProps = {
  title: string
  lead?: string
  children?: ReactNode
}

export default function Page({ title, lead, children }: PageProps) {
  return (
    <>
      <title>{`${title} | JikUp`}</title>
      <h1 className="max-w-3xl text-[28px] leading-tight font-[650] tracking-[-0.02em] sm:text-[32px]">
        {title}
        {lead && (
          <span className="font-[550] text-slate-500 dark:text-slate-400">
            {'. '}
            {lead}
          </span>
        )}
      </h1>
      {children}
    </>
  )
}
