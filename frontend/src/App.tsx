import { Routes, Route, NavLink } from 'react-router-dom'
import ApplicationPage from './pages/ApplicationPage'
import ResultsPage from './pages/ResultsPage'
import PoliciesPage from './pages/PoliciesPage'

function Navbar() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive
        ? 'bg-indigo-600 text-white'
        : 'text-slate-400 hover:text-white hover:bg-[#2a2d3e]'
    }`

  return (
    <nav className="border-b border-[#2a2d3e] bg-[#1a1d2e]">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-2">
        <span className="text-white font-bold text-lg mr-6 tracking-tight">
          <span className="text-indigo-400">Kaaj</span> Lender Platform
        </span>
        <NavLink to="/" end className={linkClass}>
          New Application
        </NavLink>
        <NavLink to="/policies" className={linkClass}>
          Policies
        </NavLink>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-[#0f1117]">
      <Navbar />
      <Routes>
        <Route path="/" element={<ApplicationPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/policies" element={<PoliciesPage />} />
      </Routes>
    </div>
  )
}
