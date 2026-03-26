/**
 * Layout.jsx
 * Estructura principal: sidebar estilo Kenjo + contenido.
 */
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from '../context/useAuth'

const ICONS = {
  dashboard:    '◻',
  docentes:     '👤',
  carreras:     '🎓',
  asignaturas:  '📚',
  periodos:     '📅',
  horarios:     '🗓',
  reportes:     '📊',
  mishorarios:  '🗓',
}

const navCoordinador = [
  { path: '/',            label: 'Dashboard',   icon: ICONS.dashboard },
  { path: '/docentes',    label: 'Docentes',    icon: ICONS.docentes },
  { path: '/carreras',    label: 'Carreras',    icon: ICONS.carreras },
  { path: '/asignaturas', label: 'Asignaturas', icon: ICONS.asignaturas },
  { path: '/periodos',    label: 'Periodos',    icon: ICONS.periodos },
  { path: '/horarios',    label: 'Horarios',    icon: ICONS.horarios },
  { path: '/reportes',    label: 'Reportes',    icon: ICONS.reportes },
]
const navDocente = [
  { path: '/mis-horarios', label: 'Mis Horarios', icon: ICONS.mishorarios },
]
const navAdministrativo = [
  { path: '/',          label: 'Dashboard', icon: ICONS.dashboard },
  { path: '/horarios',  label: 'Horarios',  icon: ICONS.horarios },
  { path: '/reportes',  label: 'Reportes',  icon: ICONS.reportes },
]

export default function Layout() {
  const { usuario, cerrarSesion, esCoordinador, esDocente } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()

  useEffect(() => {
    if (esDocente && location.pathname === '/') navigate('/mis-horarios')
  }, [esDocente, location.pathname, navigate])

  const handleLogout = () => { cerrarSesion(); navigate('/login') }

  const navItems = esCoordinador ? navCoordinador : esDocente ? navDocente : navAdministrativo
  const rolLabel = usuario?.rol || ''
  const initiales = `${usuario?.nombre?.[0] || ''}${usuario?.apellido?.[0] || ''}`.toUpperCase()

  return (
    <div className="layout">
      <aside className="sidebar">
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ITQ</div>
          <div className="sidebar-logo-text">
            <h2>Horarios ITQ</h2>
            <p>Sistema Academico</p>
          </div>
        </div>

        {/* Nav */}
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

        {/* Footer */}
        <div className="sidebar-footer">
          <div className="user-card">
            <div className="user-avatar">{initiales}</div>
            <div className="user-card-info">
              <strong>{usuario?.nombre} {usuario?.apellido}</strong>
              <span className={`user-role-badge ${rolLabel}`}>{rolLabel}</span>
            </div>
          </div>
          <button className="btn-logout" onClick={handleLogout}>
            Cerrar sesion
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
