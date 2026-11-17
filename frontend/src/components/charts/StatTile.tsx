import { card, muted } from '../ui'

export default function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className={`${card} p-4`}>
      <p className={`text-sm ${muted}`}>{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight">{value}</p>
    </div>
  )
}
