import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Lookup from './pages/Lookup'
import Feed from './pages/Feed'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-text">ARES</div>
        <div className="logo-sub">CTI Dashboard</div>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/dashboard"
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="1" y="1" width="6" height="6" rx="1" />
            <rect x="9" y="1" width="6" height="6" rx="1" />
            <rect x="1" y="9" width="6" height="6" rx="1" />
            <rect x="9" y="9" width="6" height="6" rx="1" />
          </svg>
          Overview
        </NavLink>

        <NavLink
          to="/lookup"
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="6.5" cy="6.5" r="5" />
            <path d="M10.5 10.5L14 14" strokeLinecap="round" />
          </svg>
          IOC Lookup
        </NavLink>

        <NavLink
          to="/feed"
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <svg className="nav-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M2 4h12M2 8h8M2 12h5" strokeLinecap="round" />
          </svg>
          Threat Feed
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="status-row">
          <span className="status-dot" />
          Systems online
        </div>
      </div>
    </aside>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/lookup" element={<Lookup />} />
            <Route path="/feed" element={<Feed />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
