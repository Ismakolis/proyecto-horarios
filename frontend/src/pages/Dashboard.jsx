import { useEffect, useState } from 'react'
import { getDocentes, getCarreras, getPeriodos, getHorarios } from '../services/api'
import { useAuth } from '../context/useAuth'

export default function Dashboard() {
  const { usuario } = useAuth()
  const [stats, setStats] = useState({ docentes: 0, carreras: 0, periodos: 0, horarios: 0 })

  useEffect(() => {
    Promise.all([getDocentes(), getCarreras(), getPeriodos(), getHorarios({})])
      .then(([d, c, p, h]) => setStats({
        docentes: d.data.length,
        carreras: c.data.length,
        periodos: p.data.length,
        horarios: h.data.length,
      }))
      .catch(() => {})
  }, [])

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Bienvenido, {usuario?.nombre} 👋</h1>
          <p>Panel de control — Sistema de Horarios ITQ</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>{stats.docentes}</h3>
          <p>👨‍🏫 Docentes registrados</p>
        </div>
        <div className="stat-card">
          <h3>{stats.carreras}</h3>
          <p>🎓 Carreras activas</p>
        </div>
        <div className="stat-card">
          <h3>{stats.periodos}</h3>
          <p>📅 Períodos académicos</p>
        </div>
        <div className="stat-card">
          <h3>{stats.horarios}</h3>
          <p>📆 Horarios generados</p>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginBottom: 12, fontSize: 16 }}>Accesos rápidos</h2>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {[
            { label: '+ Nuevo docente', path: '/docentes' },
            { label: '+ Nueva carrera', path: '/carreras' },
            { label: '+ Nuevo período', path: '/periodos' },
            { label: '⚡ Generar horarios', path: '/horarios' },
          ].map(item => (
            <a key={item.path} href={item.path} className="btn btn-primary" style={{ textDecoration: 'none' }}>
              {item.label}
            </a>
          ))}
        </div>
      </div>
    </>
  )
}