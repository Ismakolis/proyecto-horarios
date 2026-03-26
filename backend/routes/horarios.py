from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from schemas.horarios import HorarioCreate, HorarioUpdate, HorarioResponse, GenerarHorarioRequest
from services.horarios_service import (
    crear_horario, listar_horarios, actualizar_horario,
    eliminar_horario, generar_horarios_automatico, generar_horarios_con_ia
)
from utils.jwt import solo_coordinador, coordinador_o_admin, cualquier_rol
from models.models import Usuario

router = APIRouter()


@router.post("/", response_model=HorarioResponse, status_code=201)
async def crear(
    data: HorarioCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Crear un horario manualmente con validaciones activas"""
    return await crear_horario(data, db)


@router.get("/", response_model=List[HorarioResponse])
async def listar(
    periodo_id: Optional[str] = Query(None),
    modulo_id: Optional[str] = Query(None),
    carrera_id: Optional[str] = Query(None),
    docente_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    """Listar horarios con filtros opcionales"""
    return await listar_horarios(db, periodo_id, modulo_id, carrera_id, docente_id)


@router.put("/{horario_id}", response_model=HorarioResponse)
async def actualizar(
    horario_id: str,
    data: HorarioUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Editar un horario con validaciones activas"""
    return await actualizar_horario(horario_id, data, db)


@router.delete("/{horario_id}")
async def eliminar(
    horario_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Eliminar un horario"""
    return await eliminar_horario(horario_id, db)


@router.post("/generar")
async def generar(
    data: GenerarHorarioRequest,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """
    Generar horarios para una carrera en un modulo.
    Si usar_ia=true, Claude propone la distribucion optima.
    Si usar_ia=false, usa el algoritmo automatico del sistema.
    Respeta todas las reglas: max 3 asignaturas por docente, sin choques, carga horaria TC.
    """
    if data.usar_ia:
        return await generar_horarios_con_ia(data, db)
    return await generar_horarios_automatico(data, db)