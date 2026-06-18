/**
 * Orders Page — Order history and tracking
 */

import { motion } from 'framer-motion'

export default function Orders() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex-1 p-4 pb-20"
    >
      <h1 className="text-2xl font-bold mb-4">Orders</h1>
      <div className="text-center text-tg-text-secondary py-12">
        <span className="text-4xl mb-4 block">📦</span>
        <p>No orders yet</p>
      </div>
    </motion.div>
  )
}
