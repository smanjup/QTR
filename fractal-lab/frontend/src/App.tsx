import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './Layout'
import JuliaPage from './pages/JuliaPage'
import MandelbrotPage from './pages/MandelbrotPage'
import TreePage from './pages/TreePage'
import BarnsleyFernPage from './pages/BarnsleyFernPage'
import TreewithlovePage from './pages/TreewithlovePage'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<MandelbrotPage />} />
          <Route path="/julia" element={<JuliaPage />} />
          <Route path="/tree" element={<TreePage />} />
          <Route path="/treewithlove" element={<TreewithlovePage />} />
          <Route path="/barnsley" element={<BarnsleyFernPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
