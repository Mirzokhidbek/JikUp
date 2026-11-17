import type { ReactNode } from 'react'
import { useI18n } from '../../i18n/useI18n'
import { card, focusRing, muted } from '../ui'

export type TableColumn = { header: string; numeric?: boolean }

type Props = {
  title: string
  hint?: string
  busy?: boolean
  columns: TableColumn[]
  rows: (string | number)[][]
  children: ReactNode
  className?: string
}

export default function ChartCard({
  title,
  hint,
  busy,
  columns,
  rows,
  children,
  className,
}: Props) {
  const { t } = useI18n()
  return (
    <section className={`${card} viz-root min-w-0 p-5 ${className ?? ''}`} aria-busy={busy}>
      <h2 className="font-semibold tracking-tight">{title}</h2>
      {hint && <p className={`mt-0.5 text-sm ${muted}`}>{hint}</p>}
      <div className={`mt-4 transition-opacity ${busy ? 'opacity-50' : ''}`}>
        {rows.length === 0 ? <p className={`text-sm ${muted}`}>{t('dash.noData')}</p> : children}
      </div>
      {rows.length > 0 && (
        <details className="mt-3 text-sm">
          <summary
            className={`inline-flex min-h-11 cursor-pointer items-center ${muted} ${focusRing}`}
          >
            {t('dash.table')}
          </summary>
          <div className="overflow-x-auto">
            <table className="mt-2 w-full text-left">
              <caption className="sr-only">{title}</caption>
              <thead>
                <tr className="border-b border-ink/10 dark:border-white/10">
                  {columns.map((col) => (
                    <th
                      key={col.header}
                      scope="col"
                      className={`py-1.5 pr-4 font-medium ${col.numeric ? 'text-right' : ''}`}
                    >
                      {col.header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={i} className="border-b border-ink/5 dark:border-white/5">
                    {row.map((cell, j) => (
                      <td
                        key={j}
                        className={`py-1.5 pr-4 ${columns[j]?.numeric ? 'text-right tabular-nums' : ''}`}
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </section>
  )
}
