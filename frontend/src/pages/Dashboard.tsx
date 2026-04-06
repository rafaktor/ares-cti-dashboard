import { useState, useCallback } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { api, type ThreatStats, type Pulse } from '../api/client'
import { usePolling } from '../hooks/usePolling'

function Dots() {
  return <div className="loading-dots"><span /><span /><span /></div>
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

const GREENS = [
  '#00e676', '#18e87c', '#30e982', '#48eb88', '#60ec8e',
  '#78ee94', '#90ef9a', '#a8f0a0', '#c0f2a6', '#d8f3ac',
]

function ChartTooltip({ active, payload, label }: {
  active?: boolean
  payload?: { value: number }[]
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'var(--bg-elevated)',
      border: '1px solid var(--border-bright)',
      padding: '8px 12px',
      fontFamily: 'var(--mono)',
      fontSize: '11px',
      borderRadius: '3px',
    }}>
      <div style={{ color: 'var(--text-muted)', fontSize: '9px', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '3px' }}>
        {label}
      </div>
      <div style={{ color: 'var(--green)' }}>{payload[0].value} pulses</div>
    </div>
  )
}

const SOURCES = ['AbuseIPDB', 'AlienVault OTX', 'VirusTotal'] as const
const CACHE_ROWS = [
  { label: 'Indicator TTL', value: '60 min' },
  { label: 'Feed TTL',      value: '5 min'  },
  { label: 'Stats TTL',     value: '10 min' },
] as const

export default function Dashboard() {
  const [stats, setStats]       = useState<ThreatStats | null>(null)
  const [feed, setFeed]         = useState<Pulse[]>([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState<string | null>(null)
  const [updated, setUpdated]   = useState<Date | null>(null)

  const fetchAll = useCallback(async () => {
    try {
      const [s, f] = await Promise.all([api.stats(), api.feed(10)])
      setStats(s)
      setFeed(f.feed)
      setUpdated(new Date())
      setError(null)
    } catch {
      setError('Failed to fetch threat data — check API keys and backend.')
    } finally {
      setLoading(false)
    }
  }, [])

  usePolling(fetchAll, 5 * 60 * 1000)

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Overview</h1>
            <div className="page-subtitle">Threat intelligence aggregation · live feed</div>
          </div>
          {updated && (
            <span className="timestamp">Updated {updated.toLocaleTimeString()}</span>
          )}
        </div>
      </div>

      {error && <div className="error-box" style={{ marginBottom: '14px' }}>{error}</div>}

      {/* Stat cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Pulses</div>
          {loading
            ? <Dots />
            : <div className="stat-value green">{stats?.total_pulses ?? '—'}</div>
          }
        </div>
        <div className="stat-card">
          <div className="stat-label">Top Threat Tag</div>
          {loading
            ? <Dots />
            : <div className="stat-text">{(stats?.top_tags[0]?.tag ?? '—').toUpperCase()}</div>
          }
        </div>
        <div className="stat-card">
          <div className="stat-label">Sources Active</div>
          <div className="stat-value">3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Feed Refresh</div>
          <div className="stat-value cyan" style={{ fontSize: '28px', marginTop: '4px' }}>5 MIN</div>
        </div>
      </div>

      {/* Charts row */}
      <div className="two-col" style={{ marginBottom: '14px' }}>
        {/* Tag bar chart */}
        <div className="card">
          <div className="card-title">Top Threat Tags</div>
          {loading ? (
            <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Dots />
            </div>
          ) : stats?.top_tags.length ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={stats.top_tags}
                layout="vertical"
                margin={{ left: 4, right: 16, top: 4, bottom: 4 }}
              >
                <XAxis
                  type="number"
                  tick={{ fill: 'var(--text-muted)', fontSize: 9, fontFamily: 'var(--mono)' }}
                  axisLine={false} tickLine={false}
                />
                <YAxis
                  type="category" dataKey="tag" width={88}
                  tick={{ fill: 'var(--text-secondary)', fontSize: 9, fontFamily: 'var(--mono)' }}
                  axisLine={false} tickLine={false}
                />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(0,230,118,0.04)' }} />
                <Bar dataKey="count" radius={[0, 2, 2, 0]}>
                  {stats.top_tags.map((_, i) => (
                    <Cell key={i} fill={GREENS[i % GREENS.length]} fillOpacity={1 - i * 0.06} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <span className="empty-text">No tag data</span>
            </div>
          )}
        </div>

        {/* Source health + cache info */}
        <div className="card">
          <div className="card-title">Source Health</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '11px', marginBottom: '24px' }}>
            {SOURCES.map(name => (
              <div key={name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '1px' }}>
                  {name}
                </span>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: 'var(--green)', boxShadow: '0 0 6px var(--green)',
                    display: 'inline-block',
                  }} />
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '9px', color: 'var(--green)', letterSpacing: '1px' }}>
                    ACTIVE
                  </span>
                </span>
              </div>
            ))}
          </div>

          <div className="card-title">Cache TTL</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {CACHE_ROWS.map(row => (
              <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '1px' }}>
                  {row.label}
                </span>
                <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'var(--cyan)' }}>
                  {row.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent pulses table */}
      <div className="card">
        <div className="card-title">Recent Threat Pulses</div>
        {loading ? (
          <div style={{ padding: '32px', textAlign: 'center' }}><Dots /></div>
        ) : feed.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Author</th>
                <th>Tags</th>
                <th>Indicators</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {feed.map(p => (
                <tr key={p.id}>
                  <td className="td-name">{p.name}</td>
                  <td className="td-mono td-cyan">{p.author}</td>
                  <td>
                    <div className="tags">
                      {p.tags.slice(0, 3).map(t => <span key={t} className="tag">{t}</span>)}
                      {p.tags.length > 3 && <span className="tag muted">+{p.tags.length - 3}</span>}
                    </div>
                  </td>
                  <td className="td-mono td-bright">{p.indicators_count.toLocaleString()}</td>
                  <td className="td-mono" style={{ whiteSpace: 'nowrap' }}>{fmtDate(p.created)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <span className="empty-text">No pulses — verify AlienVault API key</span>
          </div>
        )}
      </div>
    </div>
  )
}
