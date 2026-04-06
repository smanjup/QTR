import { useCallback, useMemo, useState } from 'react'

/** Defaults match the original turtle script: tree(100, 30), backward(200), length < 9 stops. */
const DEFAULT = {
  width: 800,
  height: 600,
  length: 100,
  angle: 30,
  backward: 200,
  minLength: 9,
}

function buildTreewithloveUrl(params: {
  width: number
  height: number
  length: number
  angle: number
  backward: number
  minLength: number
}) {
  const q = new URLSearchParams({
    width: String(Math.round(params.width)),
    height: String(Math.round(params.height)),
    length: String(params.length),
    angle: String(params.angle),
    backward: String(params.backward),
    min_length: String(params.minLength),
  })
  return `/api/treewithlove.png?${q.toString()}`
}

export default function TreewithlovePage() {
  const [width, setWidth] = useState(DEFAULT.width)
  const [height, setHeight] = useState(DEFAULT.height)
  const [length, setLength] = useState(DEFAULT.length)
  const [angle, setAngle] = useState(DEFAULT.angle)
  const [backward, setBackward] = useState(DEFAULT.backward)
  const [minLength, setMinLength] = useState(DEFAULT.minLength)
  const [imgError, setImgError] = useState<string | null>(null)

  const imageSrc = useMemo(
    () =>
      buildTreewithloveUrl({
        width,
        height,
        length,
        angle,
        backward,
        minLength,
      }),
    [width, height, length, angle, backward, minLength],
  )

  const reset = useCallback(() => {
    setWidth(DEFAULT.width)
    setHeight(DEFAULT.height)
    setLength(DEFAULT.length)
    setAngle(DEFAULT.angle)
    setBackward(DEFAULT.backward)
    setMinLength(DEFAULT.minLength)
  }, [])

  return (
    <>
      <header className="hero">
        <p className="eyebrow">Fractal Lab</p>
        <h1>Tree with love</h1>
        <p className="lede">
          Same recursion as the classic turtle sketch: green <code>forward</code>, brown <code>backward</code>,{' '}
          <code>tree(0.8×length)</code> after each turn. Rendered server-side as PNG (
          <code>GET /api/treewithlove.png</code>) — no browser turtle.
        </p>
      </header>

      <section className="panel controls">
        <h2>Parameters</h2>
        <div className="grid2">
          <label>
            <span>Initial length</span>
            <input
              type="number"
              min={10}
              max={300}
              step={1}
              value={length}
              onChange={(e) => setLength(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Angle (°)</span>
            <input
              type="number"
              min={5}
              max={80}
              step={0.5}
              value={angle}
              onChange={(e) => setAngle(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Backward (root offset)</span>
            <input
              type="number"
              min={0}
              max={400}
              step={1}
              value={backward}
              onChange={(e) => setBackward(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Min length (stop)</span>
            <input
              type="number"
              min={2}
              max={50}
              step={0.5}
              value={minLength}
              onChange={(e) => setMinLength(Number(e.target.value))}
            />
          </label>
        </div>

        <h2 className="h2-tight">Image size</h2>
        <div className="grid2">
          <label>
            <span>Width (px)</span>
            <input
              type="number"
              min={64}
              max={2048}
              value={width}
              onChange={(e) => setWidth(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Height (px)</span>
            <input
              type="number"
              min={64}
              max={2048}
              value={height}
              onChange={(e) => setHeight(Number(e.target.value))}
            />
          </label>
        </div>
        <div className="actions">
          <button type="button" onClick={reset}>
            Reset (turtle defaults)
          </button>
        </div>
      </section>

      <section className="panel preview">
        <h2>Render</h2>
        {imgError ? (
          <p className="error" role="alert">
            {imgError}
          </p>
        ) : null}
        <div className="img-wrap">
          <img
            src={imageSrc}
            alt="Tree with love fractal"
            width={width}
            height={height}
            onLoad={() => setImgError(null)}
            onError={() =>
              setImgError(
                'Could not load image. Start the API: cd backend && uvicorn main:app --reload --port 8002',
              )
            }
          />
        </div>
        <p className="url-hint">
          <code>{imageSrc}</code>
        </p>
      </section>
    </>
  )
}
