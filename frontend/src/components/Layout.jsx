/**
 * Layout.jsx
 * Componente principal de estructura: sidebar + contenido.
 * Renderiza la navegacion segun el rol del usuario autenticado.
 */

import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from '../context/useAuth'

// Elementos de navegacion por rol
const navCoordinador = [
  { path: '/',            label: 'Dashboard',   icon: 'D' },
  { path: '/docentes',    label: 'Docentes',    icon: 'P' },
  { path: '/carreras',    label: 'Carreras',    icon: 'C' },
  { path: '/asignaturas', label: 'Asignaturas', icon: 'A' },
  { path: '/periodos',    label: 'Periodos',    icon: 'M' },
  { path: '/horarios',    label: 'Horarios',    icon: 'H' },
  { path: '/reportes',    label: 'Reportes',    icon: 'R' },
]

const navDocente = [
  { path: '/mis-horarios', label: 'Mis Horarios', icon: 'H' },
]

const navAdministrativo = [
  { path: '/',          label: 'Dashboard', icon: 'D' },
  { path: '/horarios',  label: 'Horarios',  icon: 'H' },
  { path: '/reportes',  label: 'Reportes',  icon: 'R' },
]

export default function Layout() {
  const { usuario, cerrarSesion, esCoordinador, esDocente } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  // Redirigir al docente si intenta acceder al dashboard
  useEffect(() => {
    if (esDocente && location.pathname === '/') {
      navigate('/mis-horarios')
    }
  }, [esDocente, location.pathname, navigate])

  const handleLogout = () => {
    cerrarSesion()
    navigate('/login')
  }

  // Seleccionar menu segun rol
  const navItems = esCoordinador
    ? navCoordinador
    : esDocente
    ? navDocente
    : navAdministrativo

  const rolLabel = usuario?.rol || ''

  return (
    <div className="layout">
      {/* Sidebar de navegacion */}
      <aside className="sidebar">
        {/* Logo institucional */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ITQ</div>
          <div className="sidebar-logo-text">
            <h2>Horarios ITQ</h2>
            <p>Sistema Academico</p>
          </div>
        </div>

        {/* Menu de navegacion */}
        <nav className="sidebar-nav">
          {navItems.map(item => (
            <button
              key={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="nav-item-icon"
                style={{
                  width: 20,
                  height: 20,
                  borderRadius: 4,
                  background: location.pathname === item.path ? 'var(--rojo-itq)' : '#2a2a2a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 10,
                  fontWeight: 800,
                  color: '#fff',
                  flexShrink: 0,
                }}
              >
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Informacion del usuario */}
        <div className="sidebar-footer">
          <div className="user-info">
            <strong>{usuario?.nombre} {usuario?.apellido}</strong>
            <span className={`user-role-badge ${rolLabel}`}>{rolLabel}</span>
          </div>
          <button className="btn-logout" onClick={handleLogout}>
            Cerrar sesion
          </button>
        </div>
      </aside>

      {/* Contenido principal */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
