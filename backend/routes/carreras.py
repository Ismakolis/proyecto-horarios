from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from schemas.carreras import (
    CarreraCreate, CarreraUpdate, CarreraResponse,
    CarreraConNivelesResponse,
    NivelCreate, NivelUpdate, NivelResponse,
    AsignaturaCreate, AsignaturaUpdate, AsignaturaResponse
)
from services.carreras_service import (
    crear_carrera, listar_carreras, obtener_carrera,
    actualizar_carrera, eliminar_carrera, agregar_nivel, actualizar_nivel,
    crear_asignatura, listar_asignaturas, actualizar_asignatura
)
from utils.jwt import solo_coordinador, cualquier_rol
from models.models import Usuario, Nivel

router = APIRouter()

# ─── ASIGNATURAS (primero para evitar conflicto con /{carrera_id}) ────────────

@router.post("/asignaturas", response_model=AsignaturaResponse, status_code=201)
async def crear_asig(
    data: AsignaturaCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await crear_asignatura(data, db)


@router.get("/asignaturas/lista", response_model=List[AsignaturaResponse])
async def listar_asig(
    carrera_id: Optional[str] = Query(None),
    nivel_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await listar_asignaturas(db, carrera_id, nivel_id)


@router.put("/asignaturas/{asignatura_id}", response_model=AsignaturaResponse)
async def actualizar_asig(
    asignatura_id: str,
    data: AsignaturaUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await actualizar_asignatura(asignatura_id, data, db)


# ─── CARRERAS ─────────────────────────────────────────────────────────────────

@router.post("/", response_model=CarreraResponse, status_code=201)
async def crear(
    data: CarreraCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await crear_carrera(data, db)


@router.get("/", response_model=List[CarreraConNivelesResponse])
async def listar(
    activo: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await listar_carreras(db, activo)


@router.get("/{carrera_id}", response_model=CarreraResponse)
async def obtener(
    carrera_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await obtener_carrera(carrera_id, db)


@router.put("/{carrera_id}", response_model=CarreraResponse)
async def actualizar(
    carrera_id: str,
    data: CarreraUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await actualizar_carrera(carrera_id, data, db)


@router.delete("/{carrera_id}")
async def eliminar(
    carrera_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await eliminar_carrera(carrera_id, db)


# ─── NIVELES ──────────────────────────────────────────────────────────────────

@router.post("/{carrera_id}/niveles", response_model=NivelResponse, status_code=201)
async def agregar_nivel_a_carrera(
    carrera_id: str,
    data: NivelCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await agregar_nivel(carrera_id, data, db)


@router.put("/{carrera_id}/niveles/{nivel_id}", response_model=NivelResponse)
async def actualizar_nivel_route(
    carrera_id: str,
    nivel_id: str,
    data: NivelUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Actualizar paralelos matutina/nocturna de un nivel"""
    return await actualizar_nivel(carrera_id, nivel_id, data, db)