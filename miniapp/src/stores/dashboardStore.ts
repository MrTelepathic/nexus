/**
 * Dashboard Store — Zustand state for live dashboard data
 */

import { create } from 'zustand'

interface Activity {
  id: string
  type: string
  description: string
  timestamp: Date
  user_name: string | null
}

interface DashboardState {
  stats: {
    total_customers: number
    active_conversations: number
    revenue_today: number
    revenue_month: number
    total_orders: number
    avg_rating: number
    conversion_rate: number
    active_products: number
  } | null
  activity: Activity[]
  setStats: (stats: DashboardState['stats']) => void
  addActivity: (activity: Activity) => void
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  activity: [],
  setStats: (stats) => set({ stats }),
  addActivity: (activity) =>
    set((state) => ({
      activity: [activity, ...state.activity].slice(0, 50),
    })),
}))
