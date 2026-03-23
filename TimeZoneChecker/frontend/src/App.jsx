import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { isValid as isValidDate } from 'date-fns'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import { MAJOR_CITIES } from './data/majorCities.js'
import './App.css'

const API = '/api'

const REF_CITY_MAX = 25
const REF_CITY_POPULAR = 20

function formatApiDetail(detail) {
  if (detail == null) return ''
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((x) => (typeof x === 'object' && x !== null ? x.msg || x.message || JSON.stringify(x) : String(x)))
      .filter(Boolean)
      .join('; ')
  }
  if (typeof detail === 'object') return JSON.stringify(detail)
  return String(detail)
}

async function convert(body) {
  const r = await fetch(`${API}/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'omit',
  })
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    const msg = formatApiDetail(err.detail) || r.statusText || 'Request failed'
    throw new Error(msg)
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

/** Calendar uses local component values as naive wall time for the reference city (not browser TZ). */
function naivePartsToDate(refDateStr, refTimeStr) {
  const parts = refDateStr.split('-').map(Number)
  const [y, mo, d] = parts
  if (parts.length < 3 || !y || !mo || !d) return new Date()
  const hm = normalizeTimeHHMM(refTimeStr)
  const [hh, mm] = hm.split(':').map(Number)
  return new Date(y, mo - 1, d, hh, mm, 0, 0)
}

function dateToNaiveParts(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return { refDate: `${y}-${m}-${day}`, refTime: `${hh}:${mm}` }
}

export default function App() {
  const resultsRef = useRef(null)
  const refBlurTimerRef = useRef(null)
  const targetBlurTimerRef = useRef(null)

  const [refQuery, setRefQuery] = useState('')
  const [refInputFocused, setRefInputFocused] = useState(false)
  const [refCity, setRefCity] = useState(null)
  const [refDate, setRefDate] = useState(todayISODate())
  const [refTime, setRefTime] = useState('12:00')

  const [targetQuery, setTargetQuery] = useState('')
  const [targetInputFocused, setTargetInputFocused] = useState(false)
  const [targets, setTargets] = useState([])

  const [loadingConvert, setLoadingConvert] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const localDatetime = useMemo(() => {
    const hm = normalizeTimeHHMM(refTime)
    return `${refDate}T${hm}:00`
  }, [refDate, refTime])

  const majorCitiesSorted = useMemo(
    () => [...MAJOR_CITIES].sort((a, b) => a.label.localeCompare(b.label)),
    [],
  )

  const refCitySuggestions = useMemo(() => {
    const q = refQuery.trim().toLowerCase()
    if (q.length < 1) return majorCitiesSorted.slice(0, REF_CITY_POPULAR)
    return majorCitiesSorted.filter((c) => c.label.toLowerCase().includes(q)).slice(0, REF_CITY_MAX)
  }, [refQuery, majorCitiesSorted])

  const targetCitySuggestions = useMemo(() => {
    const q = targetQuery.trim().toLowerCase()
    if (q.length < 1) return majorCitiesSorted.slice(0, REF_CITY_POPULAR)
    return majorCitiesSorted.filter((c) => c.label.toLowerCase().includes(q)).slice(0, REF_CITY_MAX)
  }, [targetQuery, majorCitiesSorted])

  const refDateTimeValue = useMemo(() => {
    const d = naivePartsToDate(refDate, refTime)
    if (!isValidDate(d)) return naivePartsToDate(todayISODate(), '12:00')
    return d
  }, [refDate, refTime])

  const refTz = refCity?.timezone?.trim?.() ?? ''
  const refReady = refCity && refTz.length > 0 && refDate && refTime

  const validTargets = useMemo(
    () => targets.filter((t) => typeof t.timezone === 'string' && t.timezone.trim().length > 0),
    [targets],
  )
  const canConvert = refReady && validTargets.length > 0

  const convertBlockedReason = useMemo(() => {
    if (!refCity) {
      return 'Pick a reference city in Step 1: click the field, type to filter major cities, then choose one from the list (typing alone is not enough).'
    }
    if (!refTz) {
      return 'Reference city is missing a timezone. Pick the city again from the list.'
    }
    if (!refDate || !refTime) return 'Set date and time in Step 1.'
    if (validTargets.length === 0) {
      return 'Add at least one city in Step 2: click the field, type to filter major cities, then pick one from the list.'
    }
    return null
  }, [refCity, refTz, refDate, refTime, validTargets.length])

  const pickRef = useCallback((hit) => {
    const tz = typeof hit.timezone === 'string' ? hit.timezone.trim() : ''
    if (!tz) return
    setRefCity({ label: hit.label, timezone: tz })
    setRefQuery(hit.label)
    setRefInputFocused(false)
  }, [])

  const onRefInputFocus = useCallback(() => {
    if (refBlurTimerRef.current) {
      window.clearTimeout(refBlurTimerRef.current)
      refBlurTimerRef.current = null
    }
    setRefInputFocused(true)
  }, [])

  const onRefInputBlur = useCallback(() => {
    refBlurTimerRef.current = window.setTimeout(() => setRefInputFocused(false), 200)
  }, [])

  const showRefDropdown =
    refInputFocused &&
    (refCitySuggestions.length > 0 || refQuery.trim().length >= 1)
  const refNoMatches = refInputFocused && refQuery.trim().length >= 1 && refCitySuggestions.length === 0

  const onTargetInputFocus = useCallback(() => {
    if (targetBlurTimerRef.current) {
      window.clearTimeout(targetBlurTimerRef.current)
      targetBlurTimerRef.current = null
    }
    setTargetInputFocused(true)
  }, [])

  const onTargetInputBlur = useCallback(() => {
    targetBlurTimerRef.current = window.setTimeout(() => setTargetInputFocused(false), 200)
  }, [])

  const showTargetDropdown =
    targetInputFocused &&
    (targetCitySuggestions.length > 0 || targetQuery.trim().length >= 1)
  const targetNoMatches =
    targetInputFocused && targetQuery.trim().length >= 1 && targetCitySuggestions.length === 0

  const addTarget = useCallback((hit) => {
    const tz = typeof hit.timezone === 'string' ? hit.timezone.trim() : ''
    if (!tz) return
    setTargets((prev) => {
      if (prev.some((p) => p.timezone === tz)) return prev
      return [...prev, { label: hit.label, timezone: tz }]
    })
    setTargetQuery('')
    setTargetInputFocused(false)
  }, [])

  const removeTarget = useCallback((tz) => {
    setTargets((prev) => prev.filter((p) => p.timezone !== tz))
  }, [])

  const runConvert = useCallback(async () => {
    setError('')
    setLoadingConvert(true)
    try {
      const fromTz = refCity?.timezone?.trim?.() ?? ''
      const toTzs = validTargets.map((t) => t.timezone.trim())
      if (!fromTz) {
        setError('Reference city has no timezone. Choose a city again from the list.')
        return
      }
      if (toTzs.length === 0) {
        setError('Add at least one comparison city with a valid timezone.')
        return
      }
      const data = await convert({
        from_timezone: fromTz,
        local_datetime: localDatetime,
        to_timezones: toTzs,
      })
      setResult(data)
    } catch (e) {
      const m = e instanceof Error ? e.message : String(e)
      setError(
        /failed to fetch|networkerror/i.test(m)
          ? 'Cannot reach the API. Start the backend (e.g. uvicorn on port 8001) and use the Vite dev server so /api is proxied.'
          : m,
      )
    } finally {
      setLoadingConvert(false)
    }
  }, [localDatetime, refCity, validTargets])

  useEffect(() => {
    if (!result) return
    requestAnimationFrame(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }, [result])

  return (
    <div className="shell">
      <header className="hero">
        <p className="eyebrow">TimeZoneChecker</p>
        <h1 className="title">What is the time there</h1>
        <p className="lede">
          Pick a city and a local time, add other places, and see those moments on their clocks.
        </p>
      </header>

      {error ? (
        <div className="banner error" role="alert">
          {error}
        </div>
      ) : null}

      <section className="card" id="section-reference">
        <h2>Step 1 — Reference city &amp; time</h2>
          <p className="hint">
            Choose a major city from the list. Date and time are interpreted as local wall time in that city’s timezone
            (handles DST).
          </p>

          <label className="field field-city">
            <span id="label-ref-city">City</span>
            <input
              type="text"
              autoComplete="off"
              spellCheck={false}
              placeholder="Type to filter cities, then pick one"
              aria-labelledby="label-ref-city"
              aria-autocomplete="list"
              aria-expanded={showRefDropdown}
              value={refQuery}
              onFocus={onRefInputFocus}
              onBlur={onRefInputBlur}
              onChange={(e) => {
                const v = e.target.value
                setRefQuery(v)
                if (refCity && v.trim() !== refCity.label.trim()) {
                  setRefCity(null)
                }
              }}
            />
            {showRefDropdown && refCitySuggestions.length > 0 ? (
              <ul className="hits" role="listbox" aria-label="Major cities">
                {refCitySuggestions.map((h) => (
                  <li key={h.id}>
                    <button
                      type="button"
                      role="option"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => pickRef(h)}
                    >
                      {h.label}
                      <span className="tz">{h.timezone}</span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
            {refNoMatches ? (
              <p className="mini hits-empty" role="status">
                No matches. Try another spelling or open the list with an empty search to browse popular cities.
              </p>
            ) : null}
          </label>

          {refCity ? (
            <p className="picked">
              Selected: <strong>{refCity.label}</strong>{' '}
              <span className="tz">({refCity.timezone})</span>
            </p>
          ) : null}

          <div className="field">
            <span id="label-ref-datetime">Date &amp; time</span>
            <DatePicker
              id="ref-datetime"
              selected={refDateTimeValue}
              onChange={(d) => {
                if (!d || !isValidDate(d)) return
                const p = dateToNaiveParts(d)
                setRefDate(p.refDate)
                setRefTime(normalizeTimeHHMM(p.refTime))
              }}
              showTimeSelect
              timeIntervals={15}
              dateFormat="yyyy-MM-dd HH:mm"
              timeFormat="HH:mm"
              timeCaption="Time"
              placeholderText="Pick date & time"
              ariaLabelledBy="label-ref-datetime"
              popperClassName="tz-datepicker-popper"
              calendarClassName="tz-datepicker-calendar"
              wrapperClassName="datetime-picker-wrap"
              className="datetime-picker-input"
              showIcon
              calendarIconClassName="tz-datepicker-trigger-icon"
              toggleCalendarOnIconClick
              strictParsing={false}
              autoComplete="off"
            />
            <p className="mini datetime-picker-hint">
              Use the calendar icon or click the field for a popup; the value is editable as text.
            </p>
          </div>
      </section>

      <section className="card" id="section-targets">
        <h2>Step 2 — Other cities</h2>
          <p className="hint">
            Add one or more major cities to compare. Duplicates by timezone are skipped.
          </p>

          <label className="field field-city">
            <span id="label-target-city">Add city</span>
            <input
              type="text"
              autoComplete="off"
              spellCheck={false}
              placeholder="Type to filter cities, then pick one"
              aria-labelledby="label-target-city"
              aria-autocomplete="list"
              aria-expanded={showTargetDropdown}
              value={targetQuery}
              onFocus={onTargetInputFocus}
              onBlur={onTargetInputBlur}
              onChange={(e) => setTargetQuery(e.target.value)}
            />
            {showTargetDropdown && targetCitySuggestions.length > 0 ? (
              <ul className="hits" role="listbox" aria-label="Major cities to compare">
                {targetCitySuggestions.map((h) => (
                  <li key={h.id}>
                    <button
                      type="button"
                      role="option"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => addTarget(h)}
                    >
                      {h.label}
                      <span className="tz">{h.timezone}</span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
            {targetNoMatches ? (
              <p className="mini hits-empty" role="status">
                No matches. Try another spelling or open the list with an empty search to browse popular cities.
              </p>
            ) : null}
          </label>

          <div className="chips">
            {validTargets.length === 0 ? (
              <p className="muted">No cities yet.</p>
            ) : (
              validTargets.map((t) => (
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
            <button
              type="button"
              className="primary"
              disabled={!canConvert || loadingConvert}
              onClick={runConvert}
            >
              {loadingConvert ? 'Converting…' : 'Convert'}
            </button>
          </div>
          {convertBlockedReason ? (
            <p className="convert-hint muted" role="status">
              {convertBlockedReason}
            </p>
          ) : null}
      </section>

      <section ref={resultsRef} className="card" id="section-results" tabIndex={-1}>
        <h2>Step 3 — Local times</h2>

        {result && refCity ? (
          <>
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
                      {validTargets.find((t) => t.timezone === row.timezone)?.label || row.timezone}
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
              <button type="button" className="ghost" onClick={() => setResult(null)}>
                Edit cities
              </button>
              <button
                type="button"
                className="ghost"
                onClick={() => {
                  setResult(null)
                  setTargets([])
                }}
              >
                Start over
              </button>
            </div>
          </>
        ) : (
          <p className="muted results-placeholder">
            Results appear here after you choose a reference city and time, add at least one other city in step 2, and
            click <strong>Convert</strong>.
          </p>
        )}
      </section>
    </div>
  )
}
