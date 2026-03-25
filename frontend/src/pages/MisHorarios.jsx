import { useEffect, useState, useCallback } from 'react'
import { getHorarios, getCarreras, getPeriodos, getAsignaturas } from '../services/api'
import { useAuth } from '../context/useAuth'

const TablaJornada = ({ jornada, titulo, horarioTxt, horarios, asignaturas, carreras, niveles, periodos }) => {
  const items = horarios.filter(h => h.jornada === jornada)
  if (items.length === 0) return null

  const getNombreAsignatura = (id) => asignaturas.find(a => a.id === id)?.nombre || '...'
  const getNombreCarrera = (id) => carreras.find(c => c.id === id)?.nombre || '...'
  const getNivelNumero = (id) => niveles.find(n => n.id === id)?.numero || ''
  const getNombreModulo = (pId, mId) => {
    const p = periodos.find(p => p.id === pId)
    return p?.modulos?.find(m => m.id === mId) || null
  }

  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ background: jornada === 'matutina' ? '#1e40af' : '#374151', color: '#fff', padding: '10px 18px', borderRadius: '8px 8px 0 0', display: 'flex', justifyContent: 'space-between' }}>
        <span style={{ fontWeight: 700, fontSize: 13 }}>{jornada === 'matutina' ? '☀️' : '🌙'} {titulo}</span>
        <span style={{ fontSize: 12, opacity: 0.8 }}>{horarioTxt}</span>
      </div>
      <div style={{ overflowX: 'auto', border: '1px solid #e5e7eb', borderTop: 'none', borderRadius: '0 0 8px 8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#f8fafc' }}>
              {['Módulo', 'Fecha inicio', 'Fecha fin', 'Asignatura', 'Carrera', 'Nivel', 'Paralelo', 'Horario'].map((col, i) => (
                <th key={i} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, fontSize: 12, color: '#475569', borderBottom: '1px solid #e5e7eb' }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...items].sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio)).map((h, idx) => {
              const modulo = getNombreModulo(h.periodo_id, h.modulo_id)
              return (
                <tr key={h.id} style={{ background: idx % 2 === 0 ? '#fff' : '#f9fafb', borderBottom: '1px solid #f0f0f0' }}>
                  <td style={{ padding: '10px 14px', fontWeight: 600 }}>{modulo?.nombre || 'Módulo'}</td>
                  <td style={{ padding: '10px 14px', color: '#6b7280', fontSize: 12 }}>{modulo?.fecha_inicio || '-'}</td>
                  <td style={{ padding: '10px 14px', color: '#6b7280', fontSize: 12 }}>{modulo?.fecha_fin || '-'}</td>
                  <td style={{ padding: '10px 14px', fontWeight: 600 }}>{getNombreAsignatura(h.asignatura_id)}</td>
                  <td style={{ padding: '10px 14px', fontSize: 12 }}>{getNombreCarrera(h.carrera_id)}</td>
                  <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <span style={{ background: '#dbeafe', color: '#1e40af', borderRadius: 6, padding: '2px 8px', fontSize: 12, fontWeight: 700 }}>
                      {getNivelNumero(h.nivel_id)}
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <span style={{ background: '#fef3c7', color: '#92400e', borderRadius: 6, padding: '2px 10px', fontSize: 12, fontWeight: 700 }}>
                      {h.paralelo}
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px', fontWeight: 600 }}>{h.hora_inicio} - {h.hora_fin}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function MisHorarios() {
  const { usuario } = useAuth()
  const [horarios, setHorarios] = useState([])
  const [carreras, setCarreras] = useState([])
  const [periodos, setPeriodos] = useState([])
  const [asignaturas, setAsignaturas] = useState([])
  const [niveles, setNiveles] = useState([])
  const [periodoId, setPeriodoId] = useState('')
  const [modulosFiltro, setModulosFiltro] = useState([])
  const [moduloId, setModuloId] = useState('')

  useEffect(() => {
    Promise.all([getCarreras(), getPeriodos(), getAsignaturas()])
      .then(([c, p, a]) => {
        setCarreras(c.data)
        setPeriodos(p.data)
        setAsignaturas(a.data)
        setNiveles(c.data.flatMap(car => car.niveles || []))
      })
      .catch(() => {})
  }, [])

  const cargarHorarios = useCallback(() => {
    if (!usuario?.docente_id) return
    const params = { docente_id: usuario.docente_id }
    if (periodoId) params.periodo_id = periodoId
    if (moduloId) params.modulo_id = moduloId
    getHorarios(params)
      .then(res => setHorarios(res.data))
      .catch(() => setHorarios([]))
  }, [usuario, periodoId, moduloId])

  useEffect(() => {
    cargarHorarios()
  }, [cargarHorarios])

  const onCambioPeriodo = (id) => {
    const periodo = periodos.find(p => p.id === id)
    setModulosFiltro(periodo?.modulos || [])
    setPeriodoId(id)
    setModuloId('')
  }

  const propTabla = { horarios, asignaturas, carreras, niveles, periodos }

  return (
    <>
      <div className="topbar">
        <div>
          <h1>📆 Mis Horarios</h1>
          <p>Bienvenido, {usuario?.nombre} {usuario?.apellido}</p>
        </div>
      </div>

      {!usuario?.docente_id ? (
        <div className="card">
          <div className="empty-state">
            <p style={{ fontSize: 32 }}>⚠️</p>
            <p>Tu cuenta no está vinculada a un docente.</p>
            <p style={{ fontSize: 13, color: '#6b7280', marginTop: 8 }}>
              Contacta al coordinador para vincular tu cuenta.
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="card" style={{ padding: 16, marginBottom: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label>Período</label>
                <select value={periodoId} onChange={e => onCambioPeriodo(e.target.value)}>
                  <option value="">Todos los períodos</option>
                  {periodos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                </select>
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label>Módulo</label>
                <select value={moduloId} onChange={e => setModuloId(e.target.value)} disabled={!periodoId}>
                  <option value="">Todos los módulos</option>
                  {modulosFiltro.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div className="card">
            {horarios.length === 0 ? (
              <div className="empty-state">
                <p style={{ fontSize: 32 }}>📆</p>
                <p>No tienes horarios asignados aún.</p>
              </div>
            ) : (
              <>
                <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 20 }}>
                  {horarios.length} horario(s) asignado(s)
                </p>
                <TablaJornada jornada="matutina" titulo="MODALIDAD PRESENCIAL — MATUTINO" horarioTxt="08:00 - 12:00" {...propTabla} />
                <TablaJornada jornada="nocturna" titulo="MODALIDAD PRESENCIAL — NOCTURNO" horarioTxt="18:30 - 21:30" {...propTabla} />
              </>
            )}
          </div>
        </>
      )}
    </>
  )
}