from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from schemas.periodos import (
    PeriodoCreate, PeriodoUpdate, PeriodoResponse,
    PeriodoListResponse, ModuloCreate, ModuloResponse
)
from services.periodos_service import (
    crear_periodo, listar_periodos, obtener_periodo,
    actualizar_periodo, agregar_modulo
)
from utils.jwt import solo_coordinador, cualquier_rol
from models.models import Usuario

router = APIRouter()


@router.post("/", response_model=PeriodoResponse, status_code=201)
async def crear(
    data: PeriodoCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Crear un período académico con sus módulos"""
    return await crear_periodo(data, db)


@router.get("/", response_model=List[PeriodoListResponse])
async def listar(
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    """Listar todos los períodos académicos"""
    return await listar_periodos(db)


@router.get("/{periodo_id}", response_model=PeriodoResponse)
async def obtener(
    periodo_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(cualquier_rol),
):
    """Obtener un período con sus módulos"""
    return await obtener_periodo(periodo_id, db)


@router.put("/{periodo_id}", response_model=PeriodoResponse)
async def actualizar(
    periodo_id: str,
    data: PeriodoUpdate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Actualizar un período académico"""
    return await actualizar_periodo(periodo_id, data, db)


@router.post("/{periodo_id}/modulos", response_model=ModuloResponse, status_code=201)
async def agregar_modulo_a_periodo(
    periodo_id: str,
    data: ModuloCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    """Agregar un módulo a un período existente"""
    return await agregar_modulo(periodo_id, data, db)