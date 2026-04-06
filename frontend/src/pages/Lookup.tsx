import { useState } from 'react'
import { api, type Indicator } from '../api/client'

/* ── Score gauge (SVG arc) ─────────────────────────────────── */
function ScoreGauge({ score }: { score: number }) {
  const r      = 52
  const circ   = 2 * Math.PI * r
  const pct    = Math.max(0, Math.min(100, score))
  const offset = circ - (pct / 100) * circ
  const color  = score >= 70 ? 'var(--red)' : score >= 30 ? 'var(--amber)' : 'var(--green)'
  const glow   = score >= 70 ? 'rgba(244,67,54,0.5)'  : score >= 30 ? 'rgba(255,193,7,0.5)' : 'rgba(0,230,118,0.5)'

  return (
    <svg width="140" height="140" viewBox="0 0 140 140">
      {/* Track */}
      <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(0,230,118,0.07)" strokeWidth="9" />
      {/* Fill */}
      <circle
        cx="70" cy="70" r={r}
        fill="none"
        stroke={color}
        strokeWidth="9"
        strokeDasharray={circ}
        strokeDashoffset={offset}
        strokeLinecap="round"
        transform="rotate(-90 70 70)"
        style={{
          transition: 'stroke-dashoffset 1.1s cubic-bezier(0.4,0,0.2,1), stroke 0.3s ease',
          filter: `drop-shadow(0 0 7px ${glow})`,
        }}
      />
      <text
        x="70" y="63"
        textAnchor="middle"
        fill={color}
        style={{ fontFamily: 'var(--display)', fontSize: '34px', letterSpacing: '2px' }}
      >
        {score}
      </text>
      <text
        x="70" y="80"
        textAnchor="middle"
        fill="var(--text-muted)"
        style={{ fontFamily: 'var(--mono)', fontSize: '8.5px', letterSpacing: '2px' }}
      >
        RISK SCORE
      </text>
    </svg>
  )
}

function Dots() {
  return <div className="loading-dots"><span /><span /><span /></div>
}

function riskLevel(score: number) {
  if (score >= 70) return { label: 'HIGH THREAT',   cls: 'red'   }
  if (score >= 30) return { label: 'MEDIUM THREAT',  cls: 'amber' }
  return               { label: 'LOW THREAT',    cls: 'green' }
}

/* ── Page ──────────────────────────────────────────────────── */
export default function Lookup() {
  const [ioc,     setIoc]     = useState('')
  const [type,    setType]    = useState('auto')
  const [result,  setResult]  = useState<Indicator | null>(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState<string | null>(null)
  const [showRaw, setShowRaw] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = ioc.trim()
    if (!trimmed) return
    setLoading(true)
    setError(null)
    setResult(null)
    setShowRaw(false)
    try {
      setResult(await api.lookup(trimmed, type))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lookup failed')
    } finally {
      setLoading(false)
    }
  }

  const risk = result ? riskLevel(result.score) : null

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">IOC Lookup</h1>
        <div className="page-subtitle">Scan IP addresses · domains · file hashes</div>
      </div>

      {/* Search form */}
      <form onSubmit={handleSubmit} className="lookup-form">
        <div className="input-wrap">
          <span className="input-prompt">›</span>
          <input
            className="ioc-input"
            type="text"
            value={ioc}
            onChange={e => setIoc(e.target.value)}
            placeholder="e.g.  8.8.8.8  ·  evil.com  ·  d41d8cd9..."
            spellCheck={false}
            autoComplete="off"
          />
        </div>
        <select
          className="type-select"
          value={type}
          onChange={e => setType(e.target.value)}
        >
          <option value="auto">Auto Detect</option>
          <option value="ip">IP Address</option>
          <option value="domain">Domain</option>
          <option value="hash">File Hash</option>
        </select>
        <button type="submit" className="btn-scan" disabled={loading || !ioc.trim()}>
          {loading ? 'Scanning' : 'Scan'}
        </button>
      </form>

      {error && <div className="error-box" style={{ marginBottom: '14px' }}>{error}</div>}

      {/* Loading */}
      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '52px 20px' }}>
          <div style={{
            fontFamily: 'var(--mono)',
            fontSize: '10px',
            letterSpacing: '3px',
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            marginBottom: '18px',
          }}>
            Querying threat feeds
          </div>
          <Dots />
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="fade-in">
          {/* Risk banner */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <span className={`tag ${risk!.cls}`} style={{ padding: '4px 10px', fontSize: '10px', letterSpacing: '2px' }}>
              {risk!.label}
            </span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: '13px', color: 'var(--text)' }}>
              {result.ioc}
            </span>
          </div>

          {/* Score + metadata */}
          <div className="card" style={{ marginBottom: '10px' }}>
            <div className="result-top">
              <div className="gauge-wrap">
                <ScoreGauge score={result.score} />
              </div>
              <div>
                <div className="section-label">Metadata</div>
                <div className="meta-grid" style={{ marginBottom: '16px' }}>
                  <div className="meta-item">
                    <span className="meta-label">Type</span>
                    <span className="meta-value">{result.type.toUpperCase()}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Country</span>
                    <span className="meta-value">{result.country ?? '—'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Last Seen</span>
                    <span className="meta-value" style={{ fontSize: '12px' }}>
                      {result.last_seen
                        ? new Date(result.last_seen).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                        : '—'}
                    </span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Sources</span>
                    <span className="meta-value" style={{ fontSize: '12px' }}>{result.sources.join(' · ')}</span>
                  </div>
                </div>

                {result.tags.length > 0 && (
                  <>
                    <div className="section-label">Tags</div>
                    <div className="tags">
                      {result.tags.map(t => (
                        <span key={t} className={`tag ${risk!.cls}`}>{t}</span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Source breakdown */}
          <div className="card" style={{ marginBottom: '10px' }}>
            <div className="card-title">Source Breakdown</div>
            <div className="sources-grid">
              {result.sources.map(src => (
                <div key={src} className="source-card">
                  <span className="source-name">{src}</span>
                  <span style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: 'var(--green)', boxShadow: '0 0 5px var(--green)',
                    display: 'inline-block', flexShrink: 0,
                  }} />
                </div>
              ))}
            </div>
          </div>

          {/* Raw JSON */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div className="card-title" style={{ margin: 0 }}>Raw Response</div>
              <button className="btn-raw" onClick={() => setShowRaw(v => !v)}>
                {showRaw ? 'Hide' : 'Show'} Raw
              </button>
            </div>
            {showRaw && (
              <pre className="raw-json">{JSON.stringify(result.raw, null, 2)}</pre>
            )}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !result && !error && (
        <div className="empty-state">
          <svg width="38" height="38" viewBox="0 0 38 38" fill="none" stroke="var(--text-muted)" strokeWidth="1.4">
            <circle cx="17" cy="17" r="12" />
            <path d="M26 26l9 9" strokeLinecap="round" />
          </svg>
          <span className="empty-text">Enter an IOC to begin threat scan</span>
        </div>
      )}
    </div>
  )
}
