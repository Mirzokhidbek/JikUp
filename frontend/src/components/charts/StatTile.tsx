import { card, muted } from '../ui'

export default function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className={`${card} p-5`}>
      <p className={`text-sm ${muted}`}>{label}</p>
      <p className="mt-1 text-[28px] leading-tight font-[650] tracking-[-0.02em]">{value}</p>
    </div>
  )
}
