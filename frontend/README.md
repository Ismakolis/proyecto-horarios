# Sistema de Horarios ITQ — Frontend

**Instituto Superior Tecnológico Quito**  
Interfaz web para la gestión de horarios académicos.

---

## Stack

- **Framework:** React 18 + Vite
- **Routing:** React Router v6
- **HTTP:** Axios
- **Diseño:** CSS Variables — UI estilo Kenjo, responsivo

---

## Instalación local

### 1. Instalar dependencias

```bash
cd frontend
npm install
```

### 2. Configurar URL del backend

Crear archivo `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api
```

### 3. Iniciar servidor de desarrollo

```bash
npm run dev
```

App disponible en: http://localhost:5173

### 4. Build para producción

```bash
npm run build
```

El build queda en `frontend/dist/`.

---

## Deploy en Vercel

1. Conectar repositorio en vercel.com → New Project
2. **Root Directory:** `proyecto-horarios/frontend`
3. **Framework Preset:** Vite
4. Agregar variable de entorno:
   - `VITE_API_URL` → `https://tu-backend.onrender.com/api`
5. Deploy

> El archivo `vercel.json` ya está configurado para manejar el routing de la SPA correctamente.

---

## Estructura

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Docentes.jsx
│   │   ├── Carreras.jsx
│   │   ├── Asignaturas.jsx
│   │   ├── Periodos.jsx
│   │   ├── Horarios.jsx
│   │   ├── Reportes.jsx
│   │   └── MisHorarios.jsx
│   ├── components/
│   │   └── Layout.jsx       # Sidebar responsivo con hamburger
│   ├── context/
│   │   └── AuthContext.jsx  # Sesión JWT global
│   ├── services/
│   │   └── api.js           # Cliente Axios centralizado
│   └── index.css            # Sistema de diseño completo
├── vercel.json              # Configuración SPA routing
└── .env.production          # URL backend producción
```

---

## Módulos del sistema

| Página | Descripción |
|--------|-------------|
| Dashboard | Resumen estadístico del sistema |
| Docentes | CRUD, acceso al sistema, habilidades |
| Carreras | Gestión por sede (Quito / Conocoto) |
| Asignaturas | Malla curricular por nivel y módulo |
| Períodos | Períodos académicos y módulos |
| Horarios | Generación con IA, visualización y edición |
| Reportes | Exportación Excel por carrera, nivel o docente |
| Mis Horarios | Vista del docente autenticado |