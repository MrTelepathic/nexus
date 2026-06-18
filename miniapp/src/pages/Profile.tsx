/**
 * Profile Page — User profile, badges, XP
 */

import { motion } from 'framer-motion'
import { useAuth } from '../providers/AuthProvider'
import { useNavigate } from 'react-router-dom'
import { useHaptic } from '../hooks/useHaptic'
import XPBar from '../components/gamification/XPBar'

export default function Profile() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const { impactOccurred } = useHaptic()

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      {/* Avatar + Name */}
      <div className="text-center mb-6">
        <div className="w-20 h-20 rounded-full bg-tg-button mx-auto mb-3 flex items-center justify-center text-3xl">
          {user?.first_name?.[0] || '?'}
        </div>
        <h1 className="text-xl font-bold">{user?.first_name || 'User'}</h1>
        <p className="text-tg-text-secondary text-sm">@{user?.username || 'unknown'}</p>
      </div>

      {/* XP Bar */}
      <div className="bg-tg-section-bg rounded-2xl p-4 mb-4">
        <XPBar xp={750} level={5} nextLevelXp={1000} />
      </div>

      {/* Badges */}
      <div className="bg-tg-section-bg rounded-2xl p-4 mb-4">
        <h2 className="font-semibold mb-3">Badges</h2>
        <div className="flex gap-2">
          {['🏆', '⭐', '🔥', '💎'].map((badge, i) => (
            <span key={i} className="text-2xl p-2 bg-tg-bg rounded-xl">
              {badge}
            </span>
          ))}
        </div>
      </div>

      {/* Menu */}
      <div className="space-y-1">
        {[
          { label: 'Leaderboard', icon: '🏆', path: '/leaderboard' },
          { label: 'Referrals', icon: '👥', path: '/referrals' },
          { label: 'Settings', icon: '⚙️', path: '/settings' },
        ].map((item) => (
          <button
            key={item.path}
            onClick={() => {
              impactOccurred('light')
              navigate(item.path)
            }}
            className="w-full flex items-center gap-3 p-4 bg-tg-section-bg rounded-xl"
          >
            <span>{item.icon}</span>
            <span className="flex-1 text-left">{item.label}</span>
            <span className="text-tg-text-secondary">›</span>
          </button>
        ))}
      </div>
    </motion.div>
  )
}
