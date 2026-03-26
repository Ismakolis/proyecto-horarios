# Sistema de Horarios ITQ — Backend

**Instituto Superior Tecnológico Quito**  
API REST para generación automática de horarios académicos.

---

## Stack

- **Framework:** FastAPI + Uvicorn
- **Base de datos:** PostgreSQL (asyncpg + SQLAlchemy async)
- **Autenticación:** JWT (Bearer Token)
- **IA:** Groq API — LLaMA 3.3-70b (gratis en console.groq.com)
- **Reportes:** openpyxl (Excel)

---

## Instalación local

### 1. Crear entorno virtual

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://usuario:contraseña@localhost:5432/horarios_itq
SECRET_KEY=clave_secreta_larga_y_aleatoria
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
FRONTEND_URL=http://localhost:5173
```

> Obtén tu GROQ_API_KEY gratis en: https://console.groq.com

### 4. Crear la base de datos en PostgreSQL

```sql
CREATE DATABASE horarios_itq;
```

### 5. Iniciar el servidor

```bash
uvicorn main:app --reload --port 8000
```

- API: http://localhost:8000
- Documentación: http://localhost:8000/docs

### 6. Crear usuario administrador

```bash
curl -X POST http://localhost:8000/api/auth/seed-admin
```

Credenciales iniciales:
- **Email:** admin@itq.edu.ec
- **Contraseña:** Admin123

> ⚠️ Cambiar la contraseña inmediatamente en producción.

---

## Deploy en Render

1. Conectar repositorio en render.com → New Web Service
2. **Root Directory:** `proyecto-horarios/backend`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Agregar variables de entorno en Render:
   - `DATABASE_URL` — URL interna de PostgreSQL en Render
   - `SECRET_KEY` — clave secreta aleatoria
   - `GROQ_API_KEY` — clave de Groq
   - `FRONTEND_URL` — URL de Vercel (ej: https://tu-app.vercel.app)

> La URL de PostgreSQL en Render empieza con `postgres://` — el sistema la convierte automáticamente al formato correcto.

---

## Estructura

```
backend/
├── main.py              # Entrada FastAPI, CORS, rutas
├── database.py          # Conexión PostgreSQL async
├── models/
│   └── models.py        # Modelos SQLAlchemy (tablas)
├── schemas/             # Validación con Pydantic
├── routes/              # Endpoints HTTP por módulo
├── services/            # Lógica de negocio
└── utils/
    ├── jwt.py           # Autenticación y roles
    └── excel.py         # Generación de reportes Excel
```

---

## Reglas de negocio

| Regla | Descripción |
|-------|-------------|
| Máx. asignaturas | 3 por docente por módulo (global entre sedes) |
| Habilidades | Docentes solo dictan materias asignadas |
| Sin choques | Un docente no puede estar en 2 lugares a la misma hora |
| Jornada matutina | Bloques 08:00-10:00 y 10:00-12:00 |
| Jornada nocturna | Bloques 18:30-20:00 y 20:00-21:30 |
| Carga TC mínima | 272h por período académico |
| Carga TC máxima | 380h por período académico |
| Multisede | Quito y Conocoto — docentes compartidos con límite global |

---

## Roles

| Rol | Acceso |
|-----|--------|
| coordinador | CRUD completo, generar horarios, exportar Excel |
| docente | Solo sus propios horarios |
