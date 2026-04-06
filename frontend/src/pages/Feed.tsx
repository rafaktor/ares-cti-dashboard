import { useState, useCallback } from 'react'
import { api, type Pulse } from '../api/client'
import { usePolling } from '../hooks/usePolling'

function Dots() {
  return <div className="loading-dots"><span /><span /><span /></div>
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

export default function Feed() {
  const [pulses,  setPulses]  = useState<Pulse[]>([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)
  const [updated, setUpdated] = useState<Date | null>(null)
  const [limit,   setLimit]   = useState(20)

  const fetchFeed = useCallback(async () => {
    try {
      const data = await api.feed(limit)
      setPulses(data.feed)
      setUpdated(new Date())
      setError(null)
    } catch {
      setError('Failed to load threat feed — check AlienVault API key.')
    } finally {
      setLoading(false)
    }
  }, [limit])

  usePolling(fetchFeed, 5 * 60 * 1000)

  return (
    <div className="fade-in">
      {/* Header */}
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h1 className="page-title">Threat Feed</h1>
            <div className="page-subtitle">AlienVault OTX subscribed pulses · auto-refresh 5 min</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {updated && (
              <span className="timestamp">Updated {updated.toLocaleTimeString()}</span>
            )}
            <select
              className="type-select"
              value={limit}
              onChange={e => {
                setLimit(Number(e.target.value))
                setLoading(true)
              }}
              style={{ padding: '7px 12px', fontSize: '9px' }}
            >
              <option value={10}>10 pulses</option>
              <option value={20}>20 pulses</option>
              <option value={50}>50 pulses</option>
            </select>
          </div>
        </div>
      </div>

      {error && <div className="error-box" style={{ marginBottom: '14px' }}>{error}</div>}

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div className="card-title" style={{ margin: 0 }}>Active Pulses</div>
          {!loading && (
            <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'var(--green)', letterSpacing: '1px' }}>
              {pulses.length} results
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ padding: '48px', textAlign: 'center' }}><Dots /></div>
        ) : pulses.length ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Pulse Name</th>
                <th>Author</th>
                <th>Tags</th>
                <th>Indicators</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {pulses.map(p => (
                <tr key={p.id}>
                  <td className="td-name">{p.name}</td>
                  <td className="td-mono td-cyan">{p.author}</td>
                  <td>
                    <div className="tags">
                      {p.tags.slice(0, 4).map(t => <span key={t} className="tag">{t}</span>)}
                      {p.tags.length > 4 && (
                        <span className="tag muted">+{p.tags.length - 4}</span>
                      )}
                    </div>
                  </td>
                  <td className="td-mono td-bright">{p.indicators_count.toLocaleString()}</td>
                  <td className="td-mono" style={{ whiteSpace: 'nowrap', color: 'var(--text-secondary)' }}>
                    {fmtDate(p.created)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" stroke="var(--text-muted)" strokeWidth="1.4">
              <path d="M4 8h28M4 18h20M4 28h12" strokeLinecap="round" />
            </svg>
            <span className="empty-text">No pulses — verify AlienVault API key</span>
          </div>
        )}
      </div>
    </div>
  )
}
