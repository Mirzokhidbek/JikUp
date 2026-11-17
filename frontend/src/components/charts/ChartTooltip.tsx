type Row = { name: string; value: string; color?: string }

export default function ChartTooltip({ title, rows }: { title: string; rows: Row[] }) {
  return (
    <div className="rounded-lg bg-white px-3 py-2 text-xs shadow-lg ring-1 ring-ink/5 dark:bg-slate-900 dark:ring-white/10">
      <p className="mb-1 text-slate-600 dark:text-slate-400">{title}</p>
      <ul className="space-y-0.5">
        {rows.map((row) => (
          <li key={row.name} className="flex items-center gap-2">
            {row.color && (
              <span
                aria-hidden="true"
                className="h-0.5 w-3 rounded"
                style={{ backgroundColor: row.color }}
              />
            )}
            <strong className="font-semibold text-slate-900 dark:text-slate-100">
              {row.value}
            </strong>
            <span className="text-slate-600 dark:text-slate-400">{row.name}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
