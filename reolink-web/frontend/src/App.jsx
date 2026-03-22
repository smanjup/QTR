import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.DEV ? '' : '/api'

async function api(path, options = {}) {
  const url = import.meta.env.DEV ? `http://localhost:8000${path}` : path
  const res = await fetch(url, { ...options })
  if (!res.ok) throw new Error(res.statusText)
  return res.json().catch(() => ({}))
}

function App() {
  const [recording, setRecording] = useState(false)
  const [detectionEnabled, setDetectionEnabled] = useState(true)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)

  const fetchStatus = async () => {
    try {
      const data = await api('/status')
      setStatus(data)
      setRecording(data.recording ?? false)
      setDetectionEnabled(data.detection_enabled ?? true)
      setError(null)
    } catch (e) {
      setError('Could not connect to backend. Is the server running on port 8000?')
    }
  }

  useEffect(() => {
    fetchStatus()
    const id = setInterval(fetchStatus, 2000)
    return () => clearInterval(id)
  }, [])

  const handleRecord = async () => {
    try {
      const data = await api('/record', { method: 'POST' })
      setRecording(data.recording ?? false)
      if (data.saved) setStatus((s) => ({ ...s, lastSaved: data.saved }))
    } catch (e) {
      setError('Failed to toggle recording')
    }
  }

  const handleDetection = async () => {
    try {
      const data = await api('/detection', { method: 'POST' })
      setDetectionEnabled(data.detection_enabled ?? true)
    } catch (e) {
      setError('Failed to toggle detection')
    }
  }

  const streamUrl = import.meta.env.DEV ? 'http://localhost:8000/stream' : '/stream'

  return (
    <div className="app">
      <header>
        <h1>Reolink Camera</h1>
        <p>Live stream with object detection</p>
      </header>

      {error && <div className="error">{error}</div>}

      <div className="video-container">
        <img
          src={streamUrl}
          alt="Live stream"
          className="stream"
          onError={() => setError('Stream unavailable')}
        />
      </div>

      <div className="controls">
        <button
          className={recording ? 'record active' : 'record'}
          onClick={handleRecord}
        >
          {recording ? 'Stop Recording' : 'Start Recording'}
        </button>
        <button
          className={detectionEnabled ? 'detect active' : 'detect'}
          onClick={handleDetection}
        >
          Detection: {detectionEnabled ? 'ON' : 'OFF'}
        </button>
      </div>

      <div className="status">
        <span>Recording: {recording ? 'Yes' : 'No'}</span>
        <span>Detection: {detectionEnabled ? 'ON' : 'OFF'}</span>
        {status?.lastSaved && <span>Last saved: {status.lastSaved}</span>}
      </div>
    </div>
  )
}

export default App
