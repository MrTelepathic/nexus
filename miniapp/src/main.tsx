/**
 * Nexus Mini App — Entry Point
 *
 * Sets up:
 * - TWAProvider (Telegram Web App SDK context)
 * - ThemeProvider (live theme sync with Telegram)
 * - AuthProvider (initData validation)
 * - React Router
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { TWAProvider } from './providers/TWAProvider'
import { ThemeProvider } from './providers/ThemeProvider'
import { AuthProvider } from './providers/AuthProvider'
import { WebSocketProvider } from './providers/WebSocketProvider'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <TWAProvider>
      <ThemeProvider>
        <AuthProvider>
          <WebSocketProvider>
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </WebSocketProvider>
        </AuthProvider>
      </ThemeProvider>
    </TWAProvider>
  </React.StrictMode>,
)
