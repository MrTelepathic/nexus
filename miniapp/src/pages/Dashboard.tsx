/**
 * Dashboard Page — Live Business Analytics
 *
 * Real-time stats, charts, and activity feed.
 * Uses WebSocket for live updates.
 */

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useWebSocket, useRoomSubscription } from '../hooks/useWebSocket'
import { useHaptic } from '../hooks/useHaptic'
import { formatNumber, formatCurrency, timeAgo } from '../lib/utils'
import StatsCard from '../components/dashboard/StatsCard'
import SalesChart from '../components/dashboard/SalesChart'
import LiveFeed from '../components/dashboard/LiveFeed'

interface DashboardStats {
  total_customers: number
  active_conversations: number
  revenue_today: number
  revenue_month: number
  total_orders: number
  avg_rating: number
  conversion_rate: number
  active_products: number
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { impactOccurred } = useHaptic()
  const { isConnected, subscribe } = useWebSocket()
  const [stats, setStats] = useState<DashboardStats | null>(null)

  useRoomSubscription('dashboard')

  useEffect(() => {
    // Fetch initial stats
    // In production: api.get('/dashboard/stats')
    setStats({
      total_customers: 1234,
      active_conversations: 89,
      revenue_today: 2450,
      revenue_month: 12450,
      total_orders: 342,
      avg_rating: 4.8,
      conversion_rate: 3.2,
      active_products: 47,
    })
  }, [])

  const statsCards = stats
    ? [
        { label: 'Revenue Today', value: formatCurrency(stats.revenue_today), icon: '💰', color: 'bg-green-500/10 text-green-600' },
        { label: 'Active Chats', value: stats.active_conversations.toString(), icon: '💬', color: 'bg-blue-500/10 text-blue-600' },
        { label: 'Total Orders', value: formatNumber(stats.total_orders), icon: '📦', color: 'bg-purple-500/10 text-purple-600' },
        { label: 'Customers', value: formatNumber(stats.total_customers), icon: '👥', color: 'bg-orange-500/10 text-orange-600' },
      ]
    : []

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-tg-text-secondary text-sm">
            {isConnected ? '🟢 Live' : '🔴 Connecting...'}
          </p>
        </div>
        <button
          onClick={() => {
            impactOccurred('light')
            navigate('/settings')
          }}
          className="p-2 rounded-full bg-tg-section-bg"
        >
          ⚙️
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        {statsCards.map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <StatsCard {...card} />
          </motion.div>
        ))}
      </div>

      {/* Revenue Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-tg-section-bg rounded-2xl p-4 mb-6"
      >
        <h2 className="font-semibold mb-3">Revenue</h2>
        <SalesChart />
      </motion.div>

      {/* Live Activity Feed */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-tg-section-bg rounded-2xl p-4"
      >
        <h2 className="font-semibold mb-3">Activity</h2>
        <LiveFeed />
      </motion.div>
    </motion.div>
  )
}
