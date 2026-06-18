/**
 * Onboarding Page — Shown when initData is not available
 * (e.g., when opened outside Telegram)
 */

import WebApp from '@twa-dev/sdk'

export default function Onboarding() {
  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center">
        <span className="text-6xl mb-6 block">🌐</span>
        <h1 className="text-2xl font-bold mb-2">Welcome to Nexus</h1>
        <p className="text-tg-text-secondary mb-6">
          Open this app from Telegram to get started
        </p>
        <a
          href="https://t.me/nexusbot"
          className="inline-block px-6 py-3 bg-tg-button text-tg-button-text rounded-xl font-medium"
        >
          Open in Telegram
        </a>
      </div>
    </div>
  )
}
