/**
 * ProductCard — Marketplace product card
 */

import { formatCurrency } from '../../lib/utils'

interface Props {
  product: {
    id: string
    name: string
    description: string
    price: number
    currency: string
    rating: number
    review_count: number
    image: string | null
  }
}

export default function ProductCard({ product }: Props) {
  return (
    <div className="bg-tg-section-bg rounded-2xl p-4 flex gap-4">
      <div className="w-16 h-16 bg-tg-bg rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
        📦
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="font-medium truncate">{product.name}</h3>
        <p className="text-sm text-tg-text-secondary truncate">{product.description}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="font-bold text-tg-accent">
            {formatCurrency(product.price, product.currency)}
          </span>
          <span className="text-xs text-tg-text-secondary">
            ⭐ {product.rating} ({product.review_count})
          </span>
        </div>
      </div>
    </div>
  )
}
