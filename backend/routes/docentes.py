"""
routes/docentes.py
Endpoints de docentes, acceso de usuarios y habilidades.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from schemas.docentes import (
    DocenteCreate, DocenteUpdate, DocenteResponse, DocenteListResponse,
    CrearAccesoDocente, HabilidadDocenteCreate
)
from services.docentes_service import (
    crear_docente, listar_docentes, obtener_docente,
    actualizar_docente, crear_acceso_docente,
    obtener_habilidades, actualizar_habilidades
)
from utils.jwt import solo_coordinador, cualquier_rol
from models.models import Usuario

router = APIRouter()


@router.post("/", status_code=201)
async def crear(
    data: DocenteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await crear_docente(data, db)


@router.get("/")
async def listar(
    activo: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await listar_docentes(db, activo)


@router.get("/{docente_id}")
async def obtener(
    docente_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await obtener_docente(docente_id, db)


@router.put("/{docente_id}")
async def actualizar(
    docente_id: str,
    data: DocenteUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await actualizar_docente(docente_id, data, db)


@router.post("/crear-acceso", status_code=201)
async def crear_acceso(
    data: CrearAccesoDocente,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Crea usuario y contrasena para que el docente pueda iniciar sesion."""
    return await crear_acceso_docente(data, db)


@router.get("/{docente_id}/habilidades")
async def get_habilidades(
    docente_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    return await obtener_habilidades(docente_id, db)


@router.put("/{docente_id}/habilidades")
async def set_habilidades(
    docente_id: str,
    data: HabilidadDocenteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await actualizar_habilidades(docente_id, data, db)
