from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi import HTTPException
from models.models import (
    Horario, Docente, Asignatura, Modulo, PeriodoAcademico,
    Carrera, Nivel, CargaHoraria, TipoDocente, DiaSemana, Jornada, EstadoHorario
)
from schemas.horarios import HorarioCreate, HorarioUpdate, GenerarHorarioRequest
import uuid


# ─── VALIDACIONES ─────────────────────────────────────────────────────────────

async def validar_choque_docente(modulo_id: str, docente_id: str, dia: str, hora_inicio: str, db: AsyncSession, excluir_id: str = None):
    query = select(Horario).where(
        and_(
            Horario.modulo_id == modulo_id,
            Horario.docente_id == docente_id,
            Horario.dia == dia,
            Horario.hora_inicio == hora_inicio,
        )
    )
    if excluir_id:
        query = query.where(Horario.id != excluir_id)
    r = await db.execute(query)
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Choque de horario: el docente ya tiene clase en ese día y hora")


async def validar_choque_paralelo(modulo_id: str, carrera_id: str, nivel_id: str, paralelo: str, dia: str, hora_inicio: str, db: AsyncSession, excluir_id: str = None):
    query = select(Horario).where(
        and_(
            Horario.modulo_id == modulo_id,
            Horario.carrera_id == carrera_id,
            Horario.nivel_id == nivel_id,
            Horario.paralelo == paralelo,
            Horario.dia == dia,
            Horario.hora_inicio == hora_inicio,
        )
    )
    if excluir_id:
        query = query.where(Horario.id != excluir_id)
    r = await db.execute(query)
    if r.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Choque de horario: ese paralelo ya tiene clase en ese día y hora")


async def validar_max_asignaturas_docente(modulo_id: str, docente_id: str, db: AsyncSession, excluir_id: str = None):
    query = select(func.count(Horario.id)).where(
        and_(
            Horario.modulo_id == modulo_id,
            Horario.docente_id == docente_id,
        )
    )
    if excluir_id:
        query = query.where(Horario.id != excluir_id)
    r = await db.execute(query)
    total = r.scalar()
    if total >= 3:
        raise HTTPException(status_code=400, detail="El docente ya tiene 3 asignaturas en este módulo (máximo permitido)")


async def validar_carga_horaria_tc(docente_id: str, periodo_id: str, horas_asignatura: float, db: AsyncSession):
    r = await db.execute(select(Docente).where(Docente.id == docente_id))
    docente = r.scalar_one_or_none()
    if not docente or docente.tipo != TipoDocente.TIEMPO_COMPLETO:
        return  # Solo aplica a tiempo completo

    r = await db.execute(
        select(func.sum(CargaHoraria.total_horas)).where(
            and_(
                CargaHoraria.docente_id == docente_id,
                CargaHoraria.periodo_id == periodo_id,
            )
        )
    )
    horas_actuales = r.scalar() or 0.0
    if horas_actuales + horas_asignatura > 380:
        raise HTTPException(
            status_code=400,
            detail=f"El docente de tiempo completo excedería las 380 horas del período (actual: {horas_actuales}h)"
        )


# ─── CRUD HORARIOS ────────────────────────────────────────────────────────────

async def crear_horario(data: HorarioCreate, db: AsyncSession) -> Horario:
    # Obtener horas de la asignatura para validar carga
    r = await db.execute(select(Asignatura).where(Asignatura.id == data.asignatura_id))
    asignatura = r.scalar_one_or_none()
    if not asignatura:
        raise HTTPException(status_code=404, detail="Asignatura no encontrada")

    # Validar periodo y modulo existen
    r = await db.execute(select(Modulo).where(Modulo.id == data.modulo_id))
    if not r.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    # Ejecutar todas las validaciones
    await validar_choque_docente(data.modulo_id, data.docente_id, data.dia, data.hora_inicio, db)
    await validar_choque_paralelo(data.modulo_id, data.carrera_id, data.nivel_id, data.paralelo, data.dia, data.hora_inicio, db)
    await validar_max_asignaturas_docente(data.modulo_id, data.docente_id, db)
    await validar_carga_horaria_tc(data.docente_id, data.periodo_id, asignatura.horas_modulo, db)

    horario = Horario(
        id=str(uuid.uuid4()),
        periodo_id=data.periodo_id,
        modulo_id=data.modulo_id,
        docente_id=data.docente_id,
        asignatura_id=data.asignatura_id,
        carrera_id=data.carrera_id,
        nivel_id=data.nivel_id,
        paralelo=data.paralelo,
        dia=data.dia,
        jornada=data.jornada,
        hora_inicio=data.hora_inicio,
        hora_fin=data.hora_fin,
        estado=EstadoHorario.BORRADOR,
        generado_por_ia=False,
    )
    db.add(horario)
    await db.flush()
    await _actualizar_carga_horaria(data.docente_id, data.periodo_id, data.modulo_id, db)
    await db.refresh(horario)
    return horario


