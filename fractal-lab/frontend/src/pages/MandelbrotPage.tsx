import { useCallback, useMemo, useState } from 'react'

const DEFAULT = {
  xmin: -2.2,
  xmax: 0.8,
  ymin: -1.15,
  ymax: 1.15,
  width: 800,
  height: 600,
  maxIter: 256,
}

function buildFractalUrl(params: {
  xmin: number
  xmax: number
  ymin: number
  ymax: number
  width: number
  height: number
  maxIter: number
}) {
  const q = new URLSearchParams({
    xmin: String(params.xmin),
    xmax: String(params.xmax),
    ymin: String(params.ymin),
    ymax: String(params.ymax),
    width: String(Math.round(params.width)),
    height: String(Math.round(params.height)),
    max_iter: String(Math.round(params.maxIter)),
  })
  return `/api/fractal.png?${q.toString()}`
}

export default function MandelbrotPage() {
  const [xmin, setXmin] = useState(DEFAULT.xmin)
  const [xmax, setXmax] = useState(DEFAULT.xmax)
  const [ymin, setYmin] = useState(DEFAULT.ymin)
  const [ymax, setYmax] = useState(DEFAULT.ymax)
  const [width, setWidth] = useState(DEFAULT.width)
  const [height, setHeight] = useState(DEFAULT.height)
  const [maxIter, setMaxIter] = useState(DEFAULT.maxIter)
  const [imgError, setImgError] = useState<string | null>(null)

  const imageSrc = useMemo(
    () =>
      buildFractalUrl({
        xmin,
        xmax,
        ymin,
        ymax,
        width,
        height,
        maxIter,
      }),
    [xmin, xmax, ymin, ymax, width, height, maxIter],
  )

  const resetView = useCallback(() => {
    setXmin(DEFAULT.xmin)
    setXmax(DEFAULT.xmax)
    setYmin(DEFAULT.ymin)
    setYmax(DEFAULT.ymax)
    setMaxIter(DEFAULT.maxIter)
  }, [])

  const zoomIn = useCallback(() => {
    const cx = (xmin + xmax) / 2
    const cy = (ymin + ymax) / 2
    const hw = (xmax - xmin) / 4
    const hh = (ymax - ymin) / 4
    setXmin(cx - hw)
    setXmax(cx + hw)
    setYmin(cy - hh)
    setYmax(cy + hh)
  }, [xmin, xmax, ymin, ymax])

  return (
    <>
      <header className="hero">
        <p className="eyebrow">Fractal Lab</p>
        <h1>Mandelbrot set</h1>
        <p className="lede">
          Python (NumPy) renders a PNG; React loads it via the Vite dev proxy (<code>/api</code> → port{' '}
          <code>8002</code>).
        </p>
      </header>

      <section className="panel controls">
        <h2>View</h2>
        <div className="grid2">
          <label>
            <span>x min</span>
            <input
              type="number"
              step="0.01"
              value={xmin}
              onChange={(e) => setXmin(Number(e.target.value))}
            />
          </label>
          <label>
            <span>x max</span>
            <input
              type="number"
              step="0.01"
              value={xmax}
              onChange={(e) => setXmax(Number(e.target.value))}
            />
          </label>
          <label>
            <span>y min</span>
            <input
              type="number"
              step="0.01"
              value={ymin}
              onChange={(e) => setYmin(Number(e.target.value))}
            />
          </label>
          <label>
            <span>y max</span>
            <input
              type="number"
              step="0.01"
              value={ymax}
              onChange={(e) => setYmax(Number(e.target.value))}
            />
          </label>
        </div>
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
          <label className="span2">
            <span>Max iterations</span>
            <input
              type="number"
              min={16}
              max={5000}
              value={maxIter}
              onChange={(e) => setMaxIter(Number(e.target.value))}
            />
          </label>
        </div>
        <div className="actions">
          <button type="button" onClick={resetView}>
            Reset view
          </button>
          <button type="button" onClick={zoomIn}>
            Zoom in (center)
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
            alt="Mandelbrot set"
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
