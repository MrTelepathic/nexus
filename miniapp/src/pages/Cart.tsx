/**
 * Cart Page — Shopping cart with checkout
 */

import { motion } from 'framer-motion'
import { formatCurrency } from '../lib/utils'

export default function Cart() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Cart</h1>

      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-tg-text-secondary">
          <span className="text-4xl mb-4 block">🛒</span>
          <p>Your cart is empty</p>
          <p className="text-sm mt-1">Browse the marketplace to add items</p>
        </div>
      </div>
    </motion.div>
  )
}
