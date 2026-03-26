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
        # Paralelos separados por jornada
        paralelos_mat = [chr(65 + i) for i in range(nivel.paralelos_matutina)]
        paralelos_noc = [chr(65 + i) for i in range(nivel.paralelos_nocturna)]
        
        # Asignaturas de este nivel en este módulo (máx 2)
        asigs_nivel = [a for a in asignaturas if a.nivel_id == nivel.id]
        if not asigs_nivel:
            continue

        from models.models import DocenteAsignatura

        for jornada, paralelos_jornada, slots, horas_fin in [
            (Jornada.MATUTINA, paralelos_mat, HORARIOS_MATUTINA, ["10:00", "12:00"]),
            (Jornada.NOCTURNA, paralelos_noc, HORARIOS_NOCTURNA, ["20:00", "21:30"]),
        ]:
            for paralelo in paralelos_jornada:
                # Cada asignatura del mismo paralelo recibe un slot DIFERENTE y un día DIFERENTE
                for idx_asig, asignatura in enumerate(asigs_nivel[:2]):
                    # Slot fijo por indice: asig 0 → primer bloque, asig 1 → segundo bloque
                    slot     = slots[idx_asig % len(slots)]
                    hora_fin_asig = horas_fin[idx_asig % len(horas_fin)]

                    # Buscar docente disponible con habilidades para esta asignatura
                    docente_asignado = None
                    intentos = 0
                    while intentos < len(docentes):
                        docente = docentes[docente_idx % len(docentes)]
                        docente_idx += 1
                        intentos += 1

                        # Verificar habilidad para esta asignatura
                        r_hab = await db.execute(
                            select(func.count(DocenteAsignatura.id)).where(
                                DocenteAsignatura.docente_id == docente.id,
                                DocenteAsignatura.asignatura_id == asignatura.id,
                            )
                        )
                        tiene_habilidad = r_hab.scalar() > 0

                        # Si el docente tiene habilidades y no incluye esta, saltarlo
                        r_total_hab = await db.execute(
                            select(func.count(DocenteAsignatura.id)).where(
                                DocenteAsignatura.docente_id == docente.id
                            )
                        )
                        total_habilidades = r_total_hab.scalar()
                        if total_habilidades > 0 and not tiene_habilidad:
                            continue

                        # Verificar límite de 3 asignaturas por módulo (global, todas las sedes)
                        r = await db.execute(
                            select(func.count(Horario.id)).where(and_(
                                Horario.modulo_id == data.modulo_id,
                                Horario.docente_id == docente.id,
                            ))
                        )
                        if r.scalar() < 3:
                            docente_asignado = docente
                            break

                    if not docente_asignado:
                        errores.append(f"Sin docente disponible para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo} {jornada.value}")
                        continue

                    # Buscar día sin choque para este slot fijo
                    slot_encontrado = False
                    for dia in DIAS:
                        # Verificar que el docente no tenga clase ese día en ese horario
                        r_choque_doc = await db.execute(
                            select(func.count(Horario.id)).where(and_(
                                Horario.modulo_id == data.modulo_id,
                                Horario.docente_id == docente_asignado.id,
                                Horario.dia == dia,
                                Horario.hora_inicio == slot,
                            ))
                        )
                        if r_choque_doc.scalar() > 0:
                            continue

                        # Verificar que el paralelo no tenga clase ese día en ese horario
                        r_choque_par = await db.execute(
                            select(func.count(Horario.id)).where(and_(
                                Horario.modulo_id == data.modulo_id,
                                Horario.carrera_id == data.carrera_id,
                                Horario.nivel_id == nivel.id,
                                Horario.paralelo == paralelo,
                                Horario.dia == dia,
                                Horario.hora_inicio == slot,
                            ))
                        )
                        if r_choque_par.scalar() > 0:
                            continue

                        # Sin choque — crear horario
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
                            hora_fin=hora_fin_asig,
                            estado=EstadoHorario.BORRADOR,
                            generado_por_ia=False,
                        )
                        db.add(horario)
                        await db.flush()
                        await _actualizar_carga_horaria(docente_asignado.id, data.periodo_id, data.modulo_id, db)
                        creados += 1
                        slot_encontrado = True
                        break

                    if not slot_encontrado:
                        errores.append(f"Sin slot disponible para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo} {jornada.value}")

    return {
        "mensaje": f"Generación completada: {creados} horarios creados",
        "creados": creados,
        "errores": errores
    }


