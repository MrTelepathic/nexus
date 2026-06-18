/**
 * API Client — Axios wrapper with auth headers
 *
 * Automatically attaches initData to every request.
 * Handles token refresh and error responses.
 */

import WebApp from '@twa-dev/sdk'

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

async function request<T>(method: string, path: string, data?: unknown): Promise<T> {
  const init_data = WebApp.initData

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (init_data) {
    headers['X-Init-Data'] = init_data
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, data?: unknown) => request<T>('POST', path, data),
  put: <T>(path: string, data?: unknown) => request<T>('PUT', path, data),
  patch: <T>(path: string, data?: unknown) => request<T>('PATCH', path, data),
  delete: <T>(path: string) => request<T>('DELETE', path),
}
