import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { getCarreras, getAsignaturas, createAsignatura, copiarMalla } from '../services/api'

const formInicial = { nombre: '', codigo: '', horas_modulo: '', nivel_id: '', numero_modulo: 1 }

export default function Asignaturas() {
    const [carreras, setCarreras]             = useState([])
    const [asignaturas, setAsignaturas]       = useState([])
    const [carreraSeleccionada, setCarreraSeleccionada] = useState(null)
    const [cargando, setCargando]             = useState(false)
    const [modal, setModal]                   = useState(false)
    const [form, setForm]                     = useState(formInicial)
    const [error, setError]                   = useState('')
    const [exito, setExito]                   = useState('')
    const [guardando, setGuardando]           = useState(false)
    const [nivelFiltro, setNivelFiltro]       = useState(null)
    const [modalCopiar, setModalCopiar]       = useState(false)
    const [carreraOrigenId, setCarreraOrigenId] = useState('')
    const [copiando, setCopiando]             = useState(false)
    const location = useLocation()

    useEffect(() => {
        getCarreras().then(res => {
            setCarreras(res.data)
            if (location.state?.carreraId) {
                const carrera = res.data.find(c => c.id === location.state.carreraId)
                if (carrera) seleccionarCarrera(carrera)
            }
        }).catch(() => {})
    }, [])

    const seleccionarCarrera = async (carrera) => {
        setCarreraSeleccionada(carrera)
        setNivelFiltro(null)
        setCargando(true)
        try {
            const res = await getAsignaturas(carrera.id)
            setAsignaturas(res.data)
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
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-.()0-9,/]+$/.test(nombre)) {
            setError('El nombre de la asignatura contiene caracteres no permitidos'); return
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

    const ejecutarCopia = async () => {
        if (!carreraOrigenId) return
        if (!confirm('Esto copiara todas las asignaturas de la carrera seleccionada. Continuar?')) return
        setCopiando(true)
        try {
            const res = await copiarMalla(carreraSeleccionada.id, carreraOrigenId)
            setExito(res.data.mensaje)
            setModalCopiar(false)
            const r = await getAsignaturas(carreraSeleccionada.id)
            setAsignaturas(r.data)
            setTimeout(() => setExito(''), 4000)
        } catch (e) {
            setError(e.response?.data?.detail || 'Error al copiar malla')
        } finally { setCopiando(false) }
    }

    const nivelesOrdenados = carreraSeleccionada?.niveles?.slice().sort((a, b) => a.numero - b.numero) || []
    const nivelesFiltrados = nivelFiltro ? nivelesOrdenados.filter(n => n.id === nivelFiltro) : nivelesOrdenados

    return (
        <>
            <div className="topbar">
                <div>
                    <h1>Asignaturas</h1>
                    <p>Malla curricular por carrera, nivel y modulo</p>
                </div>
                {carreraSeleccionada && (
                    <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn btn-secondary" onClick={() => { setCarreraOrigenId(''); setModalCopiar(true) }}>
                            Copiar malla
                        </button>
                        <button className="btn btn-primary" onClick={() => abrirModal()}>+ Nueva asignatura</button>
                    </div>
                )}
            </div>

            {exito && <div className="alert alert-success">{exito}</div>}
            {error && !modal && !modalCopiar && <div className="alert alert-error">{error}</div>}

            {/* Selector de carrera */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
                {carreras.map(c => (
                    <button
                        key={c.id}
                        onClick={() => seleccionarCarrera(c)}
                        style={{
                            padding: '8px 18px', borderRadius: 8, border: '2px solid',
                            cursor: 'pointer', fontSize: 13, transition: 'all 0.2s',
                            borderColor: carreraSeleccionada?.id === c.id ? 'var(--rojo-itq)' : '#e5e7eb',
                            background: carreraSeleccionada?.id === c.id ? '#fee2e2' : '#fff',
                            color: carreraSeleccionada?.id === c.id ? 'var(--rojo-itq)' : '#374151',
                            fontWeight: carreraSeleccionada?.id === c.id ? 700 : 400,
                        }}
                    >
                        {c.codigo} — {c.nombre} <span style={{ fontSize: 11, opacity: 0.7 }}>({c.sede || 'Quito'})</span>
                    </button>
                ))}
            </div>

            {/* Filtro por nivel */}
            {carreraSeleccionada && (
                <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
                    <button
                        onClick={() => setNivelFiltro(null)}
                        style={{
                            padding: '5px 14px', borderRadius: 20, border: '1.5px solid',
                            cursor: 'pointer', fontSize: 12,
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
                                padding: '5px 14px', borderRadius: 20, border: '1.5px solid',
                                cursor: 'pointer', fontSize: 12,
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
                        <div className="empty-state-icon">🎓</div>
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
                                <div style={{ background: 'var(--negro)', color: '#fff', padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: '10px 10px 0 0' }}>
                                    <span style={{ fontWeight: 700, fontSize: 14 }}>
                                        {nivel.nombre || `Nivel ${nivel.numero}`}
                                    </span>
                                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                        <span style={{ fontSize: 11, background: 'rgba(59,130,246,0.25)', color: '#93c5fd', padding: '2px 8px', borderRadius: 20, fontWeight: 600 }}>
                                            Manana: {nivel.paralelos_matutina || 0} paralelo(s)
                                        </span>
                                        <span style={{ fontSize: 11, background: 'rgba(124,58,237,0.25)', color: '#c4b5fd', padding: '2px 8px', borderRadius: 20, fontWeight: 600 }}>
                                            Noche: {nivel.paralelos_nocturna || 0} paralelo(s)
                                        </span>
                                        <span style={{ fontSize: 11, color: '#9ca3af' }}>
                                            {asigNivel.length} / 6 asignaturas
                                        </span>
                                    </div>
                                </div>

                                {/* Modulos */}
                                {[1, 2, 3].map(numMod => {
                                    const asigsMod = asigNivel.filter(a => parseInt(a.numero_modulo) === numMod)
                                    const espaciosLibres = 2 - asigsMod.length
                                    return (
                                        <div key={numMod} style={{ borderBottom: '1px solid #f0f0f0', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 16 }}>
                                            <div style={{ minWidth: 90 }}>
                                                <span style={{
                                                    background: numMod === 1 ? '#dbeafe' : numMod === 2 ? '#fef3c7' : '#d1fae5',
                                                    color: numMod === 1 ? '#1e40af' : numMod === 2 ? '#92400e' : '#065f46',
                                                    padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700,
                                                }}>
                                                    Modulo {numMod}
                                                </span>
                                            </div>
                                            <div style={{ display: 'flex', gap: 10, flex: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                                                {asigsMod.length === 0 && (
                                                    <span style={{ fontSize: 12, color: '#9ca3af', fontStyle: 'italic' }}>Sin asignaturas</span>
                                                )}
                                                {asigsMod.map(a => (
                                                    <div key={a.id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 14px', minWidth: 200 }}>
                                                        <div style={{ fontWeight: 700, fontSize: 13, color: '#1e293b' }}>{a.nombre}</div>
                                                        <div style={{ fontSize: 11, color: '#64748b', marginTop: 3, display: 'flex', gap: 8 }}>
                                                            {a.codigo && (
                                                                <span style={{ background: '#e0f2fe', color: '#0369a1', borderRadius: 4, padding: '1px 6px' }}>{a.codigo}</span>
                                                            )}
                                                            <span>{a.horas_modulo}h</span>
                                                        </div>
                                                    </div>
                                                ))}
                                                {espaciosLibres > 0 && Array.from({ length: espaciosLibres }).map((_, i) => (
                                                    <div
                                                        key={i}
                                                        onClick={() => abrirModal(nivel.id, numMod)}
                                                        style={{ border: '2px dashed #e5e7eb', borderRadius: 8, padding: '8px 14px', minWidth: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: '#9ca3af', fontSize: 12 }}
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

            {/* Modal nueva asignatura */}
            {modal && (
                <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModal(false)}>
                    <div className="modal">
                        <div className="modal-header">
                            <h2>Nueva asignatura</h2>
                            <button className="modal-close" onClick={() => setModal(false)}>×</button>
                        </div>
                        {error && <div className="alert alert-error">{error}</div>}

                        <div className="form-row">
                            <div className="form-group">
                                <label>Nombre *</label>
                                <input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} placeholder="Logica de Programacion" />
                            </div>
                            <div className="form-group">
                                <label>Codigo</label>
                                <input value={form.codigo} onChange={e => setForm({ ...form, codigo: e.target.value })} placeholder="LP" />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Nivel *</label>
                                <select value={form.nivel_id} onChange={e => setForm({ ...form, nivel_id: e.target.value })}>
                                    {nivelesOrdenados.map(n => (
                                        <option key={n.id} value={n.id}>{n.nombre || `Nivel ${n.numero}`}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Modulo *</label>
                                <select value={form.numero_modulo} onChange={e => setForm({ ...form, numero_modulo: parseInt(e.target.value) })}>
                                    <option value={1}>Modulo 1</option>
                                    <option value={2}>Modulo 2</option>
                                    <option value={3}>Modulo 3</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Total horas por modulo *</label>
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
                                placeholder="Ej: 36"
                                min="1"
                                max="500"
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

            {/* Modal copiar malla */}
            {modalCopiar && carreraSeleccionada && (
                <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setModalCopiar(false)}>
                    <div className="modal" style={{ maxWidth: 440 }}>
                        <div className="modal-header">
                            <h2>Copiar malla curricular</h2>
                            <button className="modal-close" onClick={() => setModalCopiar(false)}>×</button>
                        </div>
                        {error && <div className="alert alert-error">{error}</div>}
                        <p style={{ fontSize: 13, color: 'var(--gris-medio)', marginBottom: 16 }}>
                            Selecciona la carrera de donde quieres copiar las asignaturas hacia <strong>{carreraSeleccionada.nombre}</strong>.
                        </p>
                        <div className="form-group">
                            <label>Carrera origen</label>
                            <select value={carreraOrigenId} onChange={e => setCarreraOrigenId(e.target.value)}>
                                <option value="">Seleccionar carrera...</option>
                                {carreras.filter(c => c.id !== carreraSeleccionada.id).map(c => (
                                    <option key={c.id} value={c.id}>{c.nombre} — {c.sede || 'Quito'}</option>
                                ))}
                            </select>
                        </div>
                        <div className="alert alert-info" style={{ fontSize: 12 }}>
                            Solo se copiaran asignaturas que no existan ya en la carrera destino.
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setModalCopiar(false)}>Cancelar</button>
                            <button className="btn btn-primary" onClick={ejecutarCopia} disabled={copiando || !carreraOrigenId}>
                                {copiando ? 'Copiando...' : 'Copiar malla'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}