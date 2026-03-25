# Sistema de Horarios ITQ
**Instituto Superior Tecnológico Quito — Carrera de Desarrollo de Software**

## Stack Tecnológico
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** React + Material UI
- **IA:** Anthropic Claude API
- **Exportación:** openpyxl (Excel)

---

## Instalación y Configuración

### 1. Clonar y preparar backend

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL y API Key
```

### 3. Crear base de datos en PostgreSQL

```sql
CREATE DATABASE horarios_itq;
```

O usando Supabase: crear proyecto y copiar la connection string.

### 4. Inicializar migraciones con Alembic

```bash
alembic init alembic
alembic revision --autogenerate -m "inicial"
alembic upgrade head
```

### 5. Ejecutar backend

```bash
uvicorn main:app --reload --port 8000
```
API disponible en: http://localhost:8000
Docs automáticas en: http://localhost:8000/docs

---

### 6. Instalar y ejecutar frontend

```bash
cd frontend
npm install
npm start
```
App disponible en: http://localhost:3000

---

## Estructura del Proyecto

```
proyecto-horarios/
├── backend/
│   ├── main.py              # Entrada principal FastAPI
│   ├── database.py          # Conexión PostgreSQL
│   ├── models/
│   │   └── models.py        # Tablas SQLAlchemy
│   ├── schemas/             # Pydantic (validación de datos)
│   ├── routes/              # Endpoints de la API
│   ├── services/            # Lógica de negocio
│   └── utils/               # Helpers (JWT, Excel, IA)
└── frontend/
    └── src/
        ├── pages/           # Páginas por rol
        ├── components/      # Componentes reutilizables
        ├── services/        # Llamadas a la API
        └── context/         # Estado global (auth)
```

---

## Reglas de Negocio Implementadas

| Regla | Descripción |
|-------|-------------|
| Máx. asignaturas | Cada docente máximo 3 asignaturas por módulo |
| Jornada matutina | 08:00 - 12:00, asignaturas de 2 horas |
| Jornada nocturna | 18:30 - 21:30, asignaturas de 1.5 horas |
| Carga TC mínima | 272 horas por período (tiempo completo) |
| Carga TC máxima | 380 horas por período (tiempo completo) |
| Sin choques | Un docente no puede tener 2 clases al mismo tiempo |
| Paralelos | Configurable por período académico |

---

## Roles del Sistema

| Rol | Permisos |
|-----|----------|
| Coordinador | CRUD completo, generar horarios, exportar Excel |
| Docente | Ver sus propios horarios |
| Administrativo | Ver reportes y horarios (solo lectura) |