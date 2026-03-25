import { useEffect, useState } from 'react'
import { getPeriodos, createPeriodo, updatePeriodo } from '../services/api'

const formInicial = {
  nombre: '', anio: new Date().getFullYear(), numero: 1,
  fecha_inicio: '', fecha_fin: '', paralelos_por_nivel: 1,
  modulos: [
    { numero: 1, nombre: 'Módulo 1', fecha_inicio: '', fecha_fin: '' },
    { numero: 2, nombre: 'Módulo 2', fecha_inicio: '', fecha_fin: '' },
    { numero: 3, nombre: 'Módulo 3', fecha_inicio: '', fecha_fin: '' },
  ]
}

export default function Periodos() {
  const [periodos, setPeriodos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [modal, setModal] = useState(false)
  const [editando, setEditando] = useState(null)
  const [form, setForm] = useState(formInicial)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [guardando, setGuardando] = useState(false)

  const cargar = async () => {
    try {
      const res = await getPeriodos()
      setPeriodos(res.data)
    } catch {
      setError('Error al cargar períodos')
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

  const guardar = async () => {
    setGuardando(true)
    setError('')
    try {
      if (editando) {
        await updatePeriodo(editando.id, {
          nombre: form.nombre,
          paralelos_por_nivel: parseInt(form.paralelos_por_nivel),
        })
      } else {
        await createPeriodo({
          ...form,
          anio: parseInt(form.anio),
          numero: parseInt(form.numero),
          paralelos_por_nivel: parseInt(form.paralelos_por_nivel),
        })
      }
      setExito(editando ? 'Período actualizado' : 'Período creado correctamente')
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
          <h1>📅 Períodos Académicos</h1>
          <p>Gestión de períodos y módulos</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nuevo período</button>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modal && <div className="alert alert-error">{error}</div>}

      <div className="card">
        {cargando ? (
          <div className="loading">Cargando períodos...</div>
        ) : periodos.length === 0 ? (
          <div className="empty-state"><p>No hay períodos registrados aún.</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Año</th>
                  <th>Número</th>
                  <th>Paralelos</th>
                  <th>Módulos</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {periodos.map(p => (
                  <tr key={p.id}>
                    <td><strong>{p.nombre}</strong></td>
                    <td>{p.anio}</td>
                    <td>
                      <span className="badge badge-blue">Período {p.numero}</span>
                    </td>
                    <td>{p.paralelos_por_nivel} paralelo(s)</td>
                    <td>{p.modulos?.length || 0} módulos</td>
                    <td>
                      <span className={`badge ${p.activo ? 'badge-green' : 'badge-red'}`}>
                        {p.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-secondary" onClick={() => abrirEditar(p)}>
                        ✏️ Editar
                      </button>
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
              <h2>{editando ? 'Editar período' : 'Nuevo período académico'}</h2>
              <button className="modal-close" onClick={() => setModal(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre</label>
                <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} placeholder="2025-I" />
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
                    <label>Año</label>
                    <input type="number" value={form.anio} onChange={e => setForm({...form, anio: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Número de período</label>
                    <select value={form.numero} onChange={e => setForm({...form, numero: e.target.value})}>
                      <option value={1}>Período 1</option>
                      <option value={2}>Período 2</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Fecha inicio</label>
                    <input type="date" value={form.fecha_inicio} onChange={e => setForm({...form, fecha_inicio: e.target.value})} />
                  </div>
                  <div className="form-group">
                    <label>Fecha fin</label>
                    <input type="date" value={form.fecha_fin} onChange={e => setForm({...form, fecha_fin: e.target.value})} />
                  </div>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <p style={{ fontWeight: 700, fontSize: 14, marginBottom: 12 }}>📦 Módulos</p>
                  {form.modulos.map((mod, idx) => (
                    <div key={idx} style={{ background: '#f9fafb', borderRadius: 8, padding: 12, marginBottom: 10 }}>
                      <p style={{ fontWeight: 600, fontSize: 13, marginBottom: 8, color: 'var(--rojo-itq)' }}>
                        {mod.nombre}
                      </p>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Fecha inicio</label>
                          <input type="date" value={mod.fecha_inicio} onChange={e => updateModulo(idx, 'fecha_inicio', e.target.value)} />
                        </div>
                        <div className="form-group">
                          <label>Fecha fin</label>
                          <input type="date" value={mod.fecha_fin} onChange={e => updateModulo(idx, 'fecha_fin', e.target.value)} />
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