import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuth } from '../context/useAuth'

const navCoordinador = [
  { path: '/',            label: 'Dashboard',   icon: '◻' },
  { path: '/docentes',    label: 'Docentes',    icon: '👤' },
  { path: '/carreras',    label: 'Carreras',    icon: '🎓' },
  { path: '/asignaturas', label: 'Asignaturas', icon: '📚' },
  { path: '/periodos',    label: 'Períodos',    icon: '📅' },
  { path: '/horarios',    label: 'Horarios',    icon: '🗓' },
  { path: '/reportes',    label: 'Reportes',    icon: '📊' },
]
const navDocente = [
  { path: '/mis-horarios', label: 'Mis Horarios', icon: '🗓' },
]
const navAdministrativo = [
  { path: '/',         label: 'Dashboard', icon: '◻' },
  { path: '/horarios', label: 'Horarios',  icon: '🗓' },
  { path: '/reportes', label: 'Reportes',  icon: '📊' },
]

export default function Layout() {
  const { usuario, cerrarSesion, esCoordinador, esDocente } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (esDocente && location.pathname === '/') navigate('/mis-horarios')
  }, [esDocente, location.pathname, navigate])

  // Cierra sidebar al cambiar de página
  useEffect(() => { setSidebarOpen(false) }, [location.pathname])

  const handleLogout = () => { cerrarSesion(); navigate('/login') }
  const navItems  = esCoordinador ? navCoordinador : esDocente ? navDocente : navAdministrativo
  const rolLabel  = usuario?.rol || ''
  const initials  = `${usuario?.nombre?.[0] || ''}${usuario?.apellido?.[0] || ''}`.toUpperCase()

  return (
    <div className="layout">
      {/* Botón hamburger — solo mobile */}
      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(o => !o)}
        aria-label="Abrir menú"
      >
        <span /><span /><span />
      </button>

      {/* Overlay */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ITQ</div>
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
              <span className="nav-item-icon">{item.icon}</span>
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
