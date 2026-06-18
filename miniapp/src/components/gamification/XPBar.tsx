/**
 * XPBar — Experience points progress bar
 */

interface Props {
  xp: number
  level: number
  nextLevelXp: number
}

export default function XPBar({ xp, level, nextLevelXp }: Props) {
  const progress = (xp / nextLevelXp) * 100

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">Level {level}</span>
        <span className="text-xs text-tg-text-secondary">
          {xp}/{nextLevelXp} XP
        </span>
      </div>
      <div className="w-full h-2 bg-tg-bg rounded-full overflow-hidden">
        <div
          className="h-full bg-tg-accent rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
