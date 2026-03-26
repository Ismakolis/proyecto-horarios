from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.models import Carrera, Nivel, Asignatura
from schemas.carreras import CarreraCreate, CarreraUpdate, AsignaturaCreate, AsignaturaUpdate, NivelCreate, NivelUpdate
import uuid


# ─── CARRERAS ────────────────────────────────────────────────────────────────

async def crear_carrera(data: CarreraCreate, db: AsyncSession) -> Carrera:
    # Verificar código único
    r = await db.execute(select(Carrera).where(Carrera.codigo == data.codigo))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Ya existe una carrera con el código {data.codigo}")

    carrera_id = str(uuid.uuid4())
    carrera = Carrera(
        id=carrera_id,
        nombre=data.nombre,
        codigo=data.codigo,
        sede=data.sede,
        descripcion=data.descripcion,
    )
    db.add(carrera)
    await db.flush()

    # Crear niveles si se enviaron
    for niv in data.niveles or []:
        nivel = Nivel(
            id=str(uuid.uuid4()),
            carrera_id=carrera_id,
            numero=niv.numero,
            nombre=niv.nombre or f"Nivel {niv.numero}",
            paralelos_matutina=niv.paralelos_matutina,
            paralelos_nocturna=niv.paralelos_nocturna,
            jornada_habilitada=niv.jornada_habilitada,
        )
        db.add(nivel)
    await db.flush()

    r = await db.execute(
        select(Carrera)
        .options(selectinload(Carrera.niveles))
        .where(Carrera.id == carrera_id)
    )
    return r.scalar_one()


async def listar_carreras(db: AsyncSession, activo: bool = None) -> list:
    from sqlalchemy.orm import selectinload
    query = select(Carrera).options(selectinload(Carrera.niveles)).order_by(Carrera.nombre)
    if activo is not None:
        query = query.where(Carrera.activo == activo)
    r = await db.execute(query)
    return r.scalars().all()


async def obtener_carrera(carrera_id: str, db: AsyncSession) -> Carrera:
    r = await db.execute(
        select(Carrera)
        .options(selectinload(Carrera.niveles))
        .where(Carrera.id == carrera_id)
    )
    carrera = r.scalar_one_or_none()
    if not carrera:
        raise HTTPException(status_code=404, detail="Carrera no encontrada")
    return carrera


async def actualizar_carrera(carrera_id: str, data: CarreraUpdate, db: AsyncSession) -> Carrera:
    carrera = await obtener_carrera(carrera_id, db)
    if data.nombre is not None:
        carrera.nombre = data.nombre
    if data.descripcion is not None:
        carrera.descripcion = data.descripcion
    if data.sede is not None:
        carrera.sede = data.sede
    if data.activo is not None:
        carrera.activo = data.activo
    await db.flush()
    await db.refresh(carrera)
    return carrera


async def eliminar_carrera(carrera_id: str, db: AsyncSession):
    carrera = await obtener_carrera(carrera_id, db)
    carrera.activo = False
    await db.flush()
    return {"mensaje": f"Carrera {carrera.nombre} desactivada correctamente"}


# ─── NIVELES ──────────────────────────────────────────────────────────────────

async def agregar_nivel(carrera_id: str, data: NivelCreate, db: AsyncSession) -> Nivel:
    await obtener_carrera(carrera_id, db)

    r = await db.execute(
        select(Nivel).where(Nivel.carrera_id == carrera_id, Nivel.numero == data.numero)
    )
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Ya existe el nivel {data.numero} en esta carrera")

    nivel = Nivel(
        id=str(uuid.uuid4()),
        carrera_id=carrera_id,
        numero=data.numero,
        nombre=data.nombre or f"Nivel {data.numero}",
        paralelos_matutina=data.paralelos_matutina,
        paralelos_nocturna=data.paralelos_nocturna,
        jornada_habilitada=getattr(data, 'jornada_habilitada', 'ambas'),
    )
    db.add(nivel)
    await db.flush()
    await db.refresh(nivel)
    return nivel


async def actualizar_nivel(carrera_id: str, nivel_id: str, data, db: AsyncSession) -> Nivel:
    r = await db.execute(
        select(Nivel).where(Nivel.id == nivel_id, Nivel.carrera_id == carrera_id)
    )
    nivel = r.scalar_one_or_none()
    if not nivel:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    if data.paralelos_matutina is not None:
        nivel.paralelos_matutina = data.paralelos_matutina
    if data.paralelos_nocturna is not None:
        nivel.paralelos_nocturna = data.paralelos_nocturna
    if data.jornada_habilitada is not None:
        nivel.jornada_habilitada = data.jornada_habilitada
    await db.flush()
    await db.refresh(nivel)
    return nivel


# ─── ASIGNATURAS ──────────────────────────────────────────────────────────────

