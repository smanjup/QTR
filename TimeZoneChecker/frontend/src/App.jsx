import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

const API = '/api'

function useDebounced(value, delay) {
  const [d, setD] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setD(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return d
}

async function searchCities(q) {
  const r = await fetch(`${API}/cities/search?q=${encodeURIComponent(q)}`)
  if (!r.ok) throw new Error('Search failed')
  return r.json()
}

async function convert(body) {
  const r = await fetch(`${API}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    const d = err.detail
    const msg =
      typeof d === 'string'
        ? d
        : Array.isArray(d)
          ? d.map((x) => x.msg || x).join('; ')
          : r.statusText
    throw new Error(msg || 'Convert failed')
  }
  return r.json()
}

function todayISODate() {
  const n = new Date()
  const y = n.getFullYear()
  const m = String(n.getMonth() + 1).padStart(2, '0')
  const d = String(n.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/** Keep a single canonical form for controlled time input (HH:MM) and localDatetime. */
function normalizeTimeHHMM(input) {
  if (!input || typeof input !== 'string') return '12:00'
  const parts = input.trim().split(':')
  const h = Number.parseInt(parts[0], 10)
  const m = Number.parseInt(parts[1] ?? '0', 10)
  if (Number.isNaN(h) || Number.isNaN(m)) return '12:00'
  const hh = String(Math.min(23, Math.max(0, h))).padStart(2, '0')
  const mm = String(Math.min(59, Math.max(0, m))).padStart(2, '0')
  return `${hh}:${mm}`
}

export default function App() {
  const [step, setStep] = useState(1)

  const [refQuery, setRefQuery] = useState('')
  const debouncedRef = useDebounced(refQuery, 320)
  const [refHits, setRefHits] = useState([])
  const [refCity, setRefCity] = useState(null)
  const [refDate, setRefDate] = useState(todayISODate())
  const [refTime, setRefTime] = useState('12:00')

  const [targetQuery, setTargetQuery] = useState('')
  const debouncedTarget = useDebounced(targetQuery, 320)
  const [targetHits, setTargetHits] = useState([])
  const [targets, setTargets] = useState([])

  const [loadingRefSearch, setLoadingRefSearch] = useState(false)
  const [loadingTargetSearch, setLoadingTargetSearch] = useState(false)
  const [loadingConvert, setLoadingConvert] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    if (debouncedRef.length < 2) {
      setRefHits([])
      setLoadingRefSearch(false)
      return
    }
    let cancelled = false
    setLoadingRefSearch(true)
    searchCities(debouncedRef)
      .then((data) => {
        if (!cancelled) setRefHits(data.results || [])
      })
      .catch(() => {
        if (!cancelled) setRefHits([])
      })
      .finally(() => {
        if (!cancelled) setLoadingRefSearch(false)
      })
    return () => {
      cancelled = true
    }
  }, [debouncedRef])

  useEffect(() => {
    if (debouncedTarget.length < 2) {
      setTargetHits([])
      setLoadingTargetSearch(false)
      return
    }
    let cancelled = false
    setLoadingTargetSearch(true)
    searchCities(debouncedTarget)
      .then((data) => {
        if (!cancelled) setTargetHits(data.results || [])
      })
      .catch(() => {
        if (!cancelled) setTargetHits([])
      })
      .finally(() => {
        if (!cancelled) setLoadingTargetSearch(false)
      })
    return () => {
      cancelled = true
    }
  }, [debouncedTarget])

  const localDatetime = useMemo(() => {
    const hm = normalizeTimeHHMM(refTime)
    return `${refDate}T${hm}:00`
  }, [refDate, refTime])

  const canGoStep2 = refCity && refDate && refTime
  const canConvert = canGoStep2 && targets.length > 0

  const pickRef = useCallback((hit) => {
    setRefCity(hit)
    setRefQuery(hit.label)
    setRefHits([])
  }, [])

  const addTarget = useCallback(
    (hit) => {
      setTargets((prev) => {
        if (prev.some((p) => p.timezone === hit.timezone)) return prev
        return [...prev, { label: hit.label, timezone: hit.timezone }]
      })
      setTargetQuery('')
      setTargetHits([])
    },
    [],
  )

  const removeTarget = useCallback((tz) => {
    setTargets((prev) => prev.filter((p) => p.timezone !== tz))
  }, [])

  const runConvert = useCallback(async () => {
    setError('')
    setLoadingConvert(true)
    try {
      const toTzs = targets.map((t) => t.timezone)
      const data = await convert({
        from_timezone: refCity.timezone,
        local_datetime: localDatetime,
        to_timezones: toTzs,
      })
      setResult(data)
      setStep(3)
    } catch (e) {
      setError(e.message || String(e))
    } finally {
      setLoadingConvert(false)
    }
  }, [localDatetime, refCity, targets])

  return (
    <div className="shell">
      <header className="hero">
        <p className="eyebrow">TimeZoneChecker</p>
        <h1 className="title">What time is the time there</h1>
        <p className="lede">
          Pick a city and a local time, add other places, and see those moments on their clocks.
        </p>
        <nav className="steps" aria-label="Progress">
          <span className={step === 1 ? 'on' : ''}>1 · When &amp; where</span>
          <span className="sep">→</span>
          <span className={step === 2 ? 'on' : ''}>2 · More cities</span>
          <span className="sep">→</span>
          <span className={step === 3 ? 'on' : ''}>3 · Results</span>
        </nav>
      </header>

      {error ? (
        <div className="banner error" role="alert">
          {error}
        </div>
      ) : null}

      {step === 1 && (
        <section className="card">
          <h2>Step 1 — Reference city &amp; time</h2>
          <p className="hint">Time is interpreted as local wall time in the city you choose (handles DST).</p>

          <label className="field">
            <span>City</span>
            <input
              type="search"
              autoComplete="off"
              placeholder="e.g. Norwalk, London, Tokyo"
              value={refQuery}
              onChange={(e) => {
                setRefQuery(e.target.value)
                setRefCity(null)
              }}
            />
            {loadingRefSearch && refQuery.length >= 2 ? (
              <span className="mini">Searching…</span>
            ) : null}
            {refHits.length > 0 && (
              <ul className="hits">
                {refHits.map((h) => (
                  <li key={h.id ?? `${h.timezone}-${h.label}`}>
                    <button type="button" onClick={() => pickRef(h)}>
                      {h.label}
                      <span className="tz">{h.timezone}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </label>

          {refCity ? (
            <p className="picked">
              Selected: <strong>{refCity.label}</strong>{' '}
              <span className="tz">({refCity.timezone})</span>
            </p>
          ) : null}

          <div className="row">
            <label className="field">
              <span>Date</span>
              <input type="date" value={refDate} onChange={(e) => setRefDate(e.target.value)} />
            </label>
            <label className="field">
              <span>Time</span>
              <input
                type="time"
                step={60}
                value={refTime}
                onChange={(e) => setRefTime(normalizeTimeHHMM(e.target.value))}
              />
            </label>
          </div>

          <div className="actions">
            <button type="button" className="primary" disabled={!canGoStep2} onClick={() => setStep(2)}>
              Next
            </button>
          </div>
        </section>
      )}

      {step === 2 && (
        <section className="card">
          <h2>Step 2 — Other cities</h2>
          <p className="hint">Add one or more places to compare. Duplicates by timezone are skipped.</p>

          <label className="field">
            <span>Add city</span>
            <input
              type="search"
              autoComplete="off"
              placeholder="Search city"
              value={targetQuery}
              onChange={(e) => setTargetQuery(e.target.value)}
            />
            {loadingTargetSearch && targetQuery.length >= 2 ? (
              <span className="mini">Searching…</span>
            ) : null}
            {targetHits.length > 0 && (
              <ul className="hits">
                {targetHits.map((h) => (
                  <li key={(h.id ?? h.label) + String(h.timezone)}>
                    <button type="button" onClick={() => addTarget(h)}>
                      {h.label}
                      <span className="tz">{h.timezone}</span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </label>

          <div className="chips">
            {targets.length === 0 ? (
              <p className="muted">No cities yet.</p>
            ) : (
              targets.map((t) => (
                <button key={t.timezone} type="button" className="chip" onClick={() => removeTarget(t.timezone)}>
                  {t.label}
                  <span className="x" aria-hidden>
                    ×
                  </span>
                </button>
              ))
            )}
          </div>

          <div className="actions">
            <button type="button" className="ghost" onClick={() => setStep(1)}>
              Back
            </button>
            <button
              type="button"
              className="primary"
              disabled={!canConvert || loadingConvert}
              onClick={runConvert}
            >
              {loadingConvert ? 'Converting…' : 'Convert'}
            </button>
          </div>
        </section>
      )}

      {step === 3 && result && (
        <section className="card">
          <h2>Step 3 — Local times</h2>
          <p className="summary">
            When it is{' '}
            <strong>
              {refCity.label} · {localDatetime.replace('T', ' ')}
            </strong>
            , elsewhere it is:
          </p>

          <table className="grid">
            <thead>
              <tr>
                <th>Place (IANA zone)</th>
                <th>Local date &amp; time</th>
                <th>Offset</th>
              </tr>
            </thead>
            <tbody>
              <tr className="ref-row">
                <td>
                  {refCity.label}
                  <div className="tz">{refCity.timezone}</div>
                </td>
                <td>{result.reference_local.split('(')[0].trim()}</td>
                <td>—</td>
              </tr>
              {result.results.map((row) => (
                <tr key={row.timezone}>
                  <td>
                    {targets.find((t) => t.timezone === row.timezone)?.label || row.timezone}
                    <div className="tz">{row.timezone}</div>
                  </td>
                  <td>{row.local_datetime}</td>
                  <td>{row.offset_label}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="utc">
            UTC instant: <code>{result.utc_iso}</code>
          </p>

          <div className="actions">
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setStep(2)
                setResult(null)
              }}
            >
              Edit cities
            </button>
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setStep(1)
                setResult(null)
                setTargets([])
              }}
            >
              Start over
            </button>
          </div>
        </section>
      )}
    </div>
  )
}