# ─── GENERACIÓN PARA TODAS LAS SEDES ─────────────────────────────────────────

async def generar_horarios_todas_sedes(data, db: AsyncSession) -> dict:
    """
    Genera horarios para todas las sedes juntas en un solo algoritmo.
    Los docentes se reparten entre TODAS las asignaturas de todas las sedes
    respetando el limite global de 3 asignaturas por modulo.
    """
    from sqlalchemy import func as sqlfunc
    from models.models import Nivel, DocenteAsignatura

    # Buscar todas las sedes de esta carrera
    r = await db.execute(
        select(Carrera).where(
            and_(
                sqlfunc.lower(Carrera.nombre) == data.carrera_nombre.lower(),
                Carrera.activo == True
            )
        )
    )
    sedes = r.scalars().all()
    if not sedes:
        raise HTTPException(status_code=404, detail=f"No se encontro la carrera '{data.carrera_nombre}'")

    if data.usar_ia:
        # Para IA: generar sede por sede pero pasando los horarios ya creados como contexto
        total_creados = 0
        total_errores = []
        total_advertencias = []
        resumen_ia = ""
        for sede in sorted(sedes, key=lambda c: c.sede or 'Quito'):
            from schemas.horarios import GenerarHorarioRequest
            data_sede = GenerarHorarioRequest(
                periodo_id=data.periodo_id,
                modulo_id=data.modulo_id,
                carrera_id=sede.id,
                usar_ia=True,
            )
            resultado = await generar_horarios_con_ia(data_sede, db)
            total_creados += resultado.get("creados", 0)
            if resultado.get("errores"):
                total_errores.extend([f"[{sede.sede or 'Quito'}] {e}" for e in resultado["errores"]])
            if resultado.get("advertencias"):
                total_advertencias.extend(resultado["advertencias"])
            if resultado.get("resumen_ia"):
                resumen_ia = resultado["resumen_ia"]
        return {
            "mensaje": f"Generacion con IA completada para todas las sedes: {total_creados} horarios creados",
            "creados": total_creados,
            "errores": total_errores,
            "advertencias": total_advertencias,
            "resumen_ia": resumen_ia,
        }

    # Obtener modulo
    r = await db.execute(select(Modulo).where(Modulo.id == data.modulo_id))
    modulo = r.scalar_one_or_none()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")

    # Obtener docentes activos
    r = await db.execute(select(Docente).where(Docente.activo == True))
    docentes = r.scalars().all()
    if not docentes:
        raise HTTPException(status_code=400, detail="No hay docentes activos")

    # Recopilar TODAS las asignaturas de todas las sedes intercaladas
    # Orden: Nivel1-SedeA, Nivel1-SedeB, Nivel2-SedeA, Nivel2-SedeB...
    # Asi los docentes se distribuyen equitativamente entre sedes
    tareas = []  # lista de (carrera_id, nivel, asignatura, jornada, paralelo, slot, hora_fin)

    for sede in sorted(sedes, key=lambda c: c.sede or 'Quito'):
        r = await db.execute(
            select(Nivel).where(Nivel.carrera_id == sede.id).order_by(Nivel.numero)
        )
        niveles_sede = r.scalars().all()

        for nivel in niveles_sede:
            r = await db.execute(
                select(Asignatura).where(
                    and_(
                        Asignatura.carrera_id == sede.id,
                        Asignatura.nivel_id == nivel.id,
                        Asignatura.activo == True,
                        Asignatura.numero_modulo == modulo.numero,
                    )
                )
            )
            asigs = r.scalars().all()
            if not asigs:
                continue

            paralelos_mat = [chr(65 + i) for i in range(nivel.paralelos_matutina)]
            paralelos_noc = [chr(65 + i) for i in range(nivel.paralelos_nocturna)]

            for jornada, paralelos_j, slots, horas_fin in [
                (Jornada.MATUTINA, paralelos_mat, HORARIOS_MATUTINA, ["10:00", "12:00"]),
                (Jornada.NOCTURNA, paralelos_noc, HORARIOS_NOCTURNA, ["20:00", "21:30"]),
            ]:
                for paralelo in paralelos_j:
                    for idx_asig, asig in enumerate(asigs[:2]):
                        tareas.append({
                            "carrera_id": sede.id,
                            "sede_nombre": sede.sede or "Quito",
                            "nivel": nivel,
                            "asignatura": asig,
                            "jornada": jornada,
                            "paralelo": paralelo,
                            "slot": slots[idx_asig % len(slots)],
                            "hora_fin": horas_fin[idx_asig % len(horas_fin)],
                        })

    # Debug: log tareas encontradas por sede
    import logging
    logger = logging.getLogger(__name__)
    sedes_encontradas = {}
    for t in tareas:
        s = t["sede_nombre"]
        sedes_encontradas[s] = sedes_encontradas.get(s, 0) + 1
    logger.warning(f"TAREAS POR SEDE: {sedes_encontradas} | Total tareas: {len(tareas)}")

    # Intercalar tareas por sede para distribución equitativa
    # Agrupar por sede y luego entrelazar
    tareas_por_sede = {}
    for t in tareas:
        s = t["sede_nombre"]
        if s not in tareas_por_sede:
            tareas_por_sede[s] = []
        tareas_por_sede[s].append(t)

    tareas_intercaladas = []
    listas = list(tareas_por_sede.values())
    max_len = max(len(l) for l in listas) if listas else 0
    for i in range(max_len):
        for lista in listas:
            if i < len(lista):
                tareas_intercaladas.append(lista[i])

    # Asignar docentes a cada tarea
    creados = 0
    errores = []
    docente_idx = 0

    for tarea in tareas_intercaladas:
        asignatura = tarea["asignatura"]
        nivel      = tarea["nivel"]
        paralelo   = tarea["paralelo"]
        jornada    = tarea["jornada"]
        slot       = tarea["slot"]
        hora_fin   = tarea["hora_fin"]
        carrera_id = tarea["carrera_id"]
        sede_nombre = tarea["sede_nombre"]

        # Buscar docente disponible con habilidades y cupo global
        docente_asignado = None
        intentos = 0
        while intentos < len(docentes):
            docente = docentes[docente_idx % len(docentes)]
            docente_idx += 1
            intentos += 1

            # Verificar habilidad por nombre de asignatura (no por ID)
            # porque la misma materia tiene IDs distintos en cada sede
            r_hab = await db.execute(
                select(func.count(DocenteAsignatura.id))
                .join(Asignatura, DocenteAsignatura.asignatura_id == Asignatura.id)
                .where(
                    DocenteAsignatura.docente_id == docente.id,
                    func.lower(Asignatura.nombre) == asignatura.nombre.lower(),
                )
            )
            tiene_habilidad = r_hab.scalar() > 0
            r_total = await db.execute(
                select(func.count(DocenteAsignatura.id)).where(
                    DocenteAsignatura.docente_id == docente.id
                )
            )
            total_habs = r_total.scalar()
            if total_habs > 0 and not tiene_habilidad:
                continue

            # Verificar límite global de 3 asignaturas en este modulo
            r_count = await db.execute(
                select(func.count(Horario.id)).where(and_(
                    Horario.modulo_id == data.modulo_id,
                    Horario.docente_id == docente.id,
                ))
            )
            if r_count.scalar() >= 3:
                continue

            docente_asignado = docente
            break

        if not docente_asignado:
            logger.warning(f"SIN DOCENTE para [{sede_nombre}] {asignatura.nombre} - {nivel.nombre} paralelo {paralelo} jornada {jornada}")
            errores.append(f"[{sede_nombre}] Sin docente disponible para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo}")
            continue

        # Buscar día sin choque
        slot_encontrado = False
        for dia in DIAS:
            r_doc = await db.execute(
                select(func.count(Horario.id)).where(and_(
                    Horario.modulo_id == data.modulo_id,
                    Horario.docente_id == docente_asignado.id,
                    Horario.dia == dia,
                    Horario.hora_inicio == slot,
                ))
            )
            if r_doc.scalar() > 0:
                continue

            r_par = await db.execute(
                select(func.count(Horario.id)).where(and_(
                    Horario.modulo_id == data.modulo_id,
                    Horario.carrera_id == carrera_id,
                    Horario.nivel_id == nivel.id,
                    Horario.paralelo == paralelo,
                    Horario.dia == dia,
                    Horario.hora_inicio == slot,
                ))
            )
            if r_par.scalar() > 0:
                continue

            horario = Horario(
                id=str(uuid.uuid4()),
                periodo_id=data.periodo_id,
                modulo_id=data.modulo_id,
                docente_id=docente_asignado.id,
                asignatura_id=asignatura.id,
                carrera_id=carrera_id,
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

        if not slot_encontrado:
            errores.append(f"[{sede_nombre}] Sin slot para {asignatura.nombre} - {nivel.nombre} paralelo {paralelo}")

    return {
        "mensaje": f"Generacion completada para todas las sedes: {creados} horarios creados",
        "creados": creados,
        "errores": errores,
    }


# ─── GENERACIÓN CON IA ────────────────────────────────────────────────────────

async def _construir_contexto_ia(data, modulo, db: AsyncSession) -> dict:
    """
    Recopila toda la informacion necesaria para que Claude pueda sugerir horarios.
    Incluye asignaturas, docentes, disponibilidad y carga actual.
    """
    from models.models import Nivel, DisponibilidadDocente

    # Carrera
    r = await db.execute(select(Carrera).where(Carrera.id == data.carrera_id))
    carrera = r.scalar_one_or_none()

    # Niveles de la carrera
    r = await db.execute(
        select(Nivel).where(Nivel.carrera_id == data.carrera_id).order_by(Nivel.numero)
    )
    niveles = r.scalars().all()

    # Asignaturas del modulo (con nivel y paralelos)
    asignaturas_contexto = []
    for nivel in niveles:
        r = await db.execute(
            select(Asignatura).where(
                and_(
                    Asignatura.carrera_id == data.carrera_id,
                    Asignatura.nivel_id == nivel.id,
                    Asignatura.activo == True,
                    Asignatura.numero_modulo == modulo.numero,
                )
            )
        )
        asigs = r.scalars().all()
        paralelos_mat = [chr(65 + i) for i in range(nivel.paralelos_matutina)]
        paralelos_noc = [chr(65 + i) for i in range(nivel.paralelos_nocturna)]
        for jornada_str, paralelos_j in [("matutina", paralelos_mat), ("nocturna", paralelos_noc)]:
            for asig in asigs:
                for paralelo in paralelos_j:
                    asignaturas_contexto.append({
                        "id":            f"{asig.id}|{nivel.id}|{paralelo}|{jornada_str}",
                        "asignatura_id": asig.id,
                        "nivel_id":      nivel.id,
                        "nivel_numero":  nivel.numero,
                        "paralelo":      paralelo,
                        "jornada":       jornada_str,
                        "nombre":        asig.nombre,
                        "horas_modulo":  asig.horas_modulo,
                    })

    # Docentes activos con su carga actual y disponibilidad
    r = await db.execute(select(Docente).where(Docente.activo == True))
    docentes_db = r.scalars().all()

    docentes_contexto = []
    for doc in docentes_db:
        # Contar asignaturas ya asignadas en este modulo
        r = await db.execute(
            select(func.count(Horario.id)).where(
                and_(
                    Horario.docente_id == doc.id,
                    Horario.modulo_id  == data.modulo_id,
                )
            )
        )
        count = r.scalar() or 0

        # Disponibilidad del docente
        r = await db.execute(
            select(DisponibilidadDocente).where(
                and_(
                    DisponibilidadDocente.docente_id == doc.id,
                    DisponibilidadDocente.disponible == True,
                )
            )
        )
        disps = r.scalars().all()
        disponibilidad = [f"{d.dia.value}-{d.jornada.value}" for d in disps]

        # Obtener horarios ya asignados a este docente en este modulo
        r_horarios = await db.execute(
            select(Horario).where(
                and_(
                    Horario.docente_id == doc.id,
                    Horario.modulo_id  == data.modulo_id,
                )
            )
        )
        horarios_doc = r_horarios.scalars().all()
        horarios_existentes = [
            {"dia": h.dia, "hora_inicio": h.hora_inicio, "hora_fin": h.hora_fin}
            for h in horarios_doc
        ]

        docentes_contexto.append({
            "id":                   doc.id,
            "nombre":               f"{doc.nombre} {doc.apellido}",
            "tipo":                 doc.tipo.value,
            "asignaturas_actuales": count,
            "disponibilidad":       disponibilidad,
            "horarios_ya_asignados": horarios_existentes,
        })

    return {
        "carrera":       carrera.nombre if carrera else data.carrera_id,
        "modulo_numero": modulo.numero,
        "asignaturas":   asignaturas_contexto,
        "docentes":      docentes_contexto,
    }


async def generar_horarios_con_ia(data, db: AsyncSession) -> dict:
    """
    Genera horarios con IA:
    1. La IA decide qué docente va con cada asignatura.
    2. El sistema busca día/hora libre sin choques (igual que el modo automático).
    Esto evita que la IA genere choques de horario.
    """
    from services.ia_service import solicitar_sugerencia_ia
    from models.models import Nivel, DocenteAsignatura

    # Obtener modulo
    r = await db.execute(select(Modulo).where(Modulo.id == data.modulo_id))
    modulo = r.scalar_one_or_none()
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")

    # Construir contexto para la IA
    contexto = await _construir_contexto_ia(data, modulo, db)

    if not contexto["asignaturas"]:
        raise HTTPException(status_code=400, detail=f"No hay asignaturas en el Modulo {modulo.numero}")
    if not contexto["docentes"]:
        raise HTTPException(status_code=400, detail="No hay docentes activos")

    # Consultar a la IA — solo para asignar docentes
    plan = await solicitar_sugerencia_ia(contexto)

    # Mapa asignatura_id → docente_id sugerido por la IA
    asig_map     = {a["id"]: a for a in contexto["asignaturas"]}
    docente_ia   = {}  # asig_key → docente_id
    advertencias = []

    for asig in plan.get("asignaciones", []):
        asig_key   = asig.get("asignatura_id")
        docente_id = asig.get("docente_id")
        if asig_key and docente_id:
            docente_ia[asig_key] = docente_id

    # Obtener lista de docentes para fallback
    r = await db.execute(select(Docente).where(Docente.activo == True))
    docentes = r.scalars().all()

    creados  = 0
    errores  = []
    resumen  = plan.get("resumen", "Distribucion sugerida por IA")
    ya_procesadas = set()  # evitar procesar la misma asignatura dos veces

    for info in contexto["asignaturas"]:
        # Saltar si ya fue procesada (la IA a veces repite asignaturas)
        clave = f"{info['asignatura_id']}|{info['nivel_id']}|{info['paralelo']}|{info['jornada']}"
        if clave in ya_procesadas:
            continue
        ya_procesadas.add(clave)

        asig_key   = info["id"]
        jornada_str = info["jornada"]
        jornada    = Jornada.MATUTINA if jornada_str == "matutina" else Jornada.NOCTURNA
        slots      = HORARIOS_MATUTINA if jornada == Jornada.MATUTINA else HORARIOS_NOCTURNA
        horas_fin  = ["10:00", "12:00"] if jornada == Jornada.MATUTINA else ["20:00", "21:30"]

        # Obtener asignatura real
        r = await db.execute(select(Asignatura).where(Asignatura.id == info["asignatura_id"]))
        asignatura = r.scalar_one_or_none()
        if not asignatura:
            continue

        # Usar docente sugerido por IA, verificando que tenga cupo
        docente_id_sugerido = docente_ia.get(asig_key)
        docente_asignado = None

        # Intentar primero con el docente sugerido por la IA
        # pero verificar que tenga habilidad para esta asignatura
        if docente_id_sugerido:
            # Verificar habilidad
            r_hab_ia = await db.execute(
                select(func.count(DocenteAsignatura.id))
                .join(Asignatura, DocenteAsignatura.asignatura_id == Asignatura.id)
                .where(
                    DocenteAsignatura.docente_id == docente_id_sugerido,
                    func.lower(Asignatura.nombre) == asignatura.nombre.lower(),
                )
            )
            tiene_hab_ia = r_hab_ia.scalar() > 0
            r_total_ia = await db.execute(
                select(func.count(DocenteAsignatura.id)).where(
                    DocenteAsignatura.docente_id == docente_id_sugerido
                )
            )
            total_hab_ia = r_total_ia.scalar()
            # Si tiene habilidades pero no para esta materia, no usar
            habilidad_ok = total_hab_ia == 0 or tiene_hab_ia

            if habilidad_ok:
                r_count = await db.execute(
                    select(func.count(Horario.id)).where(and_(
                        Horario.modulo_id == data.modulo_id,
                        Horario.docente_id == docente_id_sugerido,
                    ))
                )
                if r_count.scalar() < 3:
                    r_doc = await db.execute(select(Docente).where(Docente.id == docente_id_sugerido))
                    docente_asignado = r_doc.scalar_one_or_none()

        # Si el sugerido no sirve, buscar otro con cupo y habilidad (fallback automático)
        if not docente_asignado:
            advertencias.append(f"IA sugirió docente sin cupo para {info['nombre']}, usando fallback automático")
            for docente in docentes:
                # Verificar habilidad por nombre
                r_hab = await db.execute(
                    select(func.count(DocenteAsignatura.id))
                    .join(Asignatura, DocenteAsignatura.asignatura_id == Asignatura.id)
                    .where(
                        DocenteAsignatura.docente_id == docente.id,
                        func.lower(Asignatura.nombre) == asignatura.nombre.lower(),
                    )
                )
                tiene_habilidad = r_hab.scalar() > 0
                r_total = await db.execute(
                    select(func.count(DocenteAsignatura.id)).where(
                        DocenteAsignatura.docente_id == docente.id
                    )
                )
                total_habs = r_total.scalar()
                # Si tiene habilidades pero no para esta materia, saltar
                if total_habs > 0 and not tiene_habilidad:
                    continue

                r_count = await db.execute(
                    select(func.count(Horario.id)).where(and_(
                        Horario.modulo_id == data.modulo_id,
                        Horario.docente_id == docente.id,
                    ))
                )
                if r_count.scalar() < 3:
                    docente_asignado = docente
                    break

        if not docente_asignado:
            errores.append(f"Sin docente disponible para {info['nombre']} - Nivel {info['nivel_numero']} paralelo {info['paralelo']}")
            continue

        # El SISTEMA busca slot libre: primero intenta mismo día con hora diferente
        # Las 2 materias del paralelo van el mismo día en bloques distintos (08:00 y 10:00)
        slot_encontrado = False
        for slot_idx, slot in enumerate(slots):
            hora_fin = horas_fin[slot_idx]
            for dia in DIAS:

                # Choque de docente — global entre todas las sedes y jornadas
                r_doc = await db.execute(
                    select(func.count(Horario.id)).where(and_(
                        Horario.modulo_id == data.modulo_id,
                        Horario.docente_id == docente_asignado.id,
                        Horario.jornada == jornada,
                        Horario.hora_inicio == slot,
                    ))
                )
                if r_doc.scalar() > 0:
                    continue

                # Choque de paralelo — por nivel_id y paralelo dentro del mismo modulo
                # nivel_id es único por sede, así que esto es correcto por sede
                r_par = await db.execute(
                    select(func.count(Horario.id)).where(and_(
                        Horario.modulo_id == data.modulo_id,
                        Horario.nivel_id == info["nivel_id"],
                        Horario.paralelo == info["paralelo"],
                        Horario.jornada == jornada,
                        Horario.hora_inicio == slot,
                    ))
                )
                if r_par.scalar() > 0:
                    continue

                horario = Horario(
                    id=str(uuid.uuid4()),
                    periodo_id=data.periodo_id,
                    modulo_id=data.modulo_id,
                    docente_id=docente_asignado.id,
                    asignatura_id=info["asignatura_id"],
                    carrera_id=data.carrera_id,
                    nivel_id=info["nivel_id"],
                    paralelo=info["paralelo"],
                    dia=dia,
                    jornada=jornada,
                    hora_inicio=slot,
                    hora_fin=hora_fin,
                    estado=EstadoHorario.BORRADOR,
                    generado_por_ia=True,
                )
                db.add(horario)
                await db.flush()
                await _actualizar_carga_horaria(docente_asignado.id, data.periodo_id, data.modulo_id, db)
                creados += 1
                slot_encontrado = True
                break
            if slot_encontrado:
                break

        if not slot_encontrado:
            errores.append(f"Sin slot disponible para {info['nombre']} - Nivel {info['nivel_numero']} paralelo {info['paralelo']}")

    return {
        "mensaje":      f"Generacion con IA completada: {creados} horarios creados",
        "creados":      creados,
        "resumen_ia":   resumen,
        "errores":      errores,
        "advertencias": advertencias,
    }