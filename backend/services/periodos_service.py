from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.models import PeriodoAcademico, Modulo
from schemas.periodos import PeriodoCreate, PeriodoUpdate, ModuloCreate
import uuid


async def crear_periodo(data: PeriodoCreate, db: AsyncSession) -> PeriodoAcademico:
    # Verificar que no exista el mismo período en ese año
    r = await db.execute(
        select(PeriodoAcademico).where(
            PeriodoAcademico.anio == data.anio,
            PeriodoAcademico.numero == data.numero
        )
    )
    if r.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe el período {data.numero} del año {data.anio}"
        )

    periodo_id = str(uuid.uuid4())
    periodo = PeriodoAcademico(
        id=periodo_id,
        nombre=data.nombre,
        anio=data.anio,
        numero=data.numero,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        paralelos_por_nivel=data.paralelos_por_nivel,
    )
    db.add(periodo)
    await db.flush()

    # Crear módulos si se enviaron
    for mod in data.modulos or []:
        modulo = Modulo(
            id=str(uuid.uuid4()),
            periodo_id=periodo_id,
            numero=mod.numero,
            nombre=mod.nombre or f"Módulo {mod.numero}",
            fecha_inicio=mod.fecha_inicio,
            fecha_fin=mod.fecha_fin,
        )
        db.add(modulo)

    await db.flush()

    r = await db.execute(
        select(PeriodoAcademico)
        .options(selectinload(PeriodoAcademico.modulos))
        .where(PeriodoAcademico.id == periodo_id)
    )
    return r.scalar_one()


async def listar_periodos(db: AsyncSession) -> list:
    from sqlalchemy.orm import selectinload
    r = await db.execute(
        select(PeriodoAcademico)
        .options(selectinload(PeriodoAcademico.modulos))
        .order_by(PeriodoAcademico.anio.desc(), PeriodoAcademico.numero.desc())
    )
    return r.scalars().all()

async def obtener_periodo(periodo_id: str, db: AsyncSession) -> PeriodoAcademico:
    r = await db.execute(
        select(PeriodoAcademico)
        .options(selectinload(PeriodoAcademico.modulos))
        .where(PeriodoAcademico.id == periodo_id)
    )
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")
    return periodo


async def actualizar_periodo(periodo_id: str, data: PeriodoUpdate, db: AsyncSession) -> PeriodoAcademico:
    periodo = await obtener_periodo(periodo_id, db)
    if data.nombre is not None:
        periodo.nombre = data.nombre
    if data.paralelos_por_nivel is not None:
        periodo.paralelos_por_nivel = data.paralelos_por_nivel
    if data.activo is not None:
        periodo.activo = data.activo
    await db.flush()
    await db.refresh(periodo)
    return periodo


async def agregar_modulo(periodo_id: str, data: ModuloCreate, db: AsyncSession) -> Modulo:
    await obtener_periodo(periodo_id, db)

    # Verificar que el número de módulo no esté repetido
    r = await db.execute(
        select(Modulo).where(
            Modulo.periodo_id == periodo_id,
            Modulo.numero == data.numero
        )
    )
    if r.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe el módulo {data.numero} en este período"
        )

    modulo = Modulo(
        id=str(uuid.uuid4()),
        periodo_id=periodo_id,
        numero=data.numero,
        nombre=data.nombre or f"Módulo {data.numero}",
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
    )
    db.add(modulo)
    await db.flush()
    await db.refresh(modulo)
    return modulo