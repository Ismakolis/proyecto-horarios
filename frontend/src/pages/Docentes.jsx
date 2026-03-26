/**
 * Docentes.jsx
 * Gestion de docentes, acceso al sistema y habilidades.
 */
import { useEffect, useState } from 'react'
import {
  getDocentes, createDocente, updateDocente,
  crearAccesoDocente, getHabilidades, updateHabilidades,
  getAsignaturas
} from '../services/api'

const SOLO_LETRAS = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const formInicial = {
  cedula: '', nombre: '', apellido: '',
  email: '', tipo: 'tiempo_completo', titulo: ''
}

export default function Docentes() {
  const [docentes, setDocentes]             = useState([])
  const [cargando, setCargando]             = useState(true)
  const [modal, setModal]                   = useState(false)
  const [modalAcceso, setModalAcceso]       = useState(false)
  const [modalHabilidades, setModalHabilidades] = useState(false)
  const [editando, setEditando]             = useState(null)
  const [docenteSeleccionado, setDocenteSeleccionado] = useState(null)
  const [form, setForm]                     = useState(formInicial)
  const [password, setPassword]             = useState('')
  const [todasAsignaturas, setTodasAsignaturas] = useState([])
  const [seleccionadas, setSeleccionadas]   = useState([])
  const [error, setError]                   = useState('')
  const [exito, setExito]                   = useState('')
  const [guardando, setGuardando]           = useState(false)

  const cargar = async () => {
    try {
      const res = await getDocentes()
      setDocentes(res.data)
    } catch { setError('Error al cargar docentes') }
    finally { setCargando(false) }
  }

  useEffect(() => { cargar() }, [])

  const abrirCrear = () => {
    setEditando(null); setForm(formInicial); setError(''); setModal(true)
  }

  const abrirEditar = (doc) => {
    setEditando(doc)
    setForm({
      cedula: doc.cedula, nombre: doc.nombre,
      apellido: doc.apellido, email: doc.email,
      tipo: doc.tipo, titulo: doc.titulo || '',
      activo: doc.activo,
    })
    setError(''); setModal(true)
  }

  const abrirAcceso = (doc) => {
    setDocenteSeleccionado(doc); setPassword(''); setError(''); setModalAcceso(true)
  }

  const abrirHabilidades = async (doc) => {
    setDocenteSeleccionado(doc); setError('')
    try {
      const [habs, asigs] = await Promise.all([
        getHabilidades(doc.id),
        getAsignaturas()
      ])
      setTodasAsignaturas(asigs.data)
      setSeleccionadas(habs.data.map(h => h.asignatura_id))
      setModalHabilidades(true)
    } catch { setError('Error al cargar habilidades') }
  }

  const validar = () => {
    const n = form.nombre.trim(), a = form.apellido.trim(), e = form.email.trim()
    if (!n) return 'El nombre es obligatorio'
    if (!SOLO_LETRAS.test(n)) return 'El nombre solo puede contener letras'
    if (!a) return 'El apellido es obligatorio'
    if (!SOLO_LETRAS.test(a)) return 'El apellido solo puede contener letras'
    if (!e) return 'El email es obligatorio'
    if (!EMAIL_REGEX.test(e)) return 'El email no es valido'
    if (!editando && !/^\d{10}$/.test(form.cedula.trim())) return 'La cedula debe tener 10 digitos'
    return null
  }

  const guardar = async () => {
    const err = validar()
    if (err) { setError(err); return }
    setGuardando(true); setError('')
    try {
      if (editando) {
        await updateDocente(editando.id, {
          nombre: form.nombre.trim(), apellido: form.apellido.trim(),
          email: form.email.trim(), tipo: form.tipo,
          titulo: form.titulo.trim() || null,
          activo: form.activo,
        })
      } else {
        await createDocente({
          cedula: form.cedula.trim(), nombre: form.nombre.trim(),
          apellido: form.apellido.trim(), email: form.email.trim(),
          tipo: form.tipo, titulo: form.titulo.trim() || null,
        })
      }
      setExito(editando ? 'Docente actualizado' : 'Docente creado correctamente')
      setModal(false); cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (e) {
      const d = e.response?.data?.detail
      setError(Array.isArray(d) ? d.map(x => x.msg).join(', ') : (d || 'Error al guardar'))
    } finally { setGuardando(false) }
  }

  const guardarAcceso = async () => {
    if (password.length < 6) { setError('La contraseña debe tener al menos 6 caracteres'); return }
    setGuardando(true); setError('')
    try {
      await crearAccesoDocente({ docente_id: docenteSeleccionado.id, password })
      setExito(`Acceso creado para ${docenteSeleccionado.nombre} ${docenteSeleccionado.apellido}`)
      setModalAcceso(false); cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al crear acceso')
    } finally { setGuardando(false) }
  }

  const guardarHabilidades = async () => {
    setGuardando(true); setError('')
    try {
      await updateHabilidades(docenteSeleccionado.id, { asignatura_ids: seleccionadas })
      setExito('Habilidades actualizadas')
      setModalHabilidades(false); 
      setTimeout(() => setExito(''), 3000)
    } catch (e) {
      setError(e.response?.data?.detail || 'Error al guardar habilidades')
    } finally { setGuardando(false) }
  }

  const toggleAsignatura = (id) => {
    setSeleccionadas(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  const soloLetras = (e) => {
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']$/.test(e.key) &&
      !['Backspace','Delete','ArrowLeft','ArrowRight','Tab'].includes(e.key)) {
      e.preventDefault()
    }
  }

  const soloNumeros = (e) => {
    if (!/^\d$/.test(e.key) && !['Backspace','Delete','ArrowLeft','ArrowRight','Tab'].includes(e.key)) {
      e.preventDefault()
    }
  }

  return (
    <>
      <div className="topbar">
        <div>
          <h1>Docentes</h1>
          <p>Gestion de docentes, accesos y habilidades</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nuevo docente</button>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modal && !modalAcceso && !modalHabilidades && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {cargando ? (
          <div className="loading">Cargando docentes...</div>
        ) : docentes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">👤</div>
            <p>No hay docentes registrados</p>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Docente</th>
                  <th>Cédula</th>
                  <th>Tipo</th>
                  <th>Acceso</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {docentes.map(doc => (
                  <tr key={doc.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          width: 34, height: 34, borderRadius: '50%',
                          background: 'var(--rojo-claro)', color: 'var(--rojo-itq)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 700, fontSize: 12, flexShrink: 0,
                        }}>
                          {doc.nombre[0]}{doc.apellido[0]}
                        </div>
                        <div>
                          <p style={{ fontWeight: 600, fontSize: 13, color: 'var(--negro)' }}>
                            {doc.nombre} {doc.apellido}
                          </p>
                          <p style={{ fontSize: 11, color: 'var(--gris-medio)' }}>{doc.email}</p>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: 13, color: 'var(--gris-oscuro)' }}>{doc.cedula}</td>
                    <td>
                      <span className={`badge ${doc.tipo === 'tiempo_completo' ? 'badge-blue' : 'badge-yellow'}`}>
                        {doc.tipo === 'tiempo_completo' ? 'TC' : 'TP'}
                      </span>
                    </td>
                    <td>
                      {doc.tiene_acceso ? (
                        <span className="badge badge-green">Con acceso</span>
                      ) : (
                        <button className="btn btn-secondary btn-sm" onClick={() => abrirAcceso(doc)}>
                          + Crear acceso
                        </button>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${doc.activo ? 'badge-green' : 'badge-red'}`}>
                        {doc.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => abrirEditar(doc)}>
                          Editar
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => abrirHabilidades(doc)}
                          title="Gestionar habilidades">
                          Habilidades
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── MODAL CREAR/EDITAR DOCENTE ── */}
      {modal && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
          <div className="modal">
            <div className="modal-header">
              <h2>{editando ? 'Editar docente' : 'Nuevo docente'}</h2>
              <button className="modal-close" onClick={() => setModal(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre *</label>
                <input value={form.nombre} onKeyDown={soloLetras} maxLength={100}
                  onChange={e => setForm({...form, nombre: e.target.value})} placeholder="Juan" />
              </div>
              <div className="form-group">
                <label>Apellido *</label>
                <input value={form.apellido} onKeyDown={soloLetras} maxLength={100}
                  onChange={e => setForm({...form, apellido: e.target.value})} placeholder="Perez" />
              </div>
            </div>

            {!editando && (
              <div className="form-group">
                <label>Cédula * (10 dígitos)</label>
                <input value={form.cedula} onKeyDown={soloNumeros} maxLength={10} inputMode="numeric"
                  onChange={e => setForm({...form, cedula: e.target.value})} placeholder="1234567890" />
              </div>
            )}

            <div className="form-group">
              <label>Email *</label>
              <input type="email" value={form.email}
                onChange={e => setForm({...form, email: e.target.value})} placeholder="docente@itq.edu.ec" />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Tipo</label>
                <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})}>
                  <option value="tiempo_completo">Tiempo Completo (TC)</option>
                  <option value="tiempo_parcial">Tiempo Parcial (TP)</option>
                </select>
              </div>
              <div className="form-group">
                <label>Titulo (opcional)</label>
                <input value={form.titulo} maxLength={200}
                  onChange={e => setForm({...form, titulo: e.target.value})} placeholder="Ing. en Sistemas" />
              </div>
            </div>

            {editando && (
              <div className="form-group">
                <label>Estado</label>
                <select value={form.activo} onChange={e => setForm({...form, activo: e.target.value === 'true'})}>
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
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

      {/* ── MODAL CREAR ACCESO ── */}
      {modalAcceso && docenteSeleccionado && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalAcceso(false)}>
          <div className="modal" style={{ maxWidth: 420 }}>
            <div className="modal-header">
              <h2>Crear acceso al sistema</h2>
              <button className="modal-close" onClick={() => setModalAcceso(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <div style={{ background: 'var(--gris-claro)', borderRadius: 10, padding: '12px 16px', marginBottom: 16 }}>
              <p style={{ fontWeight: 600, fontSize: 13 }}>
                {docenteSeleccionado.nombre} {docenteSeleccionado.apellido}
              </p>
              <p style={{ fontSize: 12, color: 'var(--gris-medio)', marginTop: 2 }}>
                Usuario: <strong>{docenteSeleccionado.email}</strong>
              </p>
            </div>

            <div className="form-group">
              <label>Contraseña *</label>
              <input type="password" value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres" />
            </div>

            <div className="alert alert-info" style={{ fontSize: 12 }}>
              El docente usara su email como usuario y esta contraseña para iniciar sesión.
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModalAcceso(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={guardarAcceso} disabled={guardando}>
                {guardando ? 'Creando...' : 'Crear acceso'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODAL HABILIDADES ── */}
      {modalHabilidades && docenteSeleccionado && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalHabilidades(false)}>
          <div className="modal" style={{ maxWidth: 580 }}>
            <div className="modal-header">
              <h2>Habilidades — {docenteSeleccionado.nombre} {docenteSeleccionado.apellido}</h2>
              <button className="modal-close" onClick={() => setModalHabilidades(false)}>×</button>
            </div>
            {error && <div className="alert alert-error">{error}</div>}

            <p style={{ fontSize: 13, color: 'var(--gris-medio)', marginBottom: 16 }}>
              Selecciona las asignaturas que este docente puede dictar.
            </p>

            {todasAsignaturas.length === 0 ? (
              <div className="alert alert-warning">No hay asignaturas registradas en el sistema.</div>
            ) : (
              <div style={{ maxHeight: 340, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {todasAsignaturas
                  .filter((a, idx, arr) => arr.findIndex(x => x.nombre === a.nombre && x.numero_modulo === a.numero_modulo) === idx)
                  .map(a => (
                  <div
                    key={a.id}
                    onClick={() => toggleAsignatura(a.id)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 12,
                      padding: '10px 14px', borderRadius: 8, cursor: 'pointer',
                      border: '1.5px solid',
                      borderColor: seleccionadas.includes(a.id) ? 'var(--rojo-itq)' : 'var(--gris-borde)',
                      background: seleccionadas.includes(a.id) ? 'var(--rojo-claro)' : 'var(--blanco)',
                      transition: 'all 0.15s',
                    }}
                  >
                    <div style={{
                      width: 18, height: 18, borderRadius: 4, flexShrink: 0,
                      border: '2px solid',
                      borderColor: seleccionadas.includes(a.id) ? 'var(--rojo-itq)' : 'var(--gris-borde)',
                      background: seleccionadas.includes(a.id) ? 'var(--rojo-itq)' : 'transparent',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                      {seleccionadas.includes(a.id) && (
                        <span style={{ color: '#fff', fontSize: 11, fontWeight: 700 }}>✓</span>
                      )}
                    </div>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontWeight: 600, fontSize: 13, color: 'var(--negro)' }}>{a.nombre}</p>
                      {a.codigo && (
                        <span style={{ fontSize: 11, color: 'var(--gris-medio)' }}>{a.codigo}</span>
                      )}
                    </div>
                    <span className="badge badge-gray" style={{ fontSize: 10 }}>
                      Mod. {a.numero_modulo}
                    </span>
                  </div>
                ))}
              </div>
            )}

            <div style={{ marginTop: 12, fontSize: 12, color: 'var(--gris-medio)' }}>
              {seleccionadas.length} asignatura(s) seleccionada(s)
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setModalHabilidades(false)}>Cancelar</button>
              <button className="btn btn-primary" onClick={guardarHabilidades} disabled={guardando}>
                {guardando ? 'Guardando...' : 'Guardar habilidades'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}