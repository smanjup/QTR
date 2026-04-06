import { useCallback, useMemo, useState } from 'react'

const DEFAULT = {
  width: 800,
  height: 600,
  depth: 10,
  branchAngle: 28,
  lengthScale: 0.72,
  trunkFrac: 0.22,
  originX: 0.5,
  originY: 0.92,
}

function buildTreeUrl(params: {
  width: number
  height: number
  depth: number
  branchAngle: number
  lengthScale: number
  trunkFrac: number
  originX: number
  originY: number
}) {
  const q = new URLSearchParams({
    width: String(Math.round(params.width)),
    height: String(Math.round(params.height)),
    depth: String(Math.round(params.depth)),
    branch_angle: String(params.branchAngle),
    length_scale: String(params.lengthScale),
    trunk_frac: String(params.trunkFrac),
    origin_x: String(params.originX),
    origin_y: String(params.originY),
  })
  return `/api/tree.png?${q.toString()}`
}

export default function TreePage() {
  const [width, setWidth] = useState(DEFAULT.width)
  const [height, setHeight] = useState(DEFAULT.height)
  const [depth, setDepth] = useState(DEFAULT.depth)
  const [branchAngle, setBranchAngle] = useState(DEFAULT.branchAngle)
  const [lengthScale, setLengthScale] = useState(DEFAULT.lengthScale)
  const [trunkFrac, setTrunkFrac] = useState(DEFAULT.trunkFrac)
  const [originX, setOriginX] = useState(DEFAULT.originX)
  const [originY, setOriginY] = useState(DEFAULT.originY)
  const [imgError, setImgError] = useState<string | null>(null)

  const imageSrc = useMemo(
    () =>
      buildTreeUrl({
        width,
        height,
        depth,
        branchAngle,
        lengthScale,
        trunkFrac,
        originX,
        originY,
      }),
    [width, height, depth, branchAngle, lengthScale, trunkFrac, originX, originY],
  )

  const reset = useCallback(() => {
    setWidth(DEFAULT.width)
    setHeight(DEFAULT.height)
    setDepth(DEFAULT.depth)
    setBranchAngle(DEFAULT.branchAngle)
    setLengthScale(DEFAULT.lengthScale)
    setTrunkFrac(DEFAULT.trunkFrac)
    setOriginX(DEFAULT.originX)
    setOriginY(DEFAULT.originY)
  }, [])

  return (
    <>
      <header className="hero">
        <p className="eyebrow">Fractal Lab</p>
        <h1>Fractal tree</h1>
        <p className="lede">
          Recursive binary tree in the plane: each branch splits by ±angle with length scaled each level. Rendered with
          Pillow (<code>GET /api/tree.png</code>).
        </p>
      </header>

      <section className="panel controls">
        <h2>Tree parameters</h2>
        <div className="grid2">
          <label>
            <span>Depth</span>
            <input
              type="number"
              min={1}
              max={16}
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Branch angle (°)</span>
            <input
              type="number"
              min={5}
              max={85}
              step={0.5}
              value={branchAngle}
              onChange={(e) => setBranchAngle(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Length scale</span>
            <input
              type="number"
              min={0.35}
              max={0.92}
              step={0.01}
              value={lengthScale}
              onChange={(e) => setLengthScale(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Trunk (height frac.)</span>
            <input
              type="number"
              min={0.05}
              max={0.45}
              step={0.01}
              value={trunkFrac}
              onChange={(e) => setTrunkFrac(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Origin x (0–1)</span>
            <input
              type="number"
              min={0.05}
              max={0.95}
              step={0.01}
              value={originX}
              onChange={(e) => setOriginX(Number(e.target.value))}
            />
          </label>
          <label>
            <span>Origin y (0–1)</span>
            <input
              type="number"
              min={0.5}
              max={0.99}
              step={0.01}
              value={originY}
              onChange={(e) => setOriginY(Number(e.target.value))}
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
            alt="Fractal tree"
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
