import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './context/useAuth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Docentes from './pages/Docentes'
import Carreras from './pages/Carreras'
import Periodos from './pages/Periodos'
import Horarios from './pages/Horarios'
import Layout from './components/Layout'
import Asignaturas from './pages/Asignaturas'
import Reportes from './pages/Reportes'
import MisHorarios from './pages/MisHorarios'


function RutaProtegida({ children }) {
  const { usuario, cargando } = useAuth()
  if (cargando) return <div className="loading">Cargando...</div>
  return usuario ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<RutaProtegida><Layout /></RutaProtegida>}>
            <Route index element={<Dashboard />} />
            <Route path="docentes" element={<Docentes />} />
            <Route path="carreras" element={<Carreras />} />
            <Route path="periodos" element={<Periodos />} />
            <Route path="horarios" element={<Horarios />} />
            <Route path="asignaturas" element={<Asignaturas />} />
            <Route path="reportes" element={<Reportes />} />
            <Route path="mis-horarios" element={<MisHorarios />} />
          </Route>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}