/**
 * API response types
 */

export interface ApiResponse<T> {
  data: T
  status: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

export interface DashboardStats {
  total_customers: number
  active_conversations: number
  revenue_today: number
  revenue_month: number
  total_orders: number
  avg_rating: number
  conversion_rate: number
  active_products: number
}

export interface Product {
  id: string
  name: string
  description: string | null
  category: string | null
  price: number
  currency: string
  stock: number
  images: string[]
  tags: string[]
  rating: number | null
  review_count: number
  is_active: boolean
}

export interface Order {
  id: string
  status: string
  total_amount: number
  currency: string
  items: Record<string, unknown>[]
  created_at: string
}

export interface Payment {
  id: string
  amount: number
  currency: string
  method: string
  status: string
  external_id: string | null
  created_at: string
}

export interface GamificationProfile {
  xp: number
  level: number
  daily_streak: number
  longest_streak: number
  badges: { id: string; name: string; icon_emoji: string; rarity: string }[]
  next_level_xp: number
}

export interface LeaderboardEntry {
  rank: number
  user_id: number
  username: string | null
  xp: number
  level: number
}
