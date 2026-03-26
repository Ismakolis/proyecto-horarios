"""
docentes_service.py
Servicio de gestion de docentes, acceso de usuarios y habilidades.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.models import Docente, DocenteAsignatura, Asignatura, Usuario, RolUsuario
from schemas.docentes import DocenteCreate, DocenteUpdate, CrearAccesoDocente, HabilidadDocenteCreate
from utils.jwt import hash_password
import uuid


async def crear_docente(data: DocenteCreate, db: AsyncSession) -> Docente:
    # Verificar cedula unica
    r = await db.execute(select(Docente).where(Docente.cedula == data.cedula))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe un docente con esa cedula")

    # Verificar email unico
    r = await db.execute(select(Docente).where(Docente.email == data.email))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ya existe un docente con ese email")

    docente = Docente(
        id=str(uuid.uuid4()),
        cedula=data.cedula,
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        tipo=data.tipo,
        titulo=data.titulo,
    )
    db.add(docente)
    await db.flush()
    await db.refresh(docente)
    return docente


async def listar_docentes(db: AsyncSession, activo: bool = None) -> list:
    query = select(Docente).order_by(Docente.apellido, Docente.nombre)
    if activo is not None:
        query = query.where(Docente.activo == activo)
    r = await db.execute(query)
    docentes = r.scalars().all()

    # Marcar cuales tienen acceso (usuario creado)
    result = []
    for doc in docentes:
        r2 = await db.execute(select(Usuario).where(Usuario.email == doc.email))
        usuario = r2.scalar_one_or_none()
        doc_dict = {
            "id": doc.id, "cedula": doc.cedula,
            "nombre": doc.nombre, "apellido": doc.apellido,
            "email": doc.email, "tipo": doc.tipo,
            "activo": doc.activo,
            "titulo": doc.titulo,
            "tiene_acceso": usuario is not None,
        }
        result.append(doc_dict)
    return result


async def obtener_docente(docente_id: str, db: AsyncSession) -> Docente:
    r = await db.execute(select(Docente).where(Docente.id == docente_id))
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


async def crear_acceso_docente(data: CrearAccesoDocente, db: AsyncSession) -> dict:
    """Crea un usuario en el sistema para que el docente pueda iniciar sesion."""
    # Verificar que el docente existe
    r = await db.execute(select(Docente).where(Docente.id == data.docente_id))
    docente = r.scalar_one_or_none()
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    # Verificar que no tenga ya un usuario
    r = await db.execute(select(Usuario).where(Usuario.email == docente.email))
    if r.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"El docente {docente.nombre} {docente.apellido} ya tiene acceso al sistema"
        )

    usuario = Usuario(
        id=str(uuid.uuid4()),
        nombre=docente.nombre,
        apellido=docente.apellido,
        email=docente.email,
        password_hash=hash_password(data.password),
        rol=RolUsuario.DOCENTE,
        activo=True,
    )
    db.add(usuario)
    await db.flush()

    return {
        "mensaje": f"Acceso creado para {docente.nombre} {docente.apellido}",
        "email": docente.email,
    }


async def obtener_habilidades(docente_id: str, db: AsyncSession) -> list:
    """Retorna las asignaturas que puede dictar el docente."""
    r = await db.execute(
        select(DocenteAsignatura, Asignatura)
        .join(Asignatura, DocenteAsignatura.asignatura_id == Asignatura.id)
        .where(DocenteAsignatura.docente_id == docente_id)
    )
    rows = r.all()
    return [
        {
            "id": row.DocenteAsignatura.id,
            "asignatura_id": row.DocenteAsignatura.asignatura_id,
            "nombre_asignatura": row.Asignatura.nombre,
            "codigo": row.Asignatura.codigo,
        }
        for row in rows
    ]


async def actualizar_habilidades(docente_id: str, data: HabilidadDocenteCreate, db: AsyncSession) -> dict:
    """Reemplaza las habilidades del docente con la nueva lista."""
    await obtener_docente(docente_id, db)

    # Eliminar habilidades previas
    await db.execute(
        delete(DocenteAsignatura).where(DocenteAsignatura.docente_id == docente_id)
    )

    # Insertar nuevas
    for asig_id in data.asignatura_ids:
        # Verificar que la asignatura existe
        r = await db.execute(select(Asignatura).where(Asignatura.id == asig_id))
        if not r.scalar_one_or_none():
            continue
        habilidad = DocenteAsignatura(
            id=str(uuid.uuid4()),
            docente_id=docente_id,
            asignatura_id=asig_id,
            prioridad=1,
        )
        db.add(habilidad)

    await db.flush()
    return {"mensaje": "Habilidades actualizadas correctamente"}