async def crear_asignatura(data: AsignaturaCreate, db: AsyncSession) -> Asignatura:
    # Verificar que la carrera y nivel existen
    r = await db.execute(select(Carrera).where(Carrera.id == data.carrera_id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Carrera no encontrada")

    r = await db.execute(
        select(Nivel).where(Nivel.id == data.nivel_id, Nivel.carrera_id == data.carrera_id)
    )
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Nivel no encontrado en esta carrera")

    asignatura = Asignatura(
        id=str(uuid.uuid4()),
        carrera_id=data.carrera_id,
        nivel_id=data.nivel_id,
        nombre=data.nombre,
        codigo=data.codigo,
        numero_modulo=data.numero_modulo,
        horas_semanales=10.0,
        horas_modulo=data.horas_modulo,
    )

    db.add(asignatura)
    await db.flush()
    await db.refresh(asignatura)
    return asignatura


async def listar_asignaturas(db: AsyncSession, carrera_id: str = None, nivel_id: str = None) -> list:
    query = select(Asignatura).where(Asignatura.activo == True)
    if carrera_id:
        query = query.where(Asignatura.carrera_id == carrera_id)
    if nivel_id:
        query = query.where(Asignatura.nivel_id == nivel_id)
    r = await db.execute(query)
    return r.scalars().all()


async def actualizar_asignatura(asignatura_id: str, data: AsignaturaUpdate, db: AsyncSession) -> Asignatura:
    r = await db.execute(select(Asignatura).where(Asignatura.id == asignatura_id))
    asignatura = r.scalar_one_or_none()
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    if data.nombre is not None:
        asignatura.nombre = data.nombre
    if data.horas_semanales is not None:
        asignatura.horas_semanales = data.horas_semanales
    if data.horas_modulo is not None:
        asignatura.horas_modulo = data.horas_modulo
    if data.activo is not None:
        asignatura.activo = data.activo

    await db.flush()
    await db.refresh(asignatura)
    return asignatura

async def copiar_malla(carrera_origen_id: str, carrera_destino_id: str, db: AsyncSession) -> dict:
    """
    Copia todas las asignaturas de una carrera a otra.
    Util para replicar la malla entre sedes.
    """
    from sqlalchemy import select, and_
    from models.models import Nivel

    # Verificar que ambas carreras existen
    r = await db.execute(select(Carrera).where(Carrera.id == carrera_origen_id))
    origen = r.scalar_one_or_none()
    if not origen:
        raise HTTPException(status_code=404, detail="Carrera origen no encontrada")

    r = await db.execute(select(Carrera).where(Carrera.id == carrera_destino_id))
    destino = r.scalar_one_or_none()
    if not destino:
        raise HTTPException(status_code=404, detail="Carrera destino no encontrada")

    # Obtener niveles de la carrera destino ordenados
    r = await db.execute(
        select(Nivel).where(Nivel.carrera_id == carrera_destino_id).order_by(Nivel.numero)
    )
    niveles_destino = r.scalars().all()
    mapa_niveles = {n.numero: n for n in niveles_destino}

    # Obtener niveles de la carrera origen
    r = await db.execute(
        select(Nivel).where(Nivel.carrera_id == carrera_origen_id).order_by(Nivel.numero)
    )
    niveles_origen = r.scalars().all()

    copiadas = 0
    omitidas = 0

    for nivel_origen in niveles_origen:
        nivel_destino = mapa_niveles.get(nivel_origen.numero)
        if not nivel_destino:
            omitidas += 1
            continue

        # Obtener asignaturas de este nivel en la carrera origen
        r = await db.execute(
            select(Asignatura).where(
                and_(
                    Asignatura.carrera_id == carrera_origen_id,
                    Asignatura.nivel_id == nivel_origen.id,
                    Asignatura.activo == True,
                )
            )
        )
        asigs = r.scalars().all()

        for asig in asigs:
            # Verificar que no exista ya en la carrera destino
            r = await db.execute(
                select(Asignatura).where(
                    and_(
                        Asignatura.carrera_id == carrera_destino_id,
                        Asignatura.nivel_id == nivel_destino.id,
                        Asignatura.nombre == asig.nombre,
                        Asignatura.numero_modulo == asig.numero_modulo,
                    )
                )
            )
            if r.scalar_one_or_none():
                omitidas += 1
                continue

            nueva = Asignatura(
                id=str(uuid.uuid4()),
                carrera_id=carrera_destino_id,
                nivel_id=nivel_destino.id,
                nombre=asig.nombre,
                codigo=asig.codigo,
                numero_modulo=asig.numero_modulo,
                horas_semanales=asig.horas_semanales,
                horas_modulo=asig.horas_modulo,
            )
            db.add(nueva)
            copiadas += 1

    await db.flush()
    return {
        "mensaje": f"Malla copiada: {copiadas} asignaturas copiadas, {omitidas} omitidas (ya existian o nivel no encontrado)",
        "copiadas": copiadas,
        "omitidas": omitidas,
    }