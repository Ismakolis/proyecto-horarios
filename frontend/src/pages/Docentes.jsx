import { useEffect, useState } from 'react'
import { getDocentes, createDocente, updateDocente, deleteDocente } from '../services/api'

const DIAS = ['lunes','martes','miercoles','jueves','viernes','sabado']
const JORNADAS = ['matutina','nocturna']

const formInicial = {
  cedula: '', nombre: '', apellido: '', email: '',
  tipo: 'tiempo_completo', titulo: '',
  disponibilidades: []
}

export default function Docentes() {
  const [docentes, setDocentes] = useState([])
  const [cargando, setCargando] = useState(true)
  const [modal, setModal] = useState(false)
  const [editando, setEditando] = useState(null)
  const [form, setForm] = useState(formInicial)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [guardando, setGuardando] = useState(false)

  const cargar = async () => {
    try {
      const res = await getDocentes()
      setDocentes(res.data)
    } catch {
      setError('Error al cargar docentes')
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

  const abrirEditar = (doc) => {
    setEditando(doc)
    setForm({
      cedula: doc.cedula,
      nombre: doc.nombre,
      apellido: doc.apellido,
      email: doc.email,
      tipo: doc.tipo,
      titulo: doc.titulo || '',
      disponibilidades: []
    })
    setError('')
    setModal(true)
  }

  const toggleDisponibilidad = (dia, jornada) => {
    const existe = form.disponibilidades.find(d => d.dia === dia && d.jornada === jornada)
    if (existe) {
      setForm({ ...form, disponibilidades: form.disponibilidades.filter(d => !(d.dia === dia && d.jornada === jornada)) })
    } else {
      setForm({ ...form, disponibilidades: [...form.disponibilidades, { dia, jornada, disponible: true }] })
    }
  }

  const estaSeleccionado = (dia, jornada) =>
    form.disponibilidades.some(d => d.dia === dia && d.jornada === jornada)

  const guardar = async () => {
    setGuardando(true)
    setError('')
    try {
      if (editando) {
        await updateDocente(editando.id, {
          nombre: form.nombre,
          apellido: form.apellido,
          email: form.email,
          tipo: form.tipo,
          titulo: form.titulo,
        })
      } else {
        await createDocente(form)
      }
      setExito(editando ? 'Docente actualizado correctamente' : 'Docente creado correctamente')
      setModal(false)
      cargar()
      setTimeout(() => setExito(''), 3000)
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map(e => e.msg).join(', '))
      } else {
        setError(detail || 'Error al guardar')
      }
    } finally {
      setGuardando(false)
    }
  }

  const desactivar = async (doc) => {
    if (!confirm(`¿Desactivar a ${doc.nombre} ${doc.apellido}?`)) return
    try {
      await deleteDocente(doc.id)
      setExito('Docente desactivado')
      cargar()
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Error al desactivar')
    }
  }

  return (
    <>
      <div className="topbar">
        <div>
          <h1>👨‍🏫 Docentes</h1>
          <p>Gestión de docentes y disponibilidad</p>
        </div>
        <button className="btn btn-primary" onClick={abrirCrear}>+ Nuevo docente</button>
      </div>

      {exito && <div className="alert alert-success">{exito}</div>}
      {error && !modal && <div className="alert alert-error">{error}</div>}

      <div className="card">
        {cargando ? (
          <div className="loading">Cargando docentes...</div>
        ) : docentes.length === 0 ? (
          <div className="empty-state">
            <p>No hay docentes registrados aún.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Cédula</th>
                  <th>Nombre</th>
                  <th>Email</th>
                  <th>Tipo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {docentes.map(doc => (
                  <tr key={doc.id}>
                    <td>{doc.cedula}</td>
                    <td><strong>{doc.nombre} {doc.apellido}</strong></td>
                    <td>{doc.email}</td>
                    <td>
                      <span className={`badge ${doc.tipo === 'tiempo_completo' ? 'badge-blue' : 'badge-yellow'}`}>
                        {doc.tipo === 'tiempo_completo' ? 'Tiempo Completo' : 'Tiempo Parcial'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${doc.activo ? 'badge-green' : 'badge-red'}`}>
                        {doc.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td style={{ display: 'flex', gap: 8 }}>
                      <button className="btn btn-secondary" onClick={() => abrirEditar(doc)}>✏️ Editar</button>
                      {doc.activo && (
                        <button className="btn btn-danger" onClick={() => desactivar(doc)}>🗑️</button>
                      )}
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
          <div className="modal">
            <div className="modal-header">
              <h2>{editando ? 'Editar docente' : 'Nuevo docente'}</h2>
              <button className="modal-close" onClick={() => setModal(false)}>×</button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre</label>
                <input value={form.nombre} onChange={e => setForm({...form, nombre: e.target.value})} placeholder="Juan" />
              </div>
              <div className="form-group">
                <label>Apellido</label>
                <input value={form.apellido} onChange={e => setForm({...form, apellido: e.target.value})} placeholder="Pérez" />
              </div>
            </div>

            {!editando && (
              <div className="form-group">
                <label>Cédula</label>
                <input value={form.cedula} onChange={e => setForm({...form, cedula: e.target.value})} placeholder="1234567890" maxLength={10} />
              </div>
            )}

            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="docente@itq.edu.ec" />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Tipo</label>
                <select value={form.tipo} onChange={e => setForm({...form, tipo: e.target.value})}>
                  <option value="tiempo_completo">Tiempo Completo</option>
                  <option value="tiempo_parcial">Tiempo Parcial</option>
                </select>
              </div>
              <div className="form-group">
                <label>Título</label>
                <input value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} placeholder="Ing. en Sistemas" />
              </div>
            </div>

            {!editando && (
              <div className="form-group">
                <label>Disponibilidad</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginTop: 8 }}>
                  {DIAS.map(dia =>
                    JORNADAS.map(jornada => (
                      <button
                        key={`${dia}-${jornada}`}
                        type="button"
                        onClick={() => toggleDisponibilidad(dia, jornada)}
                        style={{
                          padding: '6px 4px',
                          borderRadius: 6,
                          border: '1.5px solid',
                          fontSize: 11,
                          cursor: 'pointer',
                          borderColor: estaSeleccionado(dia, jornada) ? 'var(--rojo-itq)' : '#e5e7eb',
                          background: estaSeleccionado(dia, jornada) ? '#fee2e2' : '#fff',
                          color: estaSeleccionado(dia, jornada) ? 'var(--rojo-itq)' : '#666',
                          fontWeight: estaSeleccionado(dia, jornada) ? 700 : 400,
                        }}
                      >
                        {dia.slice(0,3)} {jornada.slice(0,3)}
                      </button>
                    ))
                  )}
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
    </>
  )
}