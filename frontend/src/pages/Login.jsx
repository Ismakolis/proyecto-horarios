import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUsuario } from '../services/api'
import { useAuth } from '../context/useAuth'

export default function Login() {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [cargando, setCargando] = useState(false)
  const { iniciarSesion }       = useAuth()
  const navigate                = useNavigate()

  const validar = () => {
    if (!email.trim()) return 'El email es obligatorio'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Ingresa un email válido'
    if (!password)     return 'La contraseña es obligatoria'
    if (password.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
    return null
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    const err = validar()
    if (err) { setError(err); return }
    setCargando(true); setError('')
    try {
      const res = await loginUsuario({ email: email.trim(), password })
      iniciarSesion(res.data.access_token, res.data.usuario)
      navigate(res.data.usuario.rol === 'docente' ? '/mis-horarios' : '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Credenciales incorrectas')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-page">
      {/* Panel izquierdo — branding */}
      <div className="login-left">
        <div className="login-brand">
          <div className="login-brand-logo">
            <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="3"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <h1>Sistema de Gestión de Horarios Académicos</h1>
          <p>Planificación inteligente de horarios para el Instituto Superior Tecnológico Quito.</p>
          <div className="login-features">
            <div className="login-feature">
              <div className="login-feature-dot" />
              Generación automática de horarios por jornada
            </div>
            <div className="login-feature">
              <div className="login-feature-dot" />
              Control de carga horaria docente TC y TP
            </div>
            <div className="login-feature">
              <div className="login-feature-dot" />
              Reportes en Excel por carrera, nivel y docente
            </div>
            <div className="login-feature">
              <div className="login-feature-dot" />
              Gestión de sedes Quito y Conocoto
            </div>
          </div>
        </div>
      </div>

      {/* Panel derecho — formulario */}
      <div className="login-right">
        <div className="login-box">
          <div className="login-box-header">
            <h2>Iniciar sesión</h2>
            <p>Ingresa tus credenciales institucionales</p>
          </div>

          <form onSubmit={handleLogin} noValidate>
            {error && <div className="error-msg">{error}</div>}

            <div className="form-group">
              <label>Correo institucional</label>
              <input
                type="email" value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="usuario@itq.edu.ec"
                autoComplete="email" autoFocus
              />
            </div>

            <div className="form-group">
              <label>Contraseña</label>
              <input
                type="password" value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
                autoComplete="current-password"
              />
            </div>

            <button type="submit" className="btn-login" disabled={cargando}>
              {cargando ? 'Ingresando...' : 'Ingresar al sistema'}
            </button>
          </form>

          <p style={{ marginTop: 20, fontSize: 11, color: '#94a3b8', textAlign: 'center' }}>
            ITQ — Instituto Superior Tecnológico Quito
          </p>
        </div>
      </div>
    </div>
  )
}
