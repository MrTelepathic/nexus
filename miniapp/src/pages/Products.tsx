/**
 * Products Page — Marketplace listing with search and filters
 */

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useHaptic } from '../hooks/useHaptic'
import ProductCard from '../components/product/ProductCard'

const mockProducts = [
  { id: '1', name: 'Starter Plan', description: 'AI assistant + CRM', price: 100, currency: 'XTR', rating: 4.8, review_count: 124, image: null },
  { id: '2', name: 'Pro Plan', description: 'Full platform access', price: 500, currency: 'XTR', rating: 4.9, review_count: 89, image: null },
  { id: '3', name: 'Custom Sticker Pack', description: '10 custom stickers', price: 50, currency: 'XTR', rating: 4.7, review_count: 56, image: null },
]

export default function Products() {
  const navigate = useNavigate()
  const { impactOccurred } = useHaptic()
  const [search, setSearch] = useState('')

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Marketplace</h1>

      {/* Search */}
      <input
        type="text"
        placeholder="Search products..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full p-3 rounded-xl bg-tg-section-bg text-tg-text placeholder:text-tg-text-secondary mb-4"
      />

      {/* Products Grid */}
      <div className="space-y-3">
        {mockProducts.map((product, i) => (
          <motion.div
            key={product.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            onClick={() => {
              impactOccurred('light')
              navigate(`/products/${product.id}`)
            }}
          >
            <ProductCard product={product} />
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