async def listar_horarios(db: AsyncSession, periodo_id: str = None, modulo_id: str = None, carrera_id: str = None, docente_id: str = None) -> list:
    query = select(Horario)
    if periodo_id:
        query = query.where(Horario.periodo_id == periodo_id)
    if modulo_id:
        query = query.where(Horario.modulo_id == modulo_id)
    if carrera_id:
        query = query.where(Horario.carrera_id == carrera_id)
    if docente_id:
        query = query.where(Horario.docente_id == docente_id)
    r = await db.execute(query)
    return r.scalars().all()


async def actualizar_horario(horario_id: str, data: HorarioUpdate, db: AsyncSession) -> Horario:
    r = await db.execute(select(Horario).where(Horario.id == horario_id))
    horario = r.scalar_one_or_none()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    if data.docente_id or data.dia or data.hora_inicio:
        docente_id = data.docente_id or horario.docente_id
        dia = data.dia or horario.dia
        hora_inicio = data.hora_inicio or horario.hora_inicio
        await validar_choque_docente(horario.modulo_id, docente_id, dia, hora_inicio, db, excluir_id=horario_id)
        await validar_choque_paralelo(horario.modulo_id, horario.carrera_id, horario.nivel_id, horario.paralelo, dia, hora_inicio, db, excluir_id=horario_id)
        if data.docente_id and data.docente_id != horario.docente_id:
            await validar_max_asignaturas_docente(horario.modulo_id, data.docente_id, db)

    if data.docente_id:
        horario.docente_id = data.docente_id
    if data.dia:
        horario.dia = data.dia
    if data.jornada:
        horario.jornada = data.jornada
    if data.hora_inicio:
        horario.hora_inicio = data.hora_inicio
    if data.hora_fin:
        horario.hora_fin = data.hora_fin
    if data.estado:
        horario.estado = data.estado
    if data.observaciones:
        horario.observaciones = data.observaciones

    await db.flush()
    await _actualizar_carga_horaria(horario.docente_id, horario.periodo_id, horario.modulo_id, db)
    await db.refresh(horario)
    return horario


async def eliminar_horario(horario_id: str, db: AsyncSession):
    r = await db.execute(select(Horario).where(Horario.id == horario_id))
    horario = r.scalar_one_or_none()
    if not horario:
        raise HTTPException(status_code=404, detail="Horario no encontrado")
    docente_id = horario.docente_id
    periodo_id = horario.periodo_id
    modulo_id = horario.modulo_id
    await db.delete(horario)
    await db.flush()
    await _actualizar_carga_horaria(docente_id, periodo_id, modulo_id, db)
    return {"mensaje": "Horario eliminado correctamente"}


# ─── CARGA HORARIA ────────────────────────────────────────────────────────────

async def _actualizar_carga_horaria(docente_id: str, periodo_id: str, modulo_id: str, db: AsyncSession):
    r = await db.execute(
        select(func.count(Horario.id), func.sum(Asignatura.horas_modulo))
        .join(Asignatura, Horario.asignatura_id == Asignatura.id)
        .where(and_(
            Horario.docente_id == docente_id,
            Horario.modulo_id == modulo_id,
        ))
    )
    row = r.one()
    total_asignaturas = row[0] or 0
    total_horas = float(row[1] or 0)

    r = await db.execute(
        select(CargaHoraria).where(and_(
            CargaHoraria.docente_id == docente_id,
            CargaHoraria.periodo_id == periodo_id,
            CargaHoraria.modulo_id == modulo_id,
        ))
    )
    carga = r.scalar_one_or_none()
    if carga:
        carga.total_asignaturas = total_asignaturas
        carga.total_horas = total_horas
    else:
        carga = CargaHoraria(
            id=str(uuid.uuid4()),
            docente_id=docente_id,
            periodo_id=periodo_id,
            modulo_id=modulo_id,
            total_asignaturas=total_asignaturas,
            total_horas=total_horas,
        )
        db.add(carga)
    await db.flush()


# ─── GENERACIÓN AUTOMÁTICA ────────────────────────────────────────────────────

HORARIOS_MATUTINA = ["08:00", "10:00"]   # 2 bloques de 2h
HORARIOS_NOCTURNA = ["18:30", "20:00"]   # 2 bloques de 1.5h
DIAS = [DiaSemana.LUNES, DiaSemana.MARTES, DiaSemana.MIERCOLES, DiaSemana.JUEVES, DiaSemana.VIERNES]


