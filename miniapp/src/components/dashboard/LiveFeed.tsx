/**
 * LiveFeed — Real-time activity feed
 */

import { timeAgo } from '../../lib/utils'

const mockActivity = [
  { id: '1', type: 'sale', description: 'New order: Starter Plan', timestamp: new Date(Date.now() - 300000), user_name: 'alice' },
  { id: '2', type: 'review', description: '5-star review on Pro Plan', timestamp: new Date(Date.now() - 600000), user_name: 'bob' },
  { id: '3', type: 'signup', description: 'New customer registered', timestamp: new Date(Date.now() - 900000), user_name: 'charlie' },
  { id: '4', type: 'sale', description: 'New order: 100 Stars pack', timestamp: new Date(Date.now() - 1200000), user_name: 'diana' },
]

const typeIcons: Record<string, string> = {
  sale: '💰',
  review: '⭐',
  signup: '👤',
  message: '💬',
  refund: '↩️',
}

export default function LiveFeed() {
  return (
    <div className="space-y-3">
      {mockActivity.map((item) => (
        <div key={item.id} className="flex items-center gap-3">
          <span className="text-lg">{typeIcons[item.type] || '📌'}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm truncate">{item.description}</p>
            <p className="text-xs text-tg-text-secondary">
              {item.user_name} · {timeAgo(item.timestamp)}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
