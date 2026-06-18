/**
 * Referrals Page — Referral tree and earnings
 */

import { motion } from 'framer-motion'
import { useHaptic } from '../hooks/useHaptic'
import WebApp from '@twa-dev/sdk'

export default function Referrals() {
  const { impactOccurred } = useHaptic()

  const handleShare = () => {
    impactOccurred('medium')
    WebApp.switchInlineQuery('Join Nexus! 🚀', ['users', 'groups', 'channels'])
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Referrals</h1>

      {/* Referral Stats */}
      <div className="bg-gradient-to-br from-purple-500 to-blue-500 rounded-2xl p-6 text-white mb-6">
        <p className="text-sm opacity-80">Total Earned</p>
        <p className="text-3xl font-bold mt-1">⭐ 0</p>
        <p className="text-sm opacity-80 mt-2">0 referrals · 10% commission</p>
      </div>

      {/* Share Button */}
      <button
        onClick={handleShare}
        className="w-full py-3 bg-tg-button text-tg-button-text rounded-xl font-medium mb-6"
      >
        Share Referral Link
      </button>

      {/* Referral Tree */}
      <h2 className="font-semibold mb-3">Your Referrals</h2>
      <div className="text-center text-tg-text-secondary py-8">
        <span className="text-4xl mb-4 block">👥</span>
        <p className="text-sm">No referrals yet</p>
        <p className="text-xs mt-1">Share your link to earn 10% commission</p>
      </div>
    </motion.div>
  )
}
