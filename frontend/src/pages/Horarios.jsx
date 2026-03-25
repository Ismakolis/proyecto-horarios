/**
 * Horarios.jsx
 * Gestion y visualizacion de horarios academicos por jornada.
 * Permite generar horarios automaticamente, editar manualmente y eliminar.
 */

import { useEffect, useState, useCallback } from 'react'
import {
  getHorarios, generarHorarios, deleteHorario,
  getCarreras, getPeriodos, exportarExcel,
  getDocentes, getAsignaturas, updateHorario
} from '../services/api'

// Dias de la semana disponibles para asignacion
const DIAS_OPTIONS = [
  { value: 'lunes',     label: 'Lunes' },
  { value: 'martes',    label: 'Martes' },
  { value: 'miercoles', label: 'Miercoles' },
  { value: 'jueves',    label: 'Jueves' },
  { value: 'viernes',   label: 'Viernes' },
]

// Slots de hora por jornada
const SLOTS_MATUTINA = ['08:00', '10:00']
const SLOTS_NOCTURNA = ['18:30', '20:00']
const HORAS_FIN_MATUTINA = { '08:00': '10:00', '10:00': '12:00' }
const HORAS_FIN_NOCTURNA = { '18:30': '20:00', '20:00': '21:30' }

/**
 * Componente que renderiza la tabla de horarios de una jornada especifica.
 * Muestra columnas: Modulo, Fecha inicio/fin, Asignatura, Nivel, Paralelo, Horario, Docente, Acciones.
 */