async def generar_horarios_automatico(data: GenerarHorarioRequest, db: AsyncSession) -> dict:
    # Obtener el módulo para saber su número
    r = await db.execute(select(Modulo).where(Modulo.id == data.modulo_id))
    modulo = r.scalar_one_or_none()
    if not modulo:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    # Obtener período para saber paralelos
    r = await db.execute(select(PeriodoAcademico).where(PeriodoAcademico.id == data.periodo_id))
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise HTTPException(status_code=404, detail="Período no encontrado")

    # Obtener SOLO las asignaturas del módulo correcto
    r = await db.execute(
        select(Asignatura).where(
            and_(
                Asignatura.carrera_id == data.carrera_id,
                Asignatura.activo == True,
                Asignatura.numero_modulo == modulo.numero,  # ← clave
            )
        )
    )
    asignaturas = r.scalars().all()
    if not asignaturas:
        raise HTTPException(
            status_code=400,
            detail=f"No hay asignaturas registradas para el Módulo {modulo.numero} de esta carrera"
        )

    # Obtener docentes activos
    r = await db.execute(select(Docente).where(Docente.activo == True))
    docentes = r.scalars().all()
    if not docentes:
        raise HTTPException(status_code=400, detail="No hay docentes activos registrados")

    # Obtener niveles de la carrera
    from models.models import Nivel
    r = await db.execute(
        select(Nivel).where(Nivel.carrera_id == data.carrera_id).order_by(Nivel.numero)
    )
    niveles = r.scalars().all()

    creados = 0
    errores = []
    docente_idx = 0

    for nivel in niveles:
        paralelos = [chr(65 + i) for i in range(nivel.paralelos)]
        
        # Asignaturas de este nivel en este módulo (máx 2)
        asigs_nivel = [a for a in asignaturas if a.nivel_id == nivel.id]
        if not asigs_nivel:
            continue

        for paralelo in paralelos:
            for jornada, slots, horas_fin in [
                (Jornada.MATUTINA, HORARIOS_MATUTINA, ["10:00", "12:00"]),
                (Jornada.NOCTURNA, HORARIOS_NOCTURNA, ["20:00", "21:30"]),
            ]:
                for idx_asig, asignatura in enumerate(asigs_nivel[:2]):
                    slot = slots[idx_asig] if idx_asig < len(slots) else slots[0]
                    hora_fin = horas_fin[idx_asig] if idx_asig < len(horas_fin) else horas_fin[0]

                    # Buscar docente disponible
                    docente_asignado = None
                    intentos = 0
                    while intentos < len(docentes):
                        docente = docentes[docente_idx % len(docentes)]
                        docente_idx += 1
                        intentos += 1

                        r = await db.execute(
                            select(func.count(Horario.id)).where(and_(
                                Horario.modulo_id == data.modulo_id,
                                Horario.docente_id == docente.id,
                            ))
                        )
                        count = r.scalar()
                        if count < 3:
                            docente_asignado = docente
                            break

                    if not docente_asignado:
                        errores.append(f"Sin docente disponible para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo} {jornada.value}")
                        continue

                    # Buscar día sin choque
                    slot_encontrado = False
                    for dia in DIAS:
                        try:
                            await validar_choque_docente(data.modulo_id, docente_asignado.id, dia, slot, db)
                            await validar_choque_paralelo(data.modulo_id, data.carrera_id, nivel.id, paralelo, dia, slot, db)

                            horario = Horario(
                                id=str(uuid.uuid4()),
                                periodo_id=data.periodo_id,
                                modulo_id=data.modulo_id,
                                docente_id=docente_asignado.id,
                                asignatura_id=asignatura.id,
                                carrera_id=data.carrera_id,
                                nivel_id=nivel.id,
                                paralelo=paralelo,
                                dia=dia,
                                jornada=jornada,
                                hora_inicio=slot,
                                hora_fin=hora_fin,
                                estado=EstadoHorario.BORRADOR,
                                generado_por_ia=False,
                            )
                            db.add(horario)
                            await db.flush()
                            await _actualizar_carga_horaria(docente_asignado.id, data.periodo_id, data.modulo_id, db)
                            creados += 1
                            slot_encontrado = True
                            break
                        except HTTPException:
                            continue

                    if not slot_encontrado:
                        errores.append(f"Sin slot disponible para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo}")

    return {
        "mensaje": f"Generación completada: {creados} horarios creados",
        "creados": creados,
        "errores": errores
    }