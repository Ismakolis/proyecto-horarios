import { useState } from 'react'
import { AuthContext } from './AuthContextValue'

const getUsuarioInicial = () => {
  try {
    const u = localStorage.getItem('usuario')
    const t = localStorage.getItem('token')
    if (u && t) return JSON.parse(u)
  } catch {
    return null
  }
  return null
}

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(getUsuarioInicial)
  const [cargando] = useState(false)

  const iniciarSesion = (token, userData) => {
    localStorage.setItem('token', token)
    localStorage.setItem('usuario', JSON.stringify(userData))
    setUsuario(userData)
  }

  const cerrarSesion = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
    setUsuario(null)
  }

  const esCoordinador = usuario?.rol === 'coordinador'
  const esDocente = usuario?.rol === 'docente'
  const esAdministrativo = usuario?.rol === 'administrativo'

  return (
    <AuthContext.Provider value={{ usuario, cargando, iniciarSesion, cerrarSesion, esCoordinador, esDocente, esAdministrativo }}>
      {children}
    </AuthContext.Provider>
  )
}