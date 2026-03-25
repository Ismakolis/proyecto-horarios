from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.models import Docente, DisponibilidadDocente
from schemas.docentes import DocenteCreate, DocenteUpdate
import uuid


async def crear_docente(data: DocenteCreate, db: AsyncSession) -> Docente:
    # Verificar cédula única
    r = await db.execute(select(Docente).where(Docente.cedula == data.cedula))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe un docente con esa cédula")

    # Verificar email único
    r = await db.execute(select(Docente).where(Docente.email == data.email))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe un docente con ese email")

    docente_id = str(uuid.uuid4())
    docente = Docente(
        id=docente_id,
        cedula=data.cedula,
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        tipo=data.tipo,
        titulo=data.titulo,
    )
    db.add(docente)
    await db.flush()

    # Agregar disponibilidades si se enviaron
    for disp in data.disponibilidades or []:
        d = DisponibilidadDocente(
            id=str(uuid.uuid4()),
            docente_id=docente_id,
            dia=disp.dia,
            jornada=disp.jornada,
            disponible=disp.disponible,
        )
        db.add(d)

    await db.flush()
    await db.refresh(docente)

    # Reload con disponibilidades
    r = await db.execute(
        select(Docente)
        .options(selectinload(Docente.disponibilidades))
        .where(Docente.id == docente_id)
    )
    return r.scalar_one()


async def listar_docentes(db: AsyncSession, activo: bool = None) -> list:
    query = select(Docente)
    if activo is not None:
        query = query.where(Docente.activo == activo)
    query = query.order_by(Docente.apellido, Docente.nombre)
    r = await db.execute(query)
    return r.scalars().all()


async def obtener_docente(docente_id: str, db: AsyncSession) -> Docente:
    r = await db.execute(
        select(Docente)
        .options(selectinload(Docente.disponibilidades))
        .where(Docente.id == docente_id)
    )
    docente = r.scalar_one_or_none()
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    return docente


async def actualizar_docente(docente_id: str, data: DocenteUpdate, db: AsyncSession) -> Docente:
    docente = await obtener_docente(docente_id, db)

    if data.nombre is not None:
        docente.nombre = data.nombre
    if data.apellido is not None:
        docente.apellido = data.apellido
    if data.email is not None:
        # Verificar que el nuevo email no esté en uso por otro
        r = await db.execute(
            select(Docente).where(Docente.email == data.email, Docente.id != docente_id)
        )
        if r.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email ya en uso por otro docente")
        docente.email = data.email
    if data.tipo is not None:
        docente.tipo = data.tipo
    if data.titulo is not None:
        docente.titulo = data.titulo
    if data.activo is not None:
        docente.activo = data.activo

    await db.flush()
    await db.refresh(docente)
    return docente


async def eliminar_docente(docente_id: str, db: AsyncSession):
    docente = await obtener_docente(docente_id, db)
    # Soft delete: solo desactivar
    docente.activo = False
    await db.flush()
    return {"mensaje": f"Docente {docente.nombre} {docente.apellido} desactivado correctamente"}


async def actualizar_disponibilidad(docente_id: str, disponibilidades: list, db: AsyncSession):
    # Verificar que el docente existe
    await obtener_docente(docente_id, db)

    # Eliminar disponibilidades previas
    r = await db.execute(
        select(DisponibilidadDocente).where(DisponibilidadDocente.docente_id == docente_id)
    )
    for d in r.scalars().all():
        await db.delete(d)

    # Insertar las nuevas
    for disp in disponibilidades:
        d = DisponibilidadDocente(
            id=str(uuid.uuid4()),
            docente_id=docente_id,
            dia=disp.dia,
            jornada=disp.jornada,
            disponible=disp.disponible,
        )
        db.add(d)

    await db.flush()
    return {"mensaje": "Disponibilidad actualizada correctamente"}