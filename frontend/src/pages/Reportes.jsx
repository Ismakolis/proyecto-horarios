import { useEffect, useState } from 'react'
import { getCarreras, getPeriodos, getDocentes, exportarExcelCarrera, exportarExcelNivel, exportarExcelDocente } from '../services/api'

export default function Reportes() {
  const [carreras, setCarreras] = useState([])
  const [periodos, setPeriodos] = useState([])
  const [docentes, setDocentes] = useState([])
  const [periodoId, setPeriodoId] = useState('')
  const [carreraId, setCarreraId] = useState('')
  const [nivelId, setNivelId] = useState('')
  const [busquedaDocente, setBusquedaDocente] = useState('')
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [descargando, setDescargando] = useState('')

  useEffect(() => {
    Promise.all([getCarreras(), getPeriodos(), getDocentes()])
      .then(([c, p, d]) => {
        setCarreras(c.data)
        setPeriodos(p.data)
        setDocentes(d.data)
        if (p.data.length > 0) setPeriodoId(p.data[0].id)
      })
      .catch(() => setError('Error al cargar datos'))
  }, [])

  const carreraSeleccionada = carreras.find(c => c.id === carreraId)
  const nivelesCarrera = carreraSeleccionada?.niveles?.slice().sort((a, b) => a.numero - b.numero) || []
  const nivelSeleccionado = nivelesCarrera.find(n => n.id === nivelId)
  const docentesFiltrados = docentes.filter(d =>
    d.activo &&
    `${d.nombre} ${d.apellido}`.toLowerCase().includes(busquedaDocente.toLowerCase())
  )

  const descargar = async (tipo, id, nombre) => {
    if (!periodoId) { setError('Selecciona un período primero'); return }
    setDescargando(`${tipo}-${id}`)
    setError('')
    try {
      let res
      if (tipo === 'carrera') res = await exportarExcelCarrera(id, periodoId)
      else if (tipo === 'docente') res = await exportarExcelDocente(id, periodoId)
      else if (tipo === 'nivel') res = await exportarExcelNivel(id, periodoId)

      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `reporte_${tipo}_${nombre}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      setExito(`Reporte descargado: ${nombre}`)
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Error al descargar el reporte')
    } finally {
      setDescargando('')
    }
  }

  const EsquemaReporte = () => (
    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 6 }}>
      {['Módulo 1', 'Módulo 2', 'Módulo 3', 'Carga por módulos', 'Carga total'].map(hoja => (
        <span key={hoja} style={{ background: '#f1f5f9', border: '1px solid #e2e8f0', borderRadius: 4, padding: '2px 8px', fontSize: 11, color: '#475569' }}>
          📄 {hoja}
        </span>
      ))}
    </div>
  )

  return (
    <>
      <div className="topbar">
        <div>
          <h1>📊 Reportes</h1>
          <p>Exportar horarios y cargas horarias</p>
        </div>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Filtros */}
      <div className="card" style={{ padding: 16, marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Período académico</label>
            <select value={periodoId} onChange={e => setPeriodoId(e.target.value)}>
              <option value="">Seleccionar período...</option>
              {periodos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Carrera</label>
            <select value={carreraId} onChange={e => { setCarreraId(e.target.value); setNivelId(''); setBusquedaDocente('') }}>
              <option value="">Seleccionar carrera...</option>
              {carreras
                .filter((c, idx, arr) => arr.findIndex(x => x.nombre.toLowerCase() === c.nombre.toLowerCase()) === idx)
                .map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>
        </div>
      </div>

      {!periodoId || !carreraId ? (
        <div className="card">
          <div className="empty-state">
            <p style={{ fontSize: 32 }}>📊</p>
            <p>Selecciona un período y una carrera para ver los reportes disponibles</p>
          </div>
        </div>
      ) : (
        <>
          {/* Reporte por Carrera */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 4 }}>🎓 Reporte por Carrera</h3>
                <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 6 }}>
                  {carreraSeleccionada?.nombre} — horarios completos y carga horaria
                </p>
                <EsquemaReporte />
              </div>
              <button
                className="btn btn-primary"
                onClick={() => descargar('carrera', carreraId, carreraSeleccionada?.codigo)}
                disabled={!!descargando}
                style={{ marginLeft: 16, whiteSpace: 'nowrap' }}
              >
                {descargando === `carrera-${carreraId}` ? '⏳ Descargando...' : '📥 Descargar Excel'}
              </button>
            </div>
          </div>

          {/* Reporte por Nivel */}
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>📚 Reporte por Nivel</h3>
            <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 12 }}>
              Horarios y carga horaria de un nivel específico
            </p>
            <EsquemaReporte />

            <div style={{ display: 'flex', gap: 8, margin: '16px 0', flexWrap: 'wrap' }}>
              {nivelesCarrera.map(n => (
                <button
                  key={n.id}
                  onClick={() => setNivelId(n.id)}
                  style={{
                    padding: '6px 14px', borderRadius: 20, border: '1.5px solid',
                    cursor: 'pointer', fontSize: 12, transition: 'all 0.2s',
                    borderColor: nivelId === n.id ? 'var(--rojo-itq)' : '#e5e7eb',
                    background: nivelId === n.id ? '#fee2e2' : '#fff',
                    color: nivelId === n.id ? 'var(--rojo-itq)' : '#6b7280',
                    fontWeight: nivelId === n.id ? 700 : 400,
                  }}
                >
                  {n.nombre || `Nivel ${n.numero}`}
                </button>
              ))}
            </div>

            {!nivelId ? (
              <p style={{ fontSize: 13, color: '#9ca3af', fontStyle: 'italic' }}>
                Selecciona un nivel para descargar su reporte
              </p>
            ) : (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc', padding: '12px 16px', borderRadius: 8 }}>
                <div>
                  <p style={{ fontWeight: 600, fontSize: 14 }}>{nivelSeleccionado?.nombre}</p>
                  <p style={{ fontSize: 12, color: '#6b7280' }}>{(nivelSeleccionado?.paralelos_matutina||0)}M / {(nivelSeleccionado?.paralelos_nocturna||0)}N paralelos</p>
                </div>
                <button
                  className="btn btn-success"
                  onClick={() => descargar('nivel', nivelId, `${carreraSeleccionada?.codigo}_nivel${nivelSeleccionado?.numero}`)}
                  disabled={!!descargando}
                >
                  {descargando === `nivel-${nivelId}` ? '⏳...' : '📥 Excel'}
                </button>
              </div>
            )}
          </div>

          {/* Reporte por Docente */}
          <div className="card">
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>👨‍🏫 Reporte por Docente</h3>
            <p style={{ fontSize: 13, color: '#6b7280', marginBottom: 12 }}>
              Horarios y carga horaria de un docente específico
            </p>
            <EsquemaReporte />

            <div className="form-group" style={{ margin: '16px 0' }}>
              <input
                placeholder="🔍 Buscar docente por nombre..."
                value={busquedaDocente}
                onChange={e => setBusquedaDocente(e.target.value)}
              />
            </div>

            {busquedaDocente.length < 2 ? (
              <p style={{ fontSize: 13, color: '#9ca3af', fontStyle: 'italic' }}>
                Escribe al menos 2 letras para buscar un docente
              </p>
            ) : docentesFiltrados.length === 0 ? (
              <p style={{ fontSize: 13, color: '#9ca3af' }}>No se encontró ningún docente con ese nombre</p>
            ) : (
              docentesFiltrados.map(d => (
                <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #f0f0f0' }}>
                  <div>
                    <p style={{ fontWeight: 600, fontSize: 14 }}>{d.nombre} {d.apellido}</p>
                    <p style={{ fontSize: 12, color: '#6b7280', display: 'flex', gap: 8, alignItems: 'center' }}>
                      <span className={`badge ${d.tipo === 'tiempo_completo' ? 'badge-blue' : 'badge-yellow'}`} style={{ fontSize: 11 }}>
                        {d.tipo === 'tiempo_completo' ? 'TC' : 'TP'}
                      </span>
                      {d.email}
                    </p>
                  </div>
                  <button
                    className="btn btn-success"
                    onClick={() => descargar('docente', d.id, `${d.nombre}_${d.apellido}`)}
                    disabled={!!descargando}
                  >
                    {descargando === `docente-${d.id}` ? '⏳...' : '📥 Excel'}
                  </button>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </>
  )
}