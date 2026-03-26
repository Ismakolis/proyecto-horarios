/**
 * Periodos.jsx
 * Gestion de periodos academicos y modulos.
 * Incluye validaciones de fechas y campos requeridos antes de enviar al backend.
 */

import { useEffect, useState } from 'react'
import { getPeriodos, createPeriodo, updatePeriodo } from '../services/api'

const formInicial = {
  nombre: '', anio: new Date().getFullYear(), numero: 1,
  fecha_inicio: '', fecha_fin: '', paralelos_por_nivel: 1,
  modulos: [
    { numero: 1, nombre: 'Modulo 1', fecha_inicio: '', fecha_fin: '' },
    { numero: 2, nombre: 'Modulo 2', fecha_inicio: '', fecha_fin: '' },
    { numero: 3, nombre: 'Modulo 3', fecha_inicio: '', fecha_fin: '' },
  ]
}

export default function Periodos() {
  const [periodos, setPeriodos]   = useState([])
  const [cargando, setCargando]   = useState(true)
  const [modal, setModal]         = useState(false)
  const [editando, setEditando]   = useState(null)
  const [form, setForm]           = useState(formInicial)
  const [error, setError]         = useState('')
  const [exito, setExito]         = useState('')
  const [guardando, setGuardando] = useState(false)

  const cargar = async () => {
    try {
      const res = await getPeriodos()
      setPeriodos(res.data)
    } catch {
      setError('Error al cargar periodos')
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => { cargar() }, [])

  const abrirCrear = () => {
    setEditando(null)
    setForm(formInicial)
    setError('')
    setModal(true)
  }

  const abrirEditar = (periodo) => {
    setEditando(periodo)
    setForm({
      nombre: periodo.nombre,
      anio: periodo.anio,
      numero: periodo.numero,
      fecha_inicio: periodo.fecha_inicio,
      fecha_fin: periodo.fecha_fin,
      paralelos_por_nivel: periodo.paralelos_por_nivel,
      modulos: []
    })
    setError('')
    setModal(true)
  }

  const updateModulo = (idx, campo, valor) => {
    const mods = [...form.modulos]
    mods[idx] = { ...mods[idx], [campo]: valor }
    setForm({ ...form, modulos: mods })
  }

  // Validacion antes de enviar
  const validar = () => {
    if (!form.nombre.trim()) return 'El nombre del periodo es obligatorio'
    if (form.nombre.trim().length < 3) return 'El nombre debe tener al menos 3 caracteres'

    if (!editando) {
      const anio = parseInt(form.anio)
      if (isNaN(anio) || anio < 2000 || anio > 2100) return 'El año debe estar entre 2000 y 2100'
      if (!form.fecha_inicio) return 'La fecha de inicio del periodo es obligatoria'
      if (!form.fecha_fin) return 'La fecha de fin del periodo es obligatoria'
      if (new Date(form.fecha_fin) <= new Date(form.fecha_inicio)) {
        return 'La fecha de fin del periodo debe ser posterior a la fecha de inicio'
      }

      // Validar cada modulo
      for (let i = 0; i < form.modulos.length; i++) {
        const mod = form.modulos[i]
        if (!mod.fecha_inicio) return `Modulo ${i + 1}: la fecha de inicio es obligatoria`
        if (!mod.fecha_fin) return `Modulo ${i + 1}: la fecha de fin es obligatoria`
        if (new Date(mod.fecha_fin) <= new Date(mod.fecha_inicio)) {
          return `Modulo ${i + 1}: la fecha de fin debe ser posterior a la fecha de inicio`
        }
      }
    }

    return null
  }

  const guardar = async () => {
    const errValidacion = validar()
    if (errValidacion) { setError(errValidacion); return }

    setGuardando(true)
    setError('')
    try {
      if (editando) {
        await updatePeriodo(editando.id, {
          nombre: form.nombre.trim(),
          paralelos_por_nivel: parseInt(form.paralelos_por_nivel),
        })
      } else {
        await createPeriodo({
          ...form,
          nombre: form.nombre.trim(),
          anio: parseInt(form.anio),
          numero: parseInt(form.numero),
          paralelos_por_nivel: parseInt(form.paralelos_por_nivel),
        })
      }
      setExito(editando ? 'Periodo actualizado' : 'Periodo creado correctamente')
      setModal(false)
      cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar')
    } finally {
      setGuardando(false)
    }
  }

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Periodos Academicos</h1>
          <p>Gestion de periodos y modulos</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nuevo periodo</button>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modal && <div className="alert alert-error">{error}</div>}

      <div className="card">
        {cargando ? (
          <div className="loading">Cargando periodos...</div>
        ) : periodos.length === 0 ? (
          <div className="empty-state"><p>No hay periodos registrados aun.</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Año</th>
                  <th>Numero</th>
                  <th>Paralelos</th>
                  <th>Modulos</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {periodos.map(p => (
                  <tr key={p.id}>
                    <td><strong>{p.nombre}</strong></td>
                    <td>{p.anio}</td>
                    <td><span className="badge badge-blue">Periodo {p.numero}</span></td>
                    <td>{p.paralelos_por_nivel} paralelo(s)</td>
                    <td>{p.modulos?.length || 0} modulos</td>
                    <td>
                      <span className={`badge ${p.activo ? 'badge-green' : 'badge-red'}`}>
                        {p.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-secondary" onClick={() => abrirEditar(p)}>Editar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
          <div className="modal" style={{ maxWidth: 580 }}>
            <div className="modal-header">
              <h2>{editando ? 'Editar periodo' : 'Nuevo periodo academico'}</h2>
              <button className="modal-close" onClick={() => setModal(false)}>x</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre * (ej: 2025-I)</label>
                <input
                  value={form.nombre}
                  onChange={e => setForm({...form, nombre: e.target.value})}
                  placeholder="2025-I"
                  maxLength={100}
                />
              </div>
              <div className="form-group">
                <label>Paralelos por nivel</label>
                <select value={form.paralelos_por_nivel} onChange={e => setForm({...form, paralelos_por_nivel: e.target.value})}>
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
            </div>

            {!editando && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label>Año *</label>
                    <input
                      type="number"
                      value={form.anio}
                      onChange={e => setForm({...form, anio: e.target.value})}
                      min={2000}
                      max={2100}
                    />
                  </div>
                  <div className="form-group">
                    <label>Numero de periodo *</label>
                    <select value={form.numero} onChange={e => setForm({...form, numero: e.target.value})}>
                      <option value={1}>Periodo 1</option>
                      <option value={2}>Periodo 2</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Fecha inicio *</label>
                    <input type="date" value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Fecha fin *</label>
                    <input
                      type="date"
                      value={form.fecha_fin}
                      min={form.fecha_inicio || undefined}
                      onChange={e => setForm({...form, fecha_fin: e.target.value})}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <p style={{ fontWeight: 700, fontSize: 14, marginBottom: 12 }}>Modulos</p>
                  {form.modulos.map((mod, idx) => (
                    <div key={idx} style={{ background: '#f9fafb', borderRadius: 8, padding: 12, marginBottom: 10 }}>
                      <p style={{ fontWeight: 600, fontSize: 13, marginBottom: 8, color: 'var(--rojo-itq)' }}>
                        {mod.nombre}
                      </p>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Fecha inicio *</label>
                          <input
                            type="date"
                            value={mod.fecha_inicio}
                            onChange={e => updateModulo(idx, 'fecha_inicio', e.target.value)}
                          />
                        </div>
                        <div className="form-group">
                          <label>Fecha fin *</label>
                          <input
                            type="date"
                            value={mod.fecha_fin}
                            min={mod.fecha_inicio || undefined}
                            onChange={e => updateModulo(idx, 'fecha_fin', e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModal(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={guardar} disabled={guardando}>
                {guardando ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
