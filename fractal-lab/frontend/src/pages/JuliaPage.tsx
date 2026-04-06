import { useCallback, useMemo, useState } from 'react'

const DEFAULT = {
  xmin: -2.0,
  xmax: 2.0,
  ymin: -2.0,
  ymax: 2.0,
  cx: -0.8,
  cy: 0.156,
  width: 800,
  height: 600,
  maxIter: 256,
}

function buildJuliaUrl(params: {
  xmin: number
  xmax: number
  ymin: number
  ymax: number
  cx: number
  cy: number
  width: number
  height: number
  maxIter: number
}) {
  const q = new URLSearchParams({
    xmin: String(params.xmin),
    xmax: String(params.xmax),
    ymin: String(params.ymin),
    ymax: String(params.ymax),
    cx: String(params.cx),
    cy: String(params.cy),
    width: String(Math.round(params.width)),
    height: String(Math.round(params.height)),
    max_iter: String(Math.round(params.maxIter)),
  })
  return `/api/julia.png?${q.toString()}`
}

export default function JuliaPage() {
  const [xmin, setXmin] = useState(DEFAULT.xmin)
  const [xmax, setXmax] = useState(DEFAULT.xmax)
  const [ymin, setYmin] = useState(DEFAULT.ymin)
  const [ymax, setYmax] = useState(DEFAULT.ymax)
  const [cx, setCx] = useState(DEFAULT.cx)
  const [cy, setCy] = useState(DEFAULT.cy)
  const [width, setWidth] = useState(DEFAULT.width)
  const [height, setHeight] = useState(DEFAULT.height)
  const [maxIter, setMaxIter] = useState(DEFAULT.maxIter)
  const [imgError, setImgError] = useState<string | null>(null)

  const imageSrc = useMemo(
    () =>
      buildJuliaUrl({
        xmin,
        xmax,
        ymin,
        ymax,
        cx,
        cy,
        width,
        height,
        maxIter,
      }),
    [xmin, xmax, ymin, ymax, cx, cy, width, height, maxIter],
  )

  const resetView = useCallback(() => {
    setXmin(DEFAULT.xmin)
    setXmax(DEFAULT.xmax)
    setYmin(DEFAULT.ymin)
    setYmax(DEFAULT.ymax)
    setCx(DEFAULT.cx)
    setCy(DEFAULT.cy)
    setMaxIter(DEFAULT.maxIter)
  }, [])

  const zoomIn = useCallback(() => {
    const zx = (xmin + xmax) / 2
    const zy = (ymin + ymax) / 2
    const hw = (xmax - xmin) / 4
    const hh = (ymax - ymin) / 4
    setXmin(zx - hw)
    setXmax(zx + hw)
    setYmin(zy - hh)
    setYmax(zy + hh)
  }, [xmin, xmax, ymin, ymax])

  return (
    <>
      <header className="hero">
        <p className="eyebrow">Fractal Lab</p>
        <h1>Julia set</h1>
        <p className="lede">
          Iterate <code>z → z² + c</code> from each pixel; <code>c</code> is fixed. Same PNG pipeline as Mandelbrot (
          <code>GET /api/julia.png</code>).
        </p>
      </header>

      <section className="panel controls">
        <h2>Julia constant c</h2>
        <div className="grid2">
          <label>
            <span>c real</span>
            <input
              type="number"
              step="0.001"
              value={cx}
              onChange={(e) => setCx(Number(e.target.value))}
            />
          </label>
          <label>
            <span>c imag</span>
            <input
              type="number"
              step="0.001"
              value={cy}
              onChange={(e) => setCy(Number(e.target.value))}
            />
          </label>
        </div>

        <h2 className="h2-tight">View</h2>
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
            Reset view &amp; c
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
            alt="Julia set"
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
