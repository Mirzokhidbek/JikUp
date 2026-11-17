import type { ReactNode } from 'react'

type PageProps = {
  title: string
  children?: ReactNode
}

export default function Page({ title, children }: PageProps) {
  return (
    <>
      <title>{`${title} | JikUp`}</title>
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      {children}
    </>
  )
}
