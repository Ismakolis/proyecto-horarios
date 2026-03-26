import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDocentes, getCarreras, getPeriodos, getHorarios } from '../services/api'
import { useAuth } from '../context/useAuth'

const StatIcon = ({ d, color }) => (
  <div className={`stat-card-icon ${color}`}>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d={d} />
    </svg>
  </div>
)

const QUICK_LINKS = [
  {
    label: 'Docentes',
    desc: 'Gestionar personal docente',
    path: '/docentes',
    d: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 11a4 4 0 100-8 4 4 0 000 8z',
    color: 'red',
  },
  {
    label: 'Carreras',
    desc: 'Niveles y paralelos',
    path: '/carreras',
    d: 'M22 10v6M2 10l10-5 10 5-10 5z M6 12v5c3 3 9 3 12 0v-5',
    color: 'blue',
  },
  {
    label: 'Periodos',
    desc: 'Modulos academicos',
    path: '/periodos',
    d: 'M8 2v4 M16 2v4 M3 10h18 M3 6a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V6z',
    color: 'green',
  },
  {
    label: 'Horarios',
    desc: 'Generar y editar',
    path: '/horarios',
    d: 'M12 2a10 10 0 100 20 10 10 0 000-20z M12 6v6l4 2',
    color: 'amber',
  },
  {
    label: 'Reportes',
    desc: 'Exportar a Excel',
    path: '/reportes',
    d: 'M18 20V10 M12 20V4 M6 20v-6',
    color: 'blue',
  },
]

export default function Dashboard() {
  const { usuario } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({ docentes: 0, carreras: 0, periodos: 0, horarios: 0 })
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    Promise.all([getDocentes(), getCarreras(), getPeriodos(), getHorarios({})])
      .then(([d, c, p, h]) => setStats({
        docentes: d.data.length,
        carreras: c.data.length,
        periodos: p.data.length,
        horarios: h.data.length,
      }))
      .catch(() => { })
      .finally(() => setCargando(false))
  }, [])

  const STATS = [
    { label: 'Docentes', value: stats.docentes, color: 'red', d: 'M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 11a4 4 0 100-8 4 4 0 000 8z' },
    { label: 'Carreras', value: stats.carreras, color: 'blue', d: 'M22 10v6M2 10l10-5 10 5-10 5z M6 12v5c3 3 9 3 12 0v-5' },
    { label: 'Periodos', value: stats.periodos, color: 'green', d: 'M8 2v4 M16 2v4 M3 10h18 M3 6a2 2 0 012-2h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V6z' },
    { label: 'Horarios', value: stats.horarios, color: 'amber', d: 'M12 2a10 10 0 100 20 10 10 0 000-20z M12 6v6l4 2' },
  ]

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Bienvenido, {usuario?.nombre}</h1>
          <p>Panel de control — Sistema de Horarios ITQ</p>
        </div>
      </div>

      {cargando ? (
        <div className="loading"><div className="loading-spinner" /> Cargando datos...</div>
      ) : (
        <>
          <div className="stats-grid">
            {STATS.map((s, i) => (
              <div key={s.label} className="stat-card" style={{ animationDelay: `${i * 0.06}s` }}>
                <StatIcon d={s.d} color={s.color} />
                <h3>{s.value}</h3>
                <p>{s.label}</p>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Accesos rapidos</h3>
            </div>
            <div className="quick-links-grid">
              {QUICK_LINKS.map(link => (
                <button
                  key={link.path}
                  className="quick-link-card"
                  onClick={() => navigate(link.path)}
                >
                  <div className={`quick-link-icon stat-card-icon ${link.color}`}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d={link.d} />
                    </svg>
                  </div>
                  <div className="quick-link-text">
                    <span className="quick-link-label">{link.label}</span>
                    <span className="quick-link-desc">{link.desc}</span>
                  </div>
                  <svg className="quick-link-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </button>
              ))}
            </div>
          </div>

          <div className="card info-card">
            <div className="info-card-icon">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <div>
              <p className="info-card-title">Flujo recomendado</p>
              <p className="info-card-body">
                Crea las <strong>carreras</strong> con sus niveles, agrega las <strong>asignaturas</strong>,
                registra los <strong>docentes</strong> con sus habilidades, define un <strong>periodo academico</strong> y
                finalmente genera los <strong>horarios</strong> automaticamente.
              </p>
            </div>
          </div>
        </>
      )}
    </>
  )
}

