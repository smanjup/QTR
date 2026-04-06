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
      </nav>
      <Outlet />
    </div>
  )
}
