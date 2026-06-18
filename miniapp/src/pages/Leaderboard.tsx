/**
 * Leaderboard Page — Live rankings via WebSocket
 */

import { motion } from 'framer-motion'
import { useRoomSubscription } from '../hooks/useWebSocket'

export default function Leaderboard() {
  useRoomSubscription('leaderboard')

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Leaderboard</h1>

      <div className="space-y-2">
        {[
          { rank: 1, name: 'Alice', xp: 12500, level: 12 },
          { rank: 2, name: 'Bob', xp: 11200, level: 11 },
          { rank: 3, name: 'Charlie', xp: 9800, level: 10 },
        ].map((entry, i) => (
          <motion.div
            key={entry.rank}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className="flex items-center gap-3 p-4 bg-tg-section-bg rounded-xl"
          >
            <span className="text-xl font-bold w-8">
              {entry.rank === 1 ? '🥇' : entry.rank === 2 ? '🥈' : entry.rank === 3 ? '🥉' : `#${entry.rank}`}
            </span>
            <div className="flex-1">
              <p className="font-medium">{entry.name}</p>
              <p className="text-xs text-tg-text-secondary">Level {entry.level}</p>
            </div>
            <span className="font-bold text-tg-accent">{entry.xp.toLocaleString()} XP</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
