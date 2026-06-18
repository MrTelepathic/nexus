/**
 * Utility functions
 */

import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toString()
}

export function formatCurrency(amount: number, currency: string = 'XTR'): string {
  const symbols: Record<string, string> = {
    XTR: '\u2b50',
    TON: '\uD83D\uDC8E',
    USD: '$',
  }
  const symbol = symbols[currency] || currency
  if (currency === 'XTR') return `${Math.round(amount)} ${symbol}`
  return `${symbol}${amount.toFixed(2)}`
}

export function timeAgo(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}
