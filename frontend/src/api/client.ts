export interface ThreatStats {
  total_pulses: number
  top_tags: { tag: string; count: number }[]
}

export interface Pulse {
  id: string
  name: string
  tags: string[]
  indicators_count: number
  created: string
  author: string
}

export interface ThreatFeed {
  feed: Pulse[]
  count: number
}

export interface Indicator {
  ioc: string
  type: string
  score: number
  sources: string[]
  tags: string[]
  country: string | null
  last_seen: string | null
  raw: Record<string, Record<string, unknown>>
}

const BASE = '/api'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json() as Promise<T>
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: string }
    throw new Error(err.error ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  stats: () => get<ThreatStats>('/threats/stats'),
  feed:  (limit = 20) => get<ThreatFeed>(`/threats/feed?limit=${limit}`),
  lookup: (ioc: string, type?: string) =>
    post<Indicator>('/indicators/lookup', {
      ioc,
      ...(type && type !== 'auto' ? { type } : {}),
    }),
}
