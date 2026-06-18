/**
 * StatsCard — Dashboard statistics card with icon and value
 */

interface Props {
  label: string
  value: string
  icon: string
  color: string
}

export default function StatsCard({ label, value, icon, color }: Props) {
  return (
    <div className="bg-tg-section-bg rounded-2xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <span className={`text-lg p-1.5 rounded-lg ${color}`}>{icon}</span>
      </div>
      <p className="text-xl font-bold">{value}</p>
      <p className="text-tg-text-secondary text-xs mt-1">{label}</p>
    </div>
  )
}
