import { Bar, BarChart, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import ChartTooltip from './ChartTooltip'

export type BarDatum = { label: string; value: number; detail: string }

const ROW_HEIGHT = 30
const AXIS_WIDTH = 132
const MAX_LABEL = 18

const shorten = (label: string) =>
  label.length > MAX_LABEL ? `${label.slice(0, MAX_LABEL - 1)}…` : label

type TipProps = { active?: boolean; payload?: { payload: BarDatum }[] }

function Tip({ active, payload }: TipProps) {
  const datum = payload?.[0]?.payload
  if (!active || !datum) return null
  return (
    <ChartTooltip title={datum.label} rows={[{ name: datum.detail, value: `${datum.value}%` }]} />
  )
}

export default function BarList({ data }: { data: BarDatum[] }) {
  return (
    <div style={{ height: data.length * ROW_HEIGHT + 8 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 48, bottom: 0, left: 0 }}>
          <XAxis type="number" hide domain={[0, 'dataMax']} />
          <YAxis
            type="category"
            dataKey="label"
            width={AXIS_WIDTH}
            tickLine={false}
            axisLine={{ stroke: 'var(--viz-axis)' }}
            tick={{ fill: 'var(--viz-text-2)', fontSize: 12 }}
            tickFormatter={shorten}
            interval={0}
          />
          <Tooltip content={<Tip />} cursor={{ fill: 'var(--viz-grid)', opacity: 0.5 }} />
          <Bar
            dataKey="value"
            fill="var(--series-1)"
            barSize={16}
            radius={[0, 4, 4, 0]}
            isAnimationActive={false}
          >
            <LabelList
              dataKey="value"
              position="right"
              formatter={(v: unknown) => `${v}%`}
              style={{ fill: 'var(--viz-text-2)', fontSize: 12 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
