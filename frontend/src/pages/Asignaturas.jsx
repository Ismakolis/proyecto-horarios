import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { getCarreras, getAsignaturas, createAsignatura } from '../services/api'

const formInicial = { nombre: '', codigo: '', horas_modulo: '', nivel_id: '', numero_modulo: 1 }

export default function Asignaturas() {
    const [carreras, setCarreras] = useState([])
    const [asignaturas, setAsignaturas] = useState([])
    const [carreraSeleccionada, setCarreraSeleccionada] = useState(null)
    const [cargando, setCargando] = useState(false)
    const [modal, setModal] = useState(false)
    const [form, setForm] = useState(formInicial)
    const [error, setError] = useState('')
    const [exito, setExito] = useState('')
    const [guardando, setGuardando] = useState(false)
    const [nivelFiltro, setNivelFiltro] = useState(null)
    const location = useLocation()

    useEffect(() => {
        getCarreras().then(res => {
            setCarreras(res.data)
            if (location.state?.carreraId) {
                const carrera = res.data.find(c => c.id === location.state.carreraId)
                if (carrera) seleccionarCarrera(carrera)
            }
        }).catch(() => { })
    }, [])

    const seleccionarCarrera = async (carrera) => {
        setCarreraSeleccionada(carrera)
        setNivelFiltro(null)
        setCargando(true)
        try {
            const res = await getAsignaturas(carrera.id)
            setAsignaturas(res.data)
            console.log('Asignaturas:', JSON.stringify(res.data))
            console.log('Niveles carrera:', JSON.stringify(carrera.niveles))
        } catch {
            setAsignaturas([])
        } finally {
            setCargando(false)
        }
    }

    const abrirModal = (nivelId = null, numMod = 1) => {
        setError('')
        setForm({
            ...formInicial,
            nivel_id: nivelId || carreraSeleccionada?.niveles?.[0]?.id || '',
            numero_modulo: numMod,
        })
        setModal(true)
    }

    const guardar = async () => {
        const nombre = form.nombre.trim()
        const horas = parseFloat(form.horas_modulo)

        if (!nombre) { setError('El nombre de la asignatura es obligatorio'); return }
        if (nombre.length < 2) { setError('El nombre debe tener al menos 2 caracteres'); return }
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.\(\)0-9,/]+$/.test(nombre)) {
            setError('El nombre de la asignatura contiene caracteres no permitidos')
            return
        }
        if (!form.nivel_id) { setError('Selecciona un nivel'); return }
        if (!form.horas_modulo) { setError('Las horas del modulo son obligatorias'); return }
        if (isNaN(horas) || horas <= 0) { setError('Las horas deben ser un numero mayor a 0'); return }
        if (horas > 500) { setError('Las horas no pueden superar 500'); return }

        setGuardando(true)
        setError('')
        try {
            await createAsignatura({
                carrera_id: carreraSeleccionada.id,
                nivel_id: form.nivel_id,
                nombre: form.nombre,
                codigo: form.codigo,
                numero_modulo: form.numero_modulo,
                horas_modulo: parseFloat(form.horas_modulo),
            })
            setExito('Asignatura creada correctamente')
            setModal(false)
            const res = await getAsignaturas(carreraSeleccionada.id)
            setAsignaturas(res.data)
            setTimeout(() => setExito(''), 3000)
        } catch (err) {
            setError(err.response?.data?.detail || 'Error al guardar')
        } finally {
            setGuardando(false)
        }
    }

    const nivelesOrdenados = carreraSeleccionada?.niveles?.slice().sort((a, b) => a.numero - b.numero) || []
    const nivelesFiltrados = nivelFiltro ? nivelesOrdenados.filter(n => n.id === nivelFiltro) : nivelesOrdenados

    return (
        <>
            <div className="topbar">
                <div>
                    <h1>📚 Asignaturas</h1>
                    <p>Malla curricular por carrera, nivel y módulo</p>
                </div>
                {carreraSeleccionada && (
                    <button className="btn btn-primary" onClick={() => abrirModal()}>+ Nueva asignatura</button>
                )}
            </div>

            {exito && <div className="alert alert-success">{exito}</div>}

            {/* Selector de carrera */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
                {carreras.map(c => (
                    <button
                        key={c.id}
                        onClick={() => seleccionarCarrera(c)}
                        style={{
                            padding: '8px 18px', borderRadius: 8, border: '2px solid', cursor: 'pointer', fontSize: 13, transition: 'all 0.2s',
                            borderColor: carreraSeleccionada?.id === c.id ? 'var(--rojo-itq)' : '#e5e7eb',
                            background: carreraSeleccionada?.id === c.id ? '#fee2e2' : '#fff',
                            color: carreraSeleccionada?.id === c.id ? 'var(--rojo-itq)' : '#374151',
                            fontWeight: carreraSeleccionada?.id === c.id ? 700 : 400,
                        }}
                    >
                        {c.codigo} — {c.nombre}
                    </button>
                ))}
            </div>

            {/* Filtro por nivel */}
            {carreraSeleccionada && (
                <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
                    <button
                        onClick={() => setNivelFiltro(null)}
                        style={{
                            padding: '5px 14px', borderRadius: 20, border: '1.5px solid', cursor: 'pointer', fontSize: 12, transition: 'all 0.2s',
                            borderColor: nivelFiltro === null ? 'var(--rojo-itq)' : '#e5e7eb',
                            background: nivelFiltro === null ? '#fee2e2' : '#fff',
                            color: nivelFiltro === null ? 'var(--rojo-itq)' : '#6b7280',
                            fontWeight: nivelFiltro === null ? 700 : 400,
                        }}
                    >
                        Todos los niveles
                    </button>
                    {nivelesOrdenados.map(n => (
                        <button
                            key={n.id}
                            onClick={() => setNivelFiltro(n.id)}
                            style={{
                                padding: '5px 14px', borderRadius: 20, border: '1.5px solid', cursor: 'pointer', fontSize: 12, transition: 'all 0.2s',
                                borderColor: nivelFiltro === n.id ? 'var(--rojo-itq)' : '#e5e7eb',
                                background: nivelFiltro === n.id ? '#fee2e2' : '#fff',
                                color: nivelFiltro === n.id ? 'var(--rojo-itq)' : '#6b7280',
                                fontWeight: nivelFiltro === n.id ? 700 : 400,
                            }}
                        >
                            {n.nombre || `Nivel ${n.numero}`}
                        </button>
                    ))}
                </div>
            )}

            {!carreraSeleccionada ? (
                <div className="card">
                    <div className="empty-state">
                        <p style={{ fontSize: 32 }}>🎓</p>
                        <p>Selecciona una carrera para ver su malla curricular</p>
                    </div>
                </div>
            ) : cargando ? (
                <div className="loading">Cargando asignaturas...</div>
            ) : (
                <div>
                    {nivelesFiltrados.map(nivel => {
                        const asigNivel = asignaturas.filter(a => a.nivel_id === nivel.id)
                        return (
                            <div key={nivel.id} className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 16 }}>

                                {/* Header nivel */}
                                <div style={{ background: '#1a1a1a', color: '#fff', padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontWeight: 700, fontSize: 14 }}>
                                        📚 {nivel.nombre || `Nivel ${nivel.numero}`}
                                    </span>
                                    <span style={{ fontSize: 12, color: '#aaa' }}>
                                        {asigNivel.length} / 6 asignatura(s)
                                    </span>
                                </div>

                                {/* Módulos */}
                                {[1, 2, 3].map(numMod => {
                                    const asigsMod = asigNivel.filter(a => parseInt(a.numero_modulo) === numMod)
                                    const espaciosLibres = 2 - asigsMod.length
                                    return (
                                        <div key={numMod} style={{ borderBottom: '1px solid #f0f0f0', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 16 }}>

                                            {/* Label módulo */}
                                            <div style={{ minWidth: 90 }}>
                                                <span style={{
                                                    background: numMod === 1 ? '#dbeafe' : numMod === 2 ? '#fef3c7' : '#d1fae5',
                                                    color: numMod === 1 ? '#1e40af' : numMod === 2 ? '#92400e' : '#065f46',
                                                    padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700,
                                                }}>
                                                    Módulo {numMod}
                                                </span>
                                            </div>

                                            {/* Asignaturas */}
                                            <div style={{ display: 'flex', gap: 10, flex: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                                                {asigsMod.length === 0 && (
                                                    <span style={{ fontSize: 12, color: '#9ca3af', fontStyle: 'italic' }}>Sin asignaturas</span>
                                                )}
                                                {asigsMod.map(a => (
                                                    <div key={a.id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 14px', minWidth: 200 }}>
                                                        <div style={{ fontWeight: 700, fontSize: 13, color: '#1e293b' }}>{a.nombre}</div>
                                                        <div style={{ fontSize: 11, color: '#64748b', marginTop: 3, display: 'flex', gap: 8 }}>
                                                            {a.codigo && (
                                                                <span style={{ background: '#e0f2fe', color: '#0369a1', borderRadius: 4, padding: '1px 6px' }}>
                                                                    {a.codigo}
                                                                </span>
                                                            )}
                                                            <span>⏱ {a.horas_modulo}h</span>
                                                        </div>
                                                    </div>
                                                ))}

                                                {/* Espacios libres */}
                                                {espaciosLibres > 0 && Array.from({ length: espaciosLibres }).map((_, i) => (
                                                    <div
                                                        key={i}
                                                        onClick={() => abrirModal(nivel.id, numMod)}
                                                        style={{ border: '2px dashed #e5e7eb', borderRadius: 8, padding: '8px 14px', minWidth: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#9ca3af', fontSize: 12, transition: 'all 0.2s' }}
                                                        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--rojo-itq)'; e.currentTarget.style.color = 'var(--rojo-itq)' }}
                                                        onMouseLeave={e => { e.currentTarget.style.borderColor = '#e5e7eb'; e.currentTarget.style.color = '#9ca3af' }}
                                                    >
                                                        + Agregar
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Modal */}
            {modal && (
                <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
                    <div className="modal">
                        <div className="modal-header">
                            <h2>+ Nueva asignatura</h2>
                            <button className="modal-close" onClick={() => setModal(false)}>×</button>
                        </div>
                        {error && <div className="alert alert-error">{error}</div>}

                        <div className="form-row">
                            <div className="form-group">
                                <label>Nombre</label>
                                <input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} placeholder="Lógica de Programación" />
                            </div>
                            <div className="form-group">
                                <label>Código</label>
                                <input value={form.codigo} onChange={e => setForm({ ...form, codigo: e.target.value })} placeholder="LP" />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Nivel</label>
                                <select value={form.nivel_id} onChange={e => setForm({ ...form, nivel_id: e.target.value })}>
                                    {nivelesOrdenados.map(n => (
                                        <option key={n.id} value={n.id}>{n.nombre || `Nivel ${n.numero}`}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Módulo</label>
                                <select value={form.numero_modulo} onChange={e => setForm({ ...form, numero_modulo: parseInt(e.target.value) })}>
                                    <option value={1}>Módulo 1</option>
                                    <option value={2}>Módulo 2</option>
                                    <option value={3}>Módulo 3</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Total horas por módulo</label>
                            <input
                                type="number"
                                value={form.horas_modulo}
                                onChange={e => setForm({ ...form, horas_modulo: e.target.value })}
                                onKeyDown={e => {
                                    if (!/[0-9.]/.test(e.key) && !['Backspace','Delete','ArrowLeft','ArrowRight','Tab'].includes(e.key)) {
                                        e.preventDefault()
                                    }
                                }}
                                inputMode="decimal"
                                placeholder="32"
                                min="1"
                                max="500" 
                                placeholder="36 matutino / 27 nocturno"
                            />
                        </div>

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