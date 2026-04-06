import { useCallback, useMemo, useState } from 'react'

const DEFAULT = {
  width: 800,
  height: 600,
  points: 350_000,
  skip: 50,
  xmin: -2.2,
  xmax: 2.7,
  ymin: 0,
  ymax: 10.1,
}

function buildBarnsleyUrl(params: {
  width: number
  height: number
  points: number
  skip: number
  xmin: number
  xmax: number
  ymin: number
  ymax: number
  seed: string
}) {
  const q = new URLSearchParams({
    width: String(Math.round(params.width)),
    height: String(Math.round(params.height)),
    points: String(Math.round(params.points)),
    skip: String(Math.round(params.skip)),
    xmin: String(params.xmin),
    xmax: String(params.xmax),
    ymin: String(params.ymin),
    ymax: String(params.ymax),
  })
  const s = params.seed.trim()
  if (s !== '' && /^-?\d+$/.test(s)) {
    q.set('seed', s)
  }
  return `/api/barnsley.png?${q.toString()}`
}

export default function BarnsleyFernPage() {
  const [width, setWidth] = useState(DEFAULT.width)
  const [height, setHeight] = useState(DEFAULT.height)
  const [points, setPoints] = useState(DEFAULT.points)
  const [skip, setSkip] = useState(DEFAULT.skip)
  const [xmin, setXmin] = useState(DEFAULT.xmin)
  const [xmax, setXmax] = useState(DEFAULT.xmax)
  const [ymin, setYmin] = useState(DEFAULT.ymin)
  const [ymax, setYmax] = useState(DEFAULT.ymax)
  const [seed, setSeed] = useState('')
  const [imgError, setImgError] = useState<string | null>(null)

  const imageSrc = useMemo(
    () =>
      buildBarnsleyUrl({
        width,
        height,
        points,
        skip,
        xmin,
        xmax,
        ymin,
        ymax,
        seed,
      }),
    [width, height, points, skip, xmin, xmax, ymin, ymax, seed],
  )

  const reset = useCallback(() => {
    setWidth(DEFAULT.width)
    setHeight(DEFAULT.height)
    setPoints(DEFAULT.points)
    setSkip(DEFAULT.skip)
    setXmin(DEFAULT.xmin)
    setXmax(DEFAULT.xmax)
    setYmin(DEFAULT.ymin)
    setYmax(DEFAULT.ymax)
    setSeed('')
  }, [])

  return (
    <>
      <header className="hero">
        <p className="eyebrow">Fractal Lab</p>
        <h1>Barnsley fern</h1>
        <p className="lede">
          Classic IFS with four affine maps (1% / 85% / 7% / 7%). Points are drawn into a density image (
          <code>GET /api/barnsley.png</code>).
        </p>
      </header>

      <section className="panel controls">
        <h2>Sampling</h2>
        <div className="grid2">
          <label>
            <span>Points (after burn-in)</span>
            <input
              type="number"
              min={10_000}
              max={2_000_000}
              step={10_000}
              value={points}
              onChange={(e) => setPoints(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Burn-in (skip)</span>
            <input
              type="number"
              min={0}
              max={50_000}
              step={10}
              value={skip}
              onChange={(e) => setSkip(Number(e.target.value))}
            />
          </label>
          <label className="span2">
            <span>Seed (optional, integer)</span>
            <input
              type="text"
              inputMode="numeric"
              placeholder="random"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
            />
          </label>
        </div>

        <h2 className="h2-tight">View bounds</h2>
        <div className="grid2">
          <label>
            <span>x min</span>
            <input
              type="number"
              step={0.1}
              value={xmin}
              onChange={(e) => setXmin(Number(e.target.value))}
            />
          </label>
          <label>
            <span>x max</span>
            <input
              type="number"
              step={0.1}
              value={xmax}
              onChange={(e) => setXmax(Number(e.target.value))}
            />
          </label>
          <label>
            <span>y min</span>
            <input
              type="number"
              step={0.1}
              value={ymin}
              onChange={(e) => setYmin(Number(e.target.value))}
            />
          </label>
          <label>
            <span>y max</span>
            <input
              type="number"
              step={0.1}
              value={ymax}
              onChange={(e) => setYmax(Number(e.target.value))}
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
            Reset defaults
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
            alt="Barnsley fern"
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
