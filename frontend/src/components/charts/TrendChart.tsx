import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TrendReport } from '../../api/types'
import ChartTooltip from './ChartTooltip'

type Props = {
  report: TrendReport
  colorOf: (skill: string) => string
  formatWeek: (week: string) => string
}

type TipProps = {
  active?: boolean
  label?: string
  payload?: { name: string; value: number; color: string }[]
  formatWeek: (week: string) => string
}

function Tip({ active, label: week, payload, formatWeek }: TipProps) {
  if (!active || !payload?.length) return null
  return (
    <ChartTooltip
      title={formatWeek(String(week))}
      rows={[...payload]
        .sort((a, b) => b.value - a.value)
        .map((p) => ({ name: p.name, value: String(p.value), color: p.color }))}
    />
  )
}

export default function TrendChart({ report, colorOf, formatWeek }: Props) {
  const data = report.weeks.map((week, i) => ({
    week,
    ...Object.fromEntries(report.series.map((s) => [s.skill, s.counts[i]])),
  }))
  const order = report.series.map((s) => s.skill)

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
          <CartesianGrid vertical={false} stroke="var(--viz-grid)" />
          <XAxis
            dataKey="week"
            tickFormatter={formatWeek}
            tickLine={false}
            axisLine={{ stroke: 'var(--viz-axis)' }}
            tick={{ fill: 'var(--viz-muted)', fontSize: 12 }}
            minTickGap={16}
          />
          <YAxis
            allowDecimals={false}
            tickLine={false}
            axisLine={false}
            tick={{ fill: 'var(--viz-muted)', fontSize: 12 }}
          />
          <Tooltip
            content={<Tip formatWeek={formatWeek} />}
            cursor={{ stroke: 'var(--viz-axis)', strokeWidth: 1 }}
          />
          <Legend
            verticalAlign="top"
            align="left"
            iconType="plainline"
            itemSorter={(item) => order.indexOf(String(item.value))}
            wrapperStyle={{ fontSize: 12, color: 'var(--viz-text-2)', paddingBottom: 8 }}
          />
          {report.series.map((s) => (
            <Line
              key={s.skill}
              dataKey={s.skill}
              name={s.skill}
              stroke={colorOf(s.skill)}
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2, stroke: 'var(--viz-surface)' }}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
