import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuth } from '../context/useAuth'

const Icon = ({ d, size = 15 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
)

const ICONS = {
  dashboard:    'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10',
  docentes:     'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 11a4 4 0 100-8 4 4 0 000 8z',
  carreras:     'M22 10v6M2 10l10-5 10 5-10 5z M6 12v5c3 3 9 3 12 0v-5',
  asignaturas:  'M4 19.5A2.5 2.5 0 016.5 17H20 M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z',
  periodos:     'M8 2v4 M16 2v4 M3 10h18 M3 6a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V6z',
  horarios:     'M12 2a10 10 0 100 20 10 10 0 000-20z M12 6v6l4 2',
  reportes:     'M18 20V10 M12 20V4 M6 20v-6',
  mishorarios:  'M12 2a10 10 0 100 20 10 10 0 000-20z M12 6v6l4 2',
}

const navCoordinador = [
  { path: '/',            label: 'Dashboard',   icon: 'dashboard' },
  { path: '/docentes',    label: 'Docentes',    icon: 'docentes' },
  { path: '/carreras',    label: 'Carreras',    icon: 'carreras' },
  { path: '/asignaturas', label: 'Asignaturas', icon: 'asignaturas' },
  { path: '/periodos',    label: 'Períodos',    icon: 'periodos' },
  { path: '/horarios',    label: 'Horarios',    icon: 'horarios' },
  { path: '/reportes',    label: 'Reportes',    icon: 'reportes' },
]
const navDocente = [
  { path: '/mis-horarios', label: 'Mis Horarios', icon: 'mishorarios' },
]
const navAdministrativo = [
  { path: '/',         label: 'Dashboard', icon: 'dashboard' },
  { path: '/horarios', label: 'Horarios',  icon: 'horarios' },
  { path: '/reportes', label: 'Reportes',  icon: 'reportes' },
]

const CalendarIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="3"/>
    <line x1="16" y1="2" x2="16" y2="6"/>
    <line x1="8" y1="2" x2="8" y2="6"/>
    <line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
)

export default function Layout() {
  const { usuario, cerrarSesion, esCoordinador, esDocente } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (esDocente && location.pathname === '/') navigate('/mis-horarios')
  }, [esDocente, location.pathname, navigate])

  useEffect(() => { setSidebarOpen(false) }, [location.pathname])

  const handleLogout = () => { cerrarSesion(); navigate('/login') }
  const navItems = esCoordinador ? navCoordinador : esDocente ? navDocente : navAdministrativo
  const rolLabel = usuario?.rol || ''
  const initials = `${usuario?.nombre?.[0] || ''}${usuario?.apellido?.[0] || ''}`.toUpperCase()

  return (
    <div className="layout">
      <button className="sidebar-toggle" onClick={() => setSidebarOpen(o => !o)} aria-label="Menu">
        <span /><span /><span />
      </button>

      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} />

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <CalendarIcon />
          </div>
          <div className="sidebar-logo-text">
            <h2>Horarios ITQ</h2>
            <p>Sistema Académico</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
            <button
              key={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="nav-item-icon">
                <Icon d={ICONS[item.icon]} />
              </span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-card">
            <div className="user-avatar">{initials}</div>
            <div className="user-card-info">
              <strong>{usuario?.nombre} {usuario?.apellido}</strong>
              <span className={`user-role-badge ${rolLabel}`}>{rolLabel}</span>
            </div>
          </div>
          <button className="btn-logout" onClick={handleLogout}>Cerrar sesión</button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
