from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from schemas.docentes import DocenteCreate, DocenteUpdate, DocenteResponse, DocenteListResponse, DisponibilidadBase
from services.docentes_service import (
    crear_docente, listar_docentes, obtener_docente,
    actualizar_docente, eliminar_docente, actualizar_disponibilidad
)
from utils.jwt import solo_coordinador, coordinador_o_admin, cualquier_rol
from models.models import Usuario, RolUsuario

router = APIRouter()


@router.post("/", response_model=DocenteResponse, status_code=201)
async def crear(
    data: DocenteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Crear un nuevo docente (solo coordinador)"""
    return await crear_docente(data, db)


@router.get("/", response_model=List[DocenteListResponse])
async def listar(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    """Listar todos los docentes"""
    return await listar_docentes(db, activo)


@router.get("/{docente_id}", response_model=DocenteResponse)
async def obtener(
    docente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(cualquier_rol),
):
    """
    Obtener un docente por ID.
    Los docentes solo pueden ver su propio perfil.
    """
    from models import RolUsuario
    # Si es docente, verificar que sea su propio perfil
    if current_user.rol == RolUsuario.DOCENTE:
        if not current_user.docente or current_user.docente.id != docente_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Solo puedes ver tu propio perfil")
    return await obtener_docente(docente_id, db)


@router.put("/{docente_id}", response_model=DocenteResponse)
async def actualizar(
    docente_id: str,
    data: DocenteUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Actualizar datos de un docente (solo coordinador)"""
    return await actualizar_docente(docente_id, data, db)


@router.delete("/{docente_id}")
async def eliminar(
    docente_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Desactivar un docente (soft delete, solo coordinador)"""
    return await eliminar_docente(docente_id, db)


@router.put("/{docente_id}/disponibilidad")
async def set_disponibilidad(
    docente_id: str,
    disponibilidades: List[DisponibilidadBase],
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """
    Reemplazar completamente la disponibilidad de un docente.
    Enviar lista vacía [] para borrar toda disponibilidad.
    """
    return await actualizar_disponibilidad(docente_id, disponibilidades, db)