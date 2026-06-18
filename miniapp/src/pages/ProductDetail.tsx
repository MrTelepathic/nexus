/**
 * ProductDetail Page — Single product view with add-to-cart
 */

import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useMainButton } from '../hooks/useMainButton'
import { useHaptic } from '../hooks/useHaptic'
import { formatCurrency } from '../lib/utils'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { impactOccurred } = useHaptic()

  // Mock product
  const product = {
    id,
    name: 'Starter Plan',
    description: 'AI assistant + CRM + 100 products. Perfect for small businesses getting started with Telegram commerce.',
    price: 100,
    currency: 'XTR',
    rating: 4.8,
    review_count: 124,
    images: [],
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="flex-1 p-4 pb-20"
    >
      {/* Product Image Placeholder */}
      <div className="w-full h-48 bg-tg-section-bg rounded-2xl mb-4 flex items-center justify-center text-4xl">
        📦
      </div>

      <h1 className="text-xl font-bold mb-2">{product.name}</h1>

      <div className="flex items-center gap-2 mb-4">
        <span className="text-yellow-500">{'⭐'.repeat(Math.round(product.rating))}</span>
        <span className="text-sm text-tg-text-secondary">
          {product.rating} ({product.review_count} reviews)
        </span>
      </div>

      <p className="text-tg-text-secondary mb-6">{product.description}</p>

      <div className="text-2xl font-bold mb-4">
        {formatCurrency(product.price, product.currency)}
      </div>
    </motion.div>
  )
}
