/**
 * Login.jsx
 * Pagina de inicio de sesion del sistema.
 * Redirige al docente a /mis-horarios y a los demas roles al dashboard.
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUsuario } from '../services/api'
import { useAuth } from '../context/useAuth'

export default function Login() {
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [cargando, setCargando] = useState(false)

  const { iniciarSesion } = useAuth()
  const navigate = useNavigate()

  /**
   * Maneja el envio del formulario de login.
   * Autentica al usuario y redirige segun su rol.
   */
  const handleLogin = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Ingresa tu email y contraseña')
      return
    }
    setCargando(true)
    setError('')
    try {
      const res = await loginUsuario({ email, password })
      iniciarSesion(res.data.access_token, res.data.usuario)
      // Redirigir segun rol
      navigate(res.data.usuario.rol === 'docente' ? '/mis-horarios' : '/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Credenciales incorrectas')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-box">
        {/* Logo */}
        <div className="login-logo">
          <div className="login-logo-icon">ITQ</div>
          <h1>Instituto Superior Tecnologico Quito</h1>
          <p>Sistema de Gestion de Horarios Academicos</p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleLogin}>
          {error && <div className="error-msg">{error}</div>}

          <div className="form-group">
            <label>Correo institucional</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="usuario@itq.edu.ec"
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña"
              autoComplete="current-password"
            />
          </div>

          <button type="submit" className="btn-login" disabled={cargando}>
            {cargando ? 'Ingresando...' : 'Ingresar al sistema'}
          </button>
        </form>
      </div>
    </div>
  )
}
