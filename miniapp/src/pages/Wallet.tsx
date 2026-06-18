/**
 * Wallet Page — Balance, transactions, cashback
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useBiometric } from '../hooks/useBiometric'
import { useHaptic } from '../hooks/useHaptic'
import { formatCurrency } from '../lib/utils'

export default function Wallet() {
  const { isAvailable, isAuthenticated, authenticate } = useBiometric()
  const { impactOccurred } = useHaptic()
  const [balance] = useState(2450)

  const handleAuth = async () => {
    impactOccurred('medium')
    if (isAvailable) {
      await authenticate()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Wallet</h1>

      {/* Balance Card */}
      <div className="bg-gradient-to-br from-tg-button to-blue-600 rounded-2xl p-6 text-white mb-6">
        <p className="text-sm opacity-80">Total Balance</p>
        <p className="text-3xl font-bold mt-1">{formatCurrency(balance)}</p>
        <div className="flex gap-2 mt-4">
          <button
            onClick={handleAuth}
            className="px-4 py-2 bg-white/20 rounded-xl text-sm"
          >
            {isAuthenticated ? '🔓 Verified' : '🔐 Verify'}
          </button>
          <button className="px-4 py-2 bg-white/20 rounded-xl text-sm">
            Add Funds
          </button>
        </div>
      </div>

      {/* Recent Transactions */}
      <h2 className="font-semibold mb-3">Recent</h2>
      <div className="text-center text-tg-text-secondary py-8">
        <p className="text-sm">No transactions yet</p>
      </div>
    </motion.div>
  )
}
