import { useState, useEffect } from 'react'
import './App.css'

const API = 'http://localhost:8001'

async function api(path, opts = {}) {
  const r = await fetch(`${API}${path}`, opts)
  if (!r.ok) throw new Error(r.statusText)
  try {
    return await r.json()
  } catch {
    return {}
  }
}

function App() {
  const [recording, setRecording] = useState(false)
  const [detection, setDetection] = useState(true)
  const [vehicleCount, setVehicleCount] = useState(0)
  const [lineRatio, setLineRatio] = useState(0.6)
  const [error, setError] = useState(null)

  const poll = async () => {
    try {
      const s = await api('/status')
      setRecording(s.recording ?? false)
      setDetection(s.detection_enabled ?? true)
      setVehicleCount(s.vehicle_count ?? 0)
      setLineRatio(s.line_y_ratio ?? 0.6)
      setError(null)
    } catch {
      setError('Backend not reachable. Run: cd reolink-vehicle-line-web\\backend && python server.py')
    }
  }

  useEffect(() => {
    poll()
    const id = setInterval(poll, 1500)
    return () => clearInterval(id)
  }, [])

  const streamUrl = `${API}/stream`

  return (
    <div className="app">
      <header>
        <h1>Reolink · Vehicle line counter</h1>
        <p>
          Virtual line at <strong>{(lineRatio * 100).toFixed(0)}%</strong> from top · counts vehicles crossing downward
        </p>
      </header>
      {error && <div className="error">{error}</div>}
      <div className="video-wrap">
        <img src={streamUrl} alt="Live" className="stream" onError={() => setError('Stream unavailable')} />
      </div>
      <div className="controls">
        <button type="button" className={recording ? 'rec on' : 'rec'} onClick={() => api('/record', { method: 'POST' }).then(poll)}>
          {recording ? 'Stop recording' : 'Start recording'}
        </button>
        <button
          type="button"
          className={detection ? 'det on' : 'det'}
          onClick={() => api('/detection', { method: 'POST' }).then(poll)}
        >
          Detection: {detection ? 'ON' : 'OFF'}
        </button>
        <button type="button" className="reset" onClick={() => api('/reset-count', { method: 'POST' }).then(poll)}>
          Reset count
        </button>
      </div>
      <div className="meta">
        <span>Crossed line: <b>{vehicleCount}</b></span>
        <span>Recordings → <code>C:\webcam_recordings\</code></span>
      </div>
    </div>
  )
}

export default App
