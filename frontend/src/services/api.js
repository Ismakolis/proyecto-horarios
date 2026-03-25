/**
 * api.js
 * Cliente HTTP centralizado para comunicacion con el backend.
 * Maneja autenticacion JWT automatica y redireccion por sesion expirada.
 */

import axios from 'axios'

// Instancia base de Axios apuntando al backend
const API = axios.create({
  baseURL: 'http://localhost:8000/api',
})

// Interceptor de peticion: agrega el token JWT si existe
API.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Interceptor de respuesta: redirige al login si el token expira
API.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Autenticacion
export const loginUsuario      = (data) => API.post('/auth/login', data)
export const getMe             = ()     => API.get('/auth/me')
export const registrarUsuario  = (data) => API.post('/auth/registro', data)

// Docentes
export const getDocentes          = (activo) => API.get('/docentes/', { params: { activo } })
export const getDocente           = (id)     => API.get(`/docentes/${id}`)
export const createDocente        = (data)   => API.post('/docentes/', data)
export const updateDocente        = (id, data) => API.put(`/docentes/${id}`, data)
export const deleteDocente        = (id)     => API.delete(`/docentes/${id}`)
export const updateDisponibilidad = (id, data) => API.put(`/docentes/${id}/disponibilidad`, data)

// Carreras y asignaturas
export const getCarreras      = ()           => API.get('/carreras/')
export const getCarrera       = (id)         => API.get(`/carreras/${id}`)
export const createCarrera    = (data)       => API.post('/carreras/', data)
export const updateCarrera    = (id, data)   => API.put(`/carreras/${id}`, data)
export const getAsignaturas   = (carreraId, nivelId) =>
  API.get('/carreras/asignaturas/lista', { params: { carrera_id: carreraId, nivel_id: nivelId } })
export const createAsignatura = (data)       => API.post('/carreras/asignaturas', data)
export const updateAsignatura = (id, data)   => API.put(`/carreras/asignaturas/${id}`, data)
export const updateNivel      = (carreraId, nivelId, data) =>
  API.put(`/carreras/${carreraId}/niveles/${nivelId}`, data)

// Periodos academicos
export const getPeriodos    = ()         => API.get('/periodos/')
export const getPeriodo     = (id)       => API.get(`/periodos/${id}`)
export const createPeriodo  = (data)     => API.post('/periodos/', data)
export const updatePeriodo  = (id, data) => API.put(`/periodos/${id}`, data)

// Horarios
export const getHorarios     = (params)     => API.get('/horarios/', { params })
export const createHorario   = (data)       => API.post('/horarios/', data)
export const updateHorario   = (id, data)   => API.put(`/horarios/${id}`, data)
export const deleteHorario   = (id)         => API.delete(`/horarios/${id}`)
export const generarHorarios = (data)       => API.post('/horarios/generar', data)

// Reportes Excel
export const exportarExcel = (periodoId) =>
  API.get(`/reportes/excel/${periodoId}`, { responseType: 'blob' })

export const exportarExcelDocente = (docenteId, periodoId) =>
  API.get(`/reportes/excel/docente/${docenteId}`, { params: { periodo_id: periodoId }, responseType: 'blob' })

export const exportarExcelCarrera = (carreraId, periodoId) =>
  API.get(`/reportes/excel/carrera/${carreraId}`, { params: { periodo_id: periodoId }, responseType: 'blob' })

export const exportarExcelNivel = (nivelId, periodoId) =>
  API.get(`/reportes/excel/nivel/${nivelId}`, { params: { periodo_id: periodoId }, responseType: 'blob' })