const TablaJornada = ({ jornada, titulo, horarioTxt, horarios, asignaturas, niveles, periodos, docentes, onEditar, onEliminar }) => {
  const items = horarios.filter(h => h.jornada === jornada)
  if (items.length === 0) return null

  // Helpers para obtener nombres desde IDs
  const getNombreAsignatura = (id) => asignaturas.find(a => a.id === id)?.nombre || '...'
  const getNivelNumero      = (id) => niveles.find(n => n.id === id)?.numero || ''
  const getNombreDocente    = (id) => {
    const d = docentes.find(d => d.id === id)
    return d ? `${d.nombre} ${d.apellido}`.toUpperCase() : '...'
  }
  const getModulo = (periodoId, moduloId) => {
    const p = periodos.find(p => p.id === periodoId)
    return p?.modulos?.find(m => m.id === moduloId) || null
  }

  const colorHeader = jornada === 'matutina' ? '#1e40af' : '#1a1a1a'

  return (
    <div style={{ marginBottom: 28 }}>
      {/* Cabecera de jornada */}
      <div style={{
        background: colorHeader,
        color: '#fff',
        padding: '10px 18px',
        borderRadius: '8px 8px 0 0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ fontWeight: 700, fontSize: 13 }}>{titulo}</span>
        <span style={{ fontSize: 12, opacity: 0.75 }}>{horarioTxt}</span>
      </div>

      {/* Tabla de datos */}
      <div style={{ overflowX: 'auto', border: '1px solid var(--gris-borde)', borderTop: 'none', borderRadius: '0 0 8px 8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead>
            <tr style={{ background: '#f8fafc' }}>
              {['Modulo', 'Fecha inicio', 'Fecha fin', 'Asignatura', 'Nivel', 'Paralelo', 'Horario', 'Docente', 'Acciones'].map((col, i) => (
                <th key={i} style={{ padding: '10px 14px', textAlign: 'left', fontWeight: 600, fontSize: 11.5, color: '#475569', borderBottom: '1px solid var(--gris-borde)', whiteSpace: 'nowrap' }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...items]
              .sort((a, b) => {
                const nA = getNivelNumero(a.nivel_id)
                const nB = getNivelNumero(b.nivel_id)
                if (nA !== nB) return nA - nB
                if (a.paralelo !== b.paralelo) return a.paralelo.localeCompare(b.paralelo)
                return a.hora_inicio.localeCompare(b.hora_inicio)
              })
              .map((h, idx) => {
                const modulo = getModulo(h.periodo_id, h.modulo_id)
                const par = idx % 2 === 0
                return (
                  <tr key={h.id} style={{ background: par ? '#fff' : '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: '#374151' }}>
                      {modulo?.nombre || 'Modulo'}
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--gris-medio)', fontSize: 12 }}>
                      {modulo?.fecha_inicio || '-'}
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--gris-medio)', fontSize: 12 }}>
                      {modulo?.fecha_fin || '-'}
                    </td>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: '#1e293b' }}>
                      {getNombreAsignatura(h.asignatura_id)}
                    </td>
                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                      <span className="badge badge-blue">{getNivelNumero(h.nivel_id)}</span>
                    </td>
                    <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                      <span className="badge badge-yellow">{h.paralelo}</span>
                    </td>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: '#374151', whiteSpace: 'nowrap' }}>
                      {h.hora_inicio} - {h.hora_fin}
                    </td>
                    <td style={{ padding: '10px 14px', color: '#374151' }}>
                      {getNombreDocente(h.docente_id)}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {/* Boton editar */}
                        <button
                          onClick={() => onEditar(h)}
                          style={{
                            background: 'var(--azul-claro)',
                            color: 'var(--azul)',
                            border: 'none',
                            borderRadius: 6,
                            padding: '4px 10px',
                            cursor: 'pointer',
                            fontSize: 12,
                            fontWeight: 600,
                          }}
                        >
                          Editar
                        </button>
                        {/* Boton eliminar */}
                        <button
                          onClick={() => onEliminar(h.id)}
                          style={{
                            background: 'var(--rojo-claro)',
                            color: 'var(--rojo-itq)',
                            border: 'none',
                            borderRadius: 6,
                            padding: '4px 10px',
                            cursor: 'pointer',
                            fontSize: 12,
                            fontWeight: 600,
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function Horarios() {
  // Datos del sistema
  const [horarios, setHorarios]         = useState([])
  const [carreras, setCarreras]         = useState([])
  const [periodos, setPeriodos]         = useState([])
  const [docentes, setDocentes]         = useState([])
  const [asignaturas, setAsignaturas]   = useState([])
  const [niveles, setNiveles]           = useState([])

  // Estado de UI
  const [cargando, setCargando]         = useState(true)
  const [generando, setGenerando]       = useState(false)
  const [error, setError]               = useState('')
  const [exito, setExito]               = useState('')
  const [resultado, setResultado]       = useState(null)

  // Filtros de visualizacion
  const [filtros, setFiltros]           = useState({ periodo_id: '', modulo_id: '', carrera_id: '' })
  const [modulosFiltro, setModulosFiltro] = useState([])

  // Modales
  const [modalGenerar, setModalGenerar] = useState(false)
  const [modalEditar, setModalEditar]   = useState(false)
  const [horarioEditando, setHorarioEditando] = useState(null)

  // Formulario de generacion
  const [formGenerar, setFormGenerar]   = useState({ periodo_id: '', modulo_id: '', carrera_id: '' })
  const [modulosGenerar, setModulosGenerar] = useState([])

  // Formulario de edicion manual
  const [formEditar, setFormEditar] = useState({
    docente_id: '',
    dia: '',
    jornada: '',
    hora_inicio: '',
    hora_fin: '',
    observaciones: '',
  })
  const [guardandoEdicion, setGuardandoEdicion] = useState(false)

  /**
   * Carga catalogos de datos necesarios para mostrar nombres en las tablas.
   */
  const cargarDatos = async () => {
    try {
      const [c, p, d, a] = await Promise.all([
        getCarreras(), getPeriodos(), getDocentes(), getAsignaturas()
      ])
      setCarreras(c.data)
      setPeriodos(p.data)
      setDocentes(d.data)
      setAsignaturas(a.data)
      setNiveles(c.data.flatMap(car => car.niveles || []))
    } catch {
      setError('Error al cargar datos del sistema')
    }
  }

  /**
   * Carga los horarios segun los filtros activos.
   */
  const cargarHorarios = useCallback(async () => {
    setCargando(true)
    try {
      const params = {}
      if (filtros.periodo_id) params.periodo_id = filtros.periodo_id
      if (filtros.modulo_id)  params.modulo_id  = filtros.modulo_id
      if (filtros.carrera_id) params.carrera_id = filtros.carrera_id
      const res = await getHorarios(params)
      setHorarios(res.data)
    } catch {
      setError('Error al cargar horarios')
    } finally {
      setCargando(false)
    }
  }, [filtros])

  useEffect(() => { cargarDatos() }, [])
  useEffect(() => { cargarHorarios() }, [cargarHorarios])

  /**
   * Actualiza modulos disponibles al cambiar el periodo en el filtro.
   */
  const onCambioPeriodoFiltro = (periodoId) => {
    const periodo = periodos.find(p => p.id === periodoId)
    setModulosFiltro(periodo?.modulos || [])
    setFiltros({ ...filtros, periodo_id: periodoId, modulo_id: '' })
  }

  /**
   * Actualiza modulos disponibles al cambiar el periodo en el formulario de generacion.
   */
  const onCambioPeriodoGenerar = (periodoId) => {
    const periodo = periodos.find(p => p.id === periodoId)
    setModulosGenerar(periodo?.modulos || [])
    setFormGenerar({ ...formGenerar, periodo_id: periodoId, modulo_id: '' })
  }

  /**
   * Ejecuta la generacion automatica de horarios con validaciones activas.
   */
  const ejecutarGeneracion = async () => {
    if (!formGenerar.periodo_id || !formGenerar.modulo_id || !formGenerar.carrera_id) {
      setError('Selecciona periodo, modulo y carrera')
      return
    }
    setGenerando(true)
    setError('')
    try {
      const res = await generarHorarios({
        periodo_id: formGenerar.periodo_id,
        modulo_id:  formGenerar.modulo_id,
        carrera_id: formGenerar.carrera_id,
        usar_ia: false,
      })
      setResultado(res.data)
      cargarHorarios()
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al generar horarios')
    } finally {
      setGenerando(false)
    }
  }

  /**
   * Elimina un horario individual tras confirmacion del usuario.
   */
  const eliminar = async (id) => {
    if (!confirm('Eliminar este horario?')) return
    try {
      await deleteHorario(id)
      setExito('Horario eliminado correctamente')
      cargarHorarios()
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Error al eliminar el horario')
    }
  }

  /**
   * Elimina todos los horarios del modulo seleccionado.
   */
  const limpiarModulo = async () => {
    if (!filtros.modulo_id) { setError('Selecciona un modulo para limpiar'); return }
    if (!confirm('Eliminar TODOS los horarios de este modulo?')) return
    try {
      const horariosModulo = horarios.filter(h => h.modulo_id === filtros.modulo_id)
      await Promise.all(horariosModulo.map(h => deleteHorario(h.id)))
      setExito(`${horariosModulo.length} horarios eliminados`)
      cargarHorarios()
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Error al limpiar el modulo')
    }
  }

  /**
   * Descarga el reporte Excel del periodo seleccionado.
   */
  const descargarExcel = async () => {
    if (!filtros.periodo_id) { setError('Selecciona un periodo para exportar'); return }
    try {
      const res = await exportarExcel(filtros.periodo_id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `horarios_${filtros.periodo_id}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      setExito('Reporte Excel descargado')
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Selecciona un periodo primero')
    }
  }

  /**
   * Abre el modal de edicion con los datos del horario seleccionado.
   */
  const abrirEditar = (horario) => {
    setHorarioEditando(horario)
    setFormEditar({
      docente_id:    horario.docente_id,
      dia:           horario.dia,
      jornada:       horario.jornada,
      hora_inicio:   horario.hora_inicio,
      hora_fin:      horario.hora_fin,
      observaciones: horario.observaciones || '',
    })
    setError('')
    setModalEditar(true)
  }

  /**
   * Actualiza la hora_fin automaticamente al cambiar la hora_inicio segun la jornada.
   */
  const onCambioHoraInicio = (horaInicio) => {
    const jornada = formEditar.jornada
    let horaFin = ''
    if (jornada === 'matutina') horaFin = HORAS_FIN_MATUTINA[horaInicio] || ''
    if (jornada === 'nocturna') horaFin = HORAS_FIN_NOCTURNA[horaInicio] || ''
    setFormEditar({ ...formEditar, hora_inicio: horaInicio, hora_fin: horaFin })
  }

  /**
   * Guarda los cambios del horario editado con validaciones activas en el backend.
   */
  const guardarEdicion = async () => {
    if (!formEditar.docente_id || !formEditar.dia || !formEditar.hora_inicio) {
      setError('Docente, dia y hora son obligatorios')
      return
    }
    setGuardandoEdicion(true)
    setError('')
    try {
      await updateHorario(horarioEditando.id, {
        docente_id:    formEditar.docente_id,
        dia:           formEditar.dia,
        jornada:       formEditar.jornada,
        hora_inicio:   formEditar.hora_inicio,
        hora_fin:      formEditar.hora_fin,
        observaciones: formEditar.observaciones,
      })
      setExito('Horario actualizado correctamente')
      setModalEditar(false)
      cargarHorarios()
      setTimeout(() => setExito(''), 3000)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail.map(e => e.msg).join(', ') : (detail || 'Error al guardar'))
    } finally {
      setGuardandoEdicion(false)
    }
  }

  // Helpers de display
  const getSlots = (jornada) => jornada === 'matutina' ? SLOTS_MATUTINA : SLOTS_NOCTURNA
  const propsTabla = { horarios, asignaturas, carreras, niveles, periodos, docentes, onEditar: abrirEditar, onEliminar: eliminar }

  return (
    <>
      {/* Encabezado */}
      <div className="topbar">
        <div>
          <h1>Horarios Academicos</h1>
          <p>Planificacion por modulo y jornada</p>
        </div>
        <div className="topbar-actions">
          {filtros.modulo_id && (
            <button className="btn btn-danger" onClick={limpiarModulo}>
              Limpiar modulo
            </button>
          )}
          <button className="btn btn-success" onClick={descargarExcel}>
            Exportar Excel
          </button>
          <button className="btn btn-primary" onClick={() => { setResultado(null); setError(''); setModalGenerar(true) }}>
            Generar horarios
          </button>
        </div>
      </div>

      {/* Alertas */}
      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modalGenerar && !modalEditar && <div className="alert alert-error">{error}</div>}

      {/* Filtros */}
      <div className="card" style={{ padding: 16, marginBottom: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Periodo academico</label>
            <select value={filtros.periodo_id} onChange={e => onCambioPeriodoFiltro(e.target.value)}>
              <option value="">Todos los periodos</option>
              {periodos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Modulo</label>
            <select
              value={filtros.modulo_id}
              onChange={e => setFiltros({ ...filtros, modulo_id: e.target.value })}
              disabled={!filtros.periodo_id}
            >
              <option value="">Todos los modulos</option>
              {modulosFiltro.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>Carrera</label>
            <select value={filtros.carrera_id} onChange={e => setFiltros({ ...filtros, carrera_id: e.target.value })}>
              <option value="">Todas las carreras</option>
              {carreras.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      {cargando ? (
        <div className="loading">Cargando horarios...</div>
      ) : horarios.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p>No hay horarios generados aun.</p>
            <small>Usa "Generar horarios" para comenzar la planificacion.</small>
          </div>
        </div>
      ) : (
        <div className="card">
          {/* Info de carrera y periodo seleccionados */}
          {filtros.carrera_id && (
            <div style={{ marginBottom: 20, paddingBottom: 16, borderBottom: '1px solid var(--gris-borde)' }}>
              <p style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>
                {carreras.find(c => c.id === filtros.carrera_id)?.nombre || '...'}
              </p>
              <p style={{ fontSize: 12, color: 'var(--gris-medio)', marginTop: 2 }}>
                {periodos.find(p => p.id === filtros.periodo_id)?.nombre || 'Todos los periodos'}
                {filtros.modulo_id && ` — ${modulosFiltro.find(m => m.id === filtros.modulo_id)?.nombre}`}
              </p>
            </div>
          )}

          <p style={{ fontSize: 13, color: 'var(--gris-medio)', marginBottom: 20 }}>
            {horarios.length} horario(s) encontrado(s)
          </p>

          {/* Tablas por jornada */}
          <TablaJornada
            jornada="matutina"
            titulo="MODALIDAD PRESENCIAL — MATUTINO (LUNES A VIERNES)"
            horarioTxt="08:00 - 12:00"
            {...propsTabla}
          />
          <TablaJornada
            jornada="nocturna"
            titulo="MODALIDAD PRESENCIAL — NOCTURNO (LUNES A VIERNES)"
            horarioTxt="18:30 - 21:30"
            {...propsTabla}
          />
        </div>
      )}

      {/* ============================================================
          MODAL: Generar horarios automaticamente
          ============================================================ */}
      {modalGenerar && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalGenerar(false)}>
          <div className="modal">
            <div className="modal-header">
              <h2>Generar horarios automaticamente</h2>
              <button className="modal-close" onClick={() => setModalGenerar(false)}>x</button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {resultado ? (
              /* Resultado de la generacion */
              <>
                <div className={`alert ${resultado.errores?.length === 0 ? 'alert-success' : 'alert-warning'}`}>
                  {resultado.mensaje}
                </div>
                {resultado.errores?.length > 0 && (
                  <div style={{ marginTop: 12 }}>
                    <p style={{ fontWeight: 700, fontSize: 13, marginBottom: 8 }}>Advertencias:</p>
                    {resultado.errores.map((e, i) => (
                      <p key={i} style={{ fontSize: 12, color: '#92400e', marginBottom: 4 }}>- {e}</p>
                    ))}
                  </div>
                )}
                <div className="modal-footer">
                  <button className="btn btn-primary" onClick={() => setModalGenerar(false)}>Cerrar</button>
                </div>
              </>
            ) : (
              /* Formulario de generacion */
              <>
                <p style={{ fontSize: 13, color: 'var(--gris-medio)', marginBottom: 16 }}>
                  El sistema asignara docentes automaticamente respetando todas las reglas de negocio:
                  maximo 3 asignaturas por docente, sin choques de horario, carga horaria TC valida.
                </p>
                <div className="form-group">
                  <label>Periodo academico</label>
                  <select value={formGenerar.periodo_id} onChange={e => onCambioPeriodoGenerar(e.target.value)}>
                    <option value="">Seleccionar periodo...</option>
                    {periodos.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Modulo</label>
                  <select
                    value={formGenerar.modulo_id}
                    onChange={e => setFormGenerar({ ...formGenerar, modulo_id: e.target.value })}
                    disabled={!formGenerar.periodo_id}
                  >
                    <option value="">Seleccionar modulo...</option>
                    {modulosGenerar.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Carrera</label>
                  <select value={formGenerar.carrera_id} onChange={e => setFormGenerar({ ...formGenerar, carrera_id: e.target.value })}>
                    <option value="">Seleccionar carrera...</option>
                    {carreras.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                  </select>
                </div>
                <div className="alert alert-warning">
                  Se generaran horarios para todas las asignaturas del modulo seleccionado.
                  Si ya existen horarios previos, pueden generarse conflictos.
                </div>
                <div className="modal-footer">
                  <button className="btn btn-secondary" onClick={() => setModalGenerar(false)}>Cancelar</button>
                  <button className="btn btn-primary" onClick={ejecutarGeneracion} disabled={generando}>
                    {generando ? 'Generando...' : 'Generar horarios'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ============================================================
          MODAL: Edicion manual de horario con validaciones activas
          ============================================================ */}
      {modalEditar && horarioEditando && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalEditar(false)}>
          <div className="modal">
            <div className="modal-header">
              <h2>Editar horario</h2>
              <button className="modal-close" onClick={() => setModalEditar(false)}>x</button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Informacion del horario (solo lectura) */}
            <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 13, color: 'var(--gris-oscuro)' }}>
              <p><strong>Asignatura:</strong> {asignaturas.find(a => a.id === horarioEditando.asignatura_id)?.nombre}</p>
              <p style={{ marginTop: 4 }}><strong>Nivel:</strong> {niveles.find(n => n.id === horarioEditando.nivel_id)?.nombre} — <strong>Paralelo:</strong> {horarioEditando.paralelo}</p>
            </div>

            {/* Docente */}
            <div className="form-group">
              <label>Docente asignado</label>
              <select value={formEditar.docente_id} onChange={e => setFormEditar({ ...formEditar, docente_id: e.target.value })}>
                <option value="">Seleccionar docente...</option>
                {docentes.filter(d => d.activo).map(d => (
                  <option key={d.id} value={d.id}>{d.nombre} {d.apellido}</option>
                ))}
              </select>
            </div>

            <div className="form-row">
              {/* Dia */}
              <div className="form-group">
                <label>Dia de la semana</label>
                <select value={formEditar.dia} onChange={e => setFormEditar({ ...formEditar, dia: e.target.value })}>
                  <option value="">Seleccionar dia...</option>
                  {DIAS_OPTIONS.map(d => (
                    <option key={d.value} value={d.value}>{d.label}</option>
                  ))}
                </select>
              </div>

              {/* Jornada */}
              <div className="form-group">
                <label>Jornada</label>
                <select
                  value={formEditar.jornada}
                  onChange={e => setFormEditar({ ...formEditar, jornada: e.target.value, hora_inicio: '', hora_fin: '' })}
                >
                  <option value="">Seleccionar jornada...</option>
                  <option value="matutina">Matutina (08:00 - 12:00)</option>
                  <option value="nocturna">Nocturna (18:30 - 21:30)</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              {/* Hora inicio */}
              <div className="form-group">
                <label>Hora de inicio</label>
                <select
                  value={formEditar.hora_inicio}
                  onChange={e => onCambioHoraInicio(e.target.value)}
                  disabled={!formEditar.jornada}
                >
                  <option value="">Seleccionar hora...</option>
                  {getSlots(formEditar.jornada).map(slot => (
                    <option key={slot} value={slot}>{slot}</option>
                  ))}
                </select>
              </div>

              {/* Hora fin (calculada automaticamente) */}
              <div className="form-group">
                <label>Hora de fin</label>
                <input
                  value={formEditar.hora_fin}
                  readOnly
                  style={{ background: '#f9fafb', color: 'var(--gris-medio)' }}
                  placeholder="Se calcula automaticamente"
                />
              </div>
            </div>

            {/* Observaciones */}
            <div className="form-group">
              <label>Observaciones (opcional)</label>
              <input
                value={formEditar.observaciones}
                onChange={e => setFormEditar({ ...formEditar, observaciones: e.target.value })}
                placeholder="Ej: Cambio por solicitud del docente"
              />
            </div>

            <div className="alert alert-info" style={{ fontSize: 12 }}>
              El sistema validara que no existan choques de horario ni se supere el maximo de asignaturas por docente.
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModalEditar(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={guardarEdicion} disabled={guardandoEdicion}>
                {guardandoEdicion ? 'Guardando...' : 'Guardar cambios'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}