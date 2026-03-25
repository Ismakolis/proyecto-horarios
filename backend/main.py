"""
main.py
Punto de entrada de la API REST del Sistema de Horarios ITQ.
Configura FastAPI, CORS, ciclo de vida y registro de rutas.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicacion: crea tablas al iniciar."""
    await create_tables()
    print("Base de datos conectada y tablas verificadas")
    yield
    print("Servidor apagado")


app = FastAPI(
    title="Sistema de Horarios ITQ",
    description="""
    API REST para la generacion automatica de horarios academicos
    del Instituto Superior Tecnologico Quito.

    Primer uso:
    1. Llama a POST /api/auth/seed-admin para crear el usuario admin inicial
    2. Usa POST /api/auth/login con admin@itq.edu.ec / Admin123
    3. Copia el token y usalo en el boton Authorize
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# Configuracion de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        os.getenv("FRONTEND_URL", "*"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers por modulo funcional
from routes.auth import router as auth_router
from routes.docentes import router as docentes_router
from routes.carreras import router as carreras_router
from routes.periodos import router as periodos_router
from routes.horarios import router as horarios_router
from routes.reportes import router as reportes_router

app.include_router(auth_router,     prefix="/api/auth",     tags=["Autenticacion"])
app.include_router(docentes_router, prefix="/api/docentes", tags=["Docentes"])
app.include_router(carreras_router, prefix="/api/carreras", tags=["Carreras y Asignaturas"])
app.include_router(periodos_router, prefix="/api/periodos", tags=["Periodos y Modulos"])
app.include_router(horarios_router, prefix="/api/horarios", tags=["Horarios"])
app.include_router(reportes_router, prefix="/api/reportes", tags=["Reportes y Excel"])


@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raiz para verificar que la API esta activa."""
    return {"sistema": "Horarios ITQ", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Sistema"])
async def health():
    """Health check para monitoreo del servidor."""
    return {"estado": "ok"}
