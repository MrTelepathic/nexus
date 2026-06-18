/**
 * Nexus Mini App — Root Component
 *
 * Handles:
 * - Page routing with transitions
 * - MainButton state management
 * - BackButton navigation
 * - App lifecycle (ready, closing confirmation)
 */

import { useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useMainButton } from './hooks/useMainButton'
import { useBackButton } from './hooks/useBackButton'
import { useHaptic } from './hooks/useHaptic'
import { useInitData } from './hooks/useInitData'

import Dashboard from './pages/Dashboard'
import Products from './pages/Products'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Orders from './pages/Orders'
import Wallet from './pages/Wallet'
import Profile from './pages/Profile'
import Leaderboard from './pages/Leaderboard'
import Referrals from './pages/Referrals'
import Settings from './pages/Settings'
import Onboarding from './pages/Onboarding'

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const { impactOccurred } = useHaptic()
  const initData = useInitData()
  const mainButton = useMainButton()
  const backButton = useBackButton()

  // Show back button on non-root pages
  const isRoot = location.pathname === '/'
  useEffect(() => {
    if (isRoot) {
      backButton.hide()
    } else {
      backButton.show()
      backButton.onClick(() => {
        impactOccurred('light')
        navigate(-1)
      })
    }
  }, [isRoot, location.pathname])

  // Welcome haptic on first load
  useEffect(() => {
    if (initData) {
      impactOccurred('medium')
    }
  }, [])

  // Configure MainButton based on route
  useEffect(() => {
    if (location.pathname === '/cart') {
      mainButton.setText('Checkout')
      mainButton.show()
      mainButton.onClick(() => {
        impactOccurred('heavy')
        navigate('/orders/new')
      })
    } else if (location.pathname.startsWith('/products/')) {
      mainButton.setText('Add to Cart')
      mainButton.show()
      mainButton.onClick(() => {
        impactOccurred('medium')
      })
    } else {
      mainButton.hide()
    }
  }, [location.pathname])

  if (!initData) {
    return <Onboarding />
  }

  return (
    <div className="flex-1 bg-tg-bg text-tg-text font-system">
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/orders/*" element={<Orders />} />
          <Route path="/wallet" element={<Wallet />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/referrals" element={<Referrals />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AnimatePresence>
    </div>
  )
}
