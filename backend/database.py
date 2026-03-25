"""
database.py
Configuracion de la conexion a PostgreSQL usando SQLAlchemy async.
Provee la sesion de base de datos y la funcion de creacion de tablas.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

# URL de conexion a la base de datos (configurable por variable de entorno)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/horarios_itq"
)

# Motor asincrono con pool de conexiones
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver queries en desarrollo
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Fabrica de sesiones asincronas
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass


async def get_db():
    """
    Dependencia de FastAPI que provee una sesion de base de datos.
    Hace commit automatico al finalizar o rollback en caso de error.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Crea todas las tablas definidas en los modelos si no existen."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
