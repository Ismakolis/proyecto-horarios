/**
 * Carreras.jsx
 * Gestion de carreras, niveles, paralelos por jornada y sede.
 */
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCarreras, createCarrera, updateCarrera, updateNivel } from '../services/api'

const formInicial = {
  nombre: '', codigo: '', sede: 'Quito', descripcion: '',
  niveles: Array.from({ length: 5 }, (_, i) => ({
    numero: i + 1,
    nombre: `Nivel ${i + 1}`,
    paralelos_matutina: 1,
    paralelos_nocturna: 1,
    jornada_habilitada: 'ambas',
  }))
}

export default function Carreras() {
  const [carreras, setCarreras]             = useState([])
  const [cargando, setCargando]             = useState(true)
  const [modal, setModal]                   = useState(false)
  const [modalNivel, setModalNivel]         = useState(false)
  const [editando, setEditando]             = useState(null)
  const [nivelEditando, setNivelEditando]   = useState(null)
  const [form, setForm]                     = useState(formInicial)
  const [formNivel, setFormNivel]           = useState({ paralelos_matutina: 1, paralelos_nocturna: 1, jornada_habilitada: 'ambas' })
  const [error, setError]                   = useState('')
  const [exito, setExito]                   = useState('')
  const [guardando, setGuardando]           = useState(false)
  const [carreraExpandida, setCarreraExpandida] = useState(null)
  const navigate = useNavigate()

  const cargar = async () => {
    try {
      const res = await getCarreras()
      setCarreras(res.data)
    } catch { setError('Error al cargar carreras') }
    finally { setCargando(false) }
  }

  useEffect(() => { cargar() }, [])

  const abrirCrear = () => {
    setEditando(null); setForm(formInicial); setError(''); setModal(true)
  }

  const abrirEditar = (carrera) => {
    setEditando(carrera)
    setForm({ nombre: carrera.nombre, codigo: carrera.codigo, sede: carrera.sede || 'Quito', descripcion: carrera.descripcion || '', niveles: [] })
    setError(''); setModal(true)
  }

  const abrirEditarNivel = (carrera, nivel) => {
    setNivelEditando({ carrera, nivel })
    setFormNivel({ paralelos_matutina: nivel.paralelos_matutina, paralelos_nocturna: nivel.paralelos_nocturna, jornada_habilitada: nivel.jornada_habilitada || 'ambas' })
    setError(''); setModalNivel(true)
  }

  const validar = () => {
    if (!form.nombre.trim()) return 'El nombre es obligatorio'
    if (form.nombre.trim().length < 3) return 'El nombre debe tener al menos 3 caracteres'
    if (!form.codigo.trim()) return 'El codigo es obligatorio'
    return null
  }

  const guardar = async () => {
    const err = validar()
    if (err) { setError(err); return }
    setGuardando(true); setError('')
    try {
      if (editando) {
        await updateCarrera(editando.id, { nombre: form.nombre.trim(), sede: form.sede, descripcion: form.descripcion.trim() || null })
      } else {
        await createCarrera({ nombre: form.nombre.trim(), codigo: form.codigo.trim().toUpperCase(), sede: form.sede, descripcion: form.descripcion.trim() || null, niveles: form.niveles })
      }
      setExito(editando ? 'Carrera actualizada' : 'Carrera creada correctamente')
      setModal(false); cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al guardar')
    } finally { setGuardando(false) }
  }

  const guardarNivel = async () => {
    setGuardando(true); setError('')
    try {
      await updateNivel(nivelEditando.carrera.id, nivelEditando.nivel.id, {
        paralelos_matutina: parseInt(formNivel.paralelos_matutina),
        paralelos_nocturna: parseInt(formNivel.paralelos_nocturna),
        jornada_habilitada: formNivel.jornada_habilitada,
      })
      setExito('Nivel actualizado')
      setModalNivel(false); cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al guardar')
    } finally { setGuardando(false) }
  }

  const updateNivelForm = (idx, campo, valor) => {
    const niveles = [...form.niveles]
    niveles[idx] = { ...niveles[idx], [campo]: campo.includes('paralelos') ? (parseInt(valor) || 0) : valor }
    setForm({ ...form, niveles })
  }

  const jornadaLabel = (j) => j === 'matutina' ? 'Solo Manana' : j === 'nocturna' ? 'Solo Noche' : 'Manana y Noche'
  const jornadaStyle = (j) => ({
    bg: j === 'matutina' ? 'var(--azul-claro)' : j === 'nocturna' ? 'var(--violeta-claro)' : 'var(--verde-claro)',
    color: j === 'matutina' ? 'var(--azul)' : j === 'nocturna' ? 'var(--violeta)' : 'var(--verde)',
  })

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Carreras</h1>
          <p>Gestion de carreras, niveles, paralelos y jornadas</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nueva carrera</button>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modal && !modalNivel && <div className="alert alert-error">{error}</div>}

      {cargando ? (
        <div className="loading">Cargando carreras...</div>
      ) : carreras.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon">🎓</div>
            <p>No hay carreras registradas</p>
            <small>Crea la primera carrera para empezar</small>
          </div>
        </div>
      ) : (
        <div>
          {carreras.map(carrera => (
            <div key={carrera.id} className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 16 }}>

              {/* Header carrera */}
              <div
                style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: carreraExpandida === carrera.id ? '1px solid var(--gris-borde)' : 'none', cursor: 'pointer' }}
                onClick={() => setCarreraExpandida(carreraExpandida === carrera.id ? null : carrera.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{ width: 42, height: 42, borderRadius: 10, background: 'var(--rojo-claro)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 12, color: 'var(--rojo-itq)', flexShrink: 0 }}>
                    {carrera.codigo}
                  </div>
                  <div>
                    <p style={{ fontWeight: 700, fontSize: 15, color: 'var(--negro)' }}>{carrera.nombre}</p>
                    <div style={{ display: 'flex', gap: 6, marginTop: 4, alignItems: 'center' }}>
                      <span className="badge badge-gray" style={{ fontSize: 10 }}>{carrera.sede || 'Quito'}</span>
                      <span className="badge badge-gray" style={{ fontSize: 10 }}>{carrera.niveles?.length || 0} niveles</span>
                      <span className={`badge ${carrera.activo ? 'badge-green' : 'badge-red'}`} style={{ fontSize: 10 }}>
                        {carrera.activo ? 'Activa' : 'Inactiva'}
                      </span>
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <button className="btn btn-secondary btn-sm" onClick={e => { e.stopPropagation(); navigate('/asignaturas', { state: { carreraId: carrera.id } }) }}>
                    Malla curricular
                  </button>
                  <button className="btn btn-ghost btn-sm" onClick={e => { e.stopPropagation(); abrirEditar(carrera) }}>
                    Editar
                  </button>
                  <span style={{ color: 'var(--gris-medio)', fontSize: 16 }}>
                    {carreraExpandida === carrera.id ? '▲' : '▼'}
                  </span>
                </div>
              </div>

              {/* Niveles expandidos */}
              {carreraExpandida === carrera.id && (
                <div style={{ padding: '16px 20px' }}>
                  <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--gris-medio)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Configuracion por nivel
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))', gap: 10 }}>
                    {carrera.niveles?.slice().sort((a, b) => a.numero - b.numero).map(nivel => {
                      const js = jornadaStyle(nivel.jornada_habilitada)
                      return (
                        <div key={nivel.id} style={{ border: '1px solid var(--gris-borde)', borderRadius: 10, padding: '12px 14px', background: 'var(--gris-claro)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                            <span style={{ fontWeight: 700, fontSize: 13, color: 'var(--negro)' }}>
                              {nivel.nombre || `Nivel ${nivel.numero}`}
                            </span>
                            <button className="btn btn-ghost btn-sm" style={{ padding: '2px 8px', fontSize: 11 }} onClick={() => abrirEditarNivel(carrera, nivel)}>
                              Editar
                            </button>
                          </div>
                          <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                            <div style={{ flex: 1, textAlign: 'center', padding: '6px 4px', background: 'var(--azul-claro)', borderRadius: 8, border: '1px solid var(--azul-borde)' }}>
                              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--azul)' }}>{nivel.paralelos_matutina}</div>
                              <div style={{ fontSize: 9, color: 'var(--azul)', fontWeight: 600 }}>MANANA</div>
                            </div>
                            <div style={{ flex: 1, textAlign: 'center', padding: '6px 4px', background: 'var(--violeta-claro)', borderRadius: 8, border: '1px solid #ddd6fe' }}>
                              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--violeta)' }}>{nivel.paralelos_nocturna}</div>
                              <div style={{ fontSize: 9, color: 'var(--violeta)', fontWeight: 600 }}>NOCHE</div>
                            </div>
                          </div>
                          <div style={{ textAlign: 'center' }}>
                            <span style={{ fontSize: 10, fontWeight: 600, padding: '2px 10px', borderRadius: 20, background: js.bg, color: js.color }}>
                              {jornadaLabel(nivel.jornada_habilitada)}
                            </span>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── MODAL CREAR/EDITAR CARRERA ── */}
      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
          <div className="modal" style={{ maxWidth: 620 }}>
            <div className="modal-header">
              <h2>{editando ? 'Editar carrera' : 'Nueva carrera'}</h2>
              <button className="modal-close" onClick={() => setModal(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre *</label>
                <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} placeholder="Desarrollo de Software" maxLength={150} />
              </div>
              <div className="form-group">
                <label>Codigo *</label>
                <input value={form.codigo} onChange={e => setForm({...form, codigo: e.target.value.toUpperCase()})} placeholder="DS" maxLength={20} disabled={!!editando} />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Sede *</label>
                <select value={form.sede} onChange={e => setForm({...form, sede: e.target.value})}>
                  <option value="Quito">Quito</option>
                  <option value="Conocoto">Conocoto</option>
                </select>
              </div>
              <div className="form-group">
                <label>Descripcion (opcional)</label>
                <input value={form.descripcion} onChange={e => setForm({...form, descripcion: e.target.value})} placeholder="Descripcion de la carrera" maxLength={500} />
              </div>
            </div>

            {!editando && (
              <div>
                <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--gris-oscuro)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Configuracion por nivel
                </p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 10 }}>
                  {form.niveles.map((niv, idx) => (
                    <div key={idx} style={{ border: '1px solid var(--gris-borde)', borderRadius: 10, padding: '12px 14px', background: 'var(--gris-claro)' }}>
                      <p style={{ fontWeight: 700, fontSize: 13, marginBottom: 10, color: 'var(--negro)' }}>Nivel {niv.numero}</p>
                      <div className="form-group" style={{ marginBottom: 8 }}>
                        <label style={{ fontSize: 11 }}>Jornada habilitada</label>
                        <select value={niv.jornada_habilitada} onChange={e => updateNivelForm(idx, 'jornada_habilitada', e.target.value)}>
                          <option value="ambas">Manana y Noche</option>
                          <option value="matutina">Solo Manana</option>
                          <option value="nocturna">Solo Noche</option>
                        </select>
                      </div>
                      {(niv.jornada_habilitada === 'ambas' || niv.jornada_habilitada === 'matutina') && (
                        <div className="form-group" style={{ marginBottom: 6 }}>
                          <label style={{ color: 'var(--azul)', fontSize: 11 }}>Paralelos jornada Manana (08:00 - 12:00)</label>
                          <input type="number" min="1" max="10" value={niv.paralelos_matutina} onChange={e => updateNivelForm(idx, 'paralelos_matutina', e.target.value)} />
                        </div>
                      )}
                      {(niv.jornada_habilitada === 'ambas' || niv.jornada_habilitada === 'nocturna') && (
                        <div className="form-group" style={{ marginBottom: 0 }}>
                          <label style={{ color: 'var(--violeta)', fontSize: 11 }}>Paralelos jornada Noche (18:30 - 21:30)</label>
                          <input type="number" min="1" max="10" value={niv.paralelos_nocturna} onChange={e => updateNivelForm(idx, 'paralelos_nocturna', e.target.value)} />
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
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

      {/* ── MODAL EDITAR NIVEL ── */}
      {modalNivel && nivelEditando && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalNivel(false)}>
          <div className="modal" style={{ maxWidth: 400 }}>
            <div className="modal-header">
              <h2>Editar nivel — {nivelEditando.nivel.nombre}</h2>
              <button className="modal-close" onClick={() => setModalNivel(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <p style={{ fontSize: 13, color: 'var(--gris-medio)', marginBottom: 16 }}>
              Configura los paralelos y jornada habilitada para este nivel.
            </p>
            <div className="form-group">
              <label>Jornada habilitada</label>
              <select value={formNivel.jornada_habilitada} onChange={e => setFormNivel({...formNivel, jornada_habilitada: e.target.value})}>
                <option value="ambas">Manana y Noche</option>
                <option value="matutina">Solo Manana</option>
                <option value="nocturna">Solo Noche</option>
              </select>
            </div>
            {(formNivel.jornada_habilitada === 'ambas' || formNivel.jornada_habilitada === 'matutina') && (
              <div className="form-group">
                <label style={{ color: 'var(--azul)' }}>Paralelos jornada Manana (08:00 - 12:00)</label>
                <input type="number" min="1" max="10" value={formNivel.paralelos_matutina} onChange={e => setFormNivel({...formNivel, paralelos_matutina: e.target.value})} />
              </div>
            )}
            {(formNivel.jornada_habilitada === 'ambas' || formNivel.jornada_habilitada === 'nocturna') && (
              <div className="form-group">
                <label style={{ color: 'var(--violeta)' }}>Paralelos jornada Noche (18:30 - 21:30)</label>
                <input type="number" min="1" max="10" value={formNivel.paralelos_nocturna} onChange={e => setFormNivel({...formNivel, paralelos_nocturna: e.target.value})} />
              </div>
            )}
            <div className="alert alert-info" style={{ fontSize: 12 }}>
              Los paralelos de manana seran A, B, C... y los de noche tambien A, B, C... de forma independiente.
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModalNivel(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={guardarNivel} disabled={guardando}>
                {guardando ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}