import { NavLink, Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div className="shell">
      <nav className="nav" aria-label="Fractal types">
        <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')} end>
          Mandelbrot
        </NavLink>
        <NavLink to="/julia" className={({ isActive }) => (isActive ? 'active' : '')}>
          Julia
        </NavLink>
        <NavLink to="/tree" className={({ isActive }) => (isActive ? 'active' : '')}>
          Tree
        </NavLink>
        <NavLink to="/treewithlove" className={({ isActive }) => (isActive ? 'active' : '')}>
          Tree with love
        </NavLink>
        <NavLink to="/barnsley" className={({ isActive }) => (isActive ? 'active' : '')}>
          Barnsley fern
        </NavLink>
      </nav>
      <Outlet />
    </div>
  )
}
