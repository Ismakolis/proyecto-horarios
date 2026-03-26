/**
 * Docentes.jsx
 * Gestion de docentes y disponibilidad horaria.
 * Incluye validaciones de frontend antes de enviar al backend.
 */

import { useEffect, useState } from 'react'
import { getDocentes, createDocente, updateDocente, deleteDocente } from '../services/api'

const DIAS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado']
const JORNADAS = ['matutina', 'nocturna']

const formInicial = {
  cedula: '', nombre: '', apellido: '', email: '',
  tipo: 'tiempo_completo', titulo: '',
  disponibilidades: []
}

// Regex para validar que un campo solo tenga letras, espacios y guiones
const SOLO_LETRAS = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function Docentes() {
  const [docentes, setDocentes]   = useState([])
  const [cargando, setCargando]   = useState(true)
  const [modal, setModal]         = useState(false)
  const [editando, setEditando]   = useState(null)
  const [form, setForm]           = useState(formInicial)
  const [error, setError]         = useState('')
  const [exito, setExito]         = useState('')
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

  // Validacion de formulario antes de enviar al backend
  const validar = () => {
    const nombre   = form.nombre.trim()
    const apellido = form.apellido.trim()
    const email    = form.email.trim()
    const cedula   = form.cedula.trim()

    if (!nombre) return 'El nombre es obligatorio'
    if (nombre.length < 2) return 'El nombre debe tener al menos 2 caracteres'
    if (!SOLO_LETRAS.test(nombre)) return 'El nombre solo puede contener letras, espacios y guiones'

    if (!apellido) return 'El apellido es obligatorio'
    if (apellido.length < 2) return 'El apellido debe tener al menos 2 caracteres'
    if (!SOLO_LETRAS.test(apellido)) return 'El apellido solo puede contener letras, espacios y guiones'

    if (!email) return 'El email es obligatorio'
    if (!EMAIL_REGEX.test(email)) return 'El email no tiene un formato valido'

    if (!editando) {
      if (!cedula) return 'La cedula es obligatoria'
      if (!/^\d{10}$/.test(cedula)) return 'La cedula debe tener exactamente 10 digitos numericos'
    }

    if (form.titulo) {
      const titulo = form.titulo.trim()
      if (titulo.length > 200) return 'El titulo no puede superar los 200 caracteres'
    }

    return null // sin errores
  }

  const guardar = async () => {
    const errValidacion = validar()
    if (errValidacion) { setError(errValidacion); return }

    setGuardando(true)
    setError('')
    try {
      if (editando) {
        await updateDocente(editando.id, {
          nombre:   form.nombre.trim(),
          apellido: form.apellido.trim(),
          email:    form.email.trim(),
          tipo:     form.tipo,
          titulo:   form.titulo.trim() || null,
        })
      } else {
        await createDocente({
          ...form,
          nombre:   form.nombre.trim(),
          apellido: form.apellido.trim(),
          email:    form.email.trim(),
          cedula:   form.cedula.trim(),
          titulo:   form.titulo.trim() || null,
        })
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
    if (!confirm(`Desactivar a ${doc.nombre} ${doc.apellido}?`)) return
    try {
      await deleteDocente(doc.id)
      setExito('Docente desactivado')
      cargar()
      setTimeout(() => setExito(''), 3000)
    } catch {
      setError('Error al desactivar')
    }
  }

  // Bloquear numeros en campos de texto de nombre/apellido
  const soloLetras = (e) => {
    const char = e.key
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$/.test(char) && !['Backspace','Delete','ArrowLeft','ArrowRight','Tab'].includes(char)) {
      e.preventDefault()
    }
  }

  // Bloquear letras en campo de cedula
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
          <p>Gestion de docentes y disponibilidad</p>
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
            <p>No hay docentes registrados aun.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Cedula</th>
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
                      <button className="btn btn-secondary" onClick={() => abrirEditar(doc)}>Editar</button>
                      {doc.activo && (
                        <button className="btn btn-danger" onClick={() => desactivar(doc)}>Desactivar</button>
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
              <button className="modal-close" onClick={() => setModal(false)}>x</button>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <div className="form-row">
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  value={form.nombre}
                  onChange={e => setForm({...form, nombre: e.target.value})}
                  onKeyDown={soloLetras}
                  placeholder="Juan"
                  maxLength={100}
                />
              </div>
              <div className="form-group">
                <label>Apellido *</label>
                <input
                  value={form.apellido}
                  onChange={e => setForm({...form, apellido: e.target.value})}
                  onKeyDown={soloLetras}
                  placeholder="Perez"
                  maxLength={100}
                />
              </div>
            </div>

            {!editando && (
              <div className="form-group">
                <label>Cedula * (10 digitos)</label>
                <input
                  value={form.cedula}
                  onChange={e => setForm({...form, cedula: e.target.value})}
                  onKeyDown={soloNumeros}
                  placeholder="1234567890"
                  maxLength={10}
                  inputMode="numeric"
                />
              </div>
            )}

            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({...form, email: e.target.value})}
                placeholder="docente@itq.edu.ec"
              />
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
                <label>Titulo (opcional)</label>
                <input
                  value={form.titulo}
                  onChange={e => setForm({...form, titulo: e.target.value})}
                  placeholder="Ing. en Sistemas"
                  maxLength={200}
                />
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
                        {dia.slice(0, 3)} {jornada.slice(0, 3)}
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
