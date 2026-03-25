from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models.models import Horario, Docente, Asignatura, Modulo, Carrera, Nivel, CargaHoraria, PeriodoAcademico
import io


# ─── ESTILOS ──────────────────────────────────────────────────────────────────

def borde_completo():
    lado = Side(style="thin", color="000000")
    return Border(left=lado, right=lado, top=lado, bottom=lado)

def celda_titulo(ws, fila, col_inicio, col_fin, texto, color="1F3864", size=12):
    ws.merge_cells(start_row=fila, start_column=col_inicio, end_row=fila, end_column=col_fin)
    c = ws.cell(row=fila, column=col_inicio, value=texto)
    c.font = Font(bold=True, color="FFFFFF", size=size)
    c.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    return c

def celda_subtitulo(ws, fila, col_inicio, col_fin, texto, color="2E75B6"):
    ws.merge_cells(start_row=fila, start_column=col_inicio, end_row=fila, end_column=col_fin)
    c = ws.cell(row=fila, column=col_inicio, value=texto)
    c.font = Font(bold=True, color="FFFFFF", size=11)
    c.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    c.alignment = Alignment(horizontal="center", vertical="center")
    return c

def celda_encabezado(cell, color="BDD7EE"):
    cell.font = Font(bold=True, size=10, color="1F3864")
    cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = borde_completo()

def celda_dato(cell, fila_par=False):
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    cell.border = borde_completo()
    cell.font = Font(size=10)
    if fila_par:
        cell.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

def celda_centro(cell, fila_par=False):
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = borde_completo()
    cell.font = Font(size=10)
    if fila_par:
        cell.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

def autoajustar(ws, anchos: dict):
    for col, ancho in anchos.items():
        ws.column_dimensions[get_column_letter(col)].width = ancho


# ─── CARGAR DATOS RELACIONADOS ────────────────────────────────────────────────

async def cargar_catalogos(db: AsyncSession):
    docentes_map = {}
    r = await db.execute(select(Docente))
    for d in r.scalars().all():
        docentes_map[d.id] = f"{d.nombre} {d.apellido}"

    asignaturas_map = {}
    r = await db.execute(select(Asignatura))
    for a in r.scalars().all():
        asignaturas_map[a.id] = a

    carreras_map = {}
    r = await db.execute(select(Carrera))
    for c in r.scalars().all():
        carreras_map[c.id] = c.nombre

    niveles_map = {}
    r = await db.execute(select(Nivel))
    for n in r.scalars().all():
        niveles_map[n.id] = n.numero

    return docentes_map, asignaturas_map, carreras_map, niveles_map


# ─── HOJA MÓDULO (formato ITQ) ────────────────────────────────────────────────

async def escribir_hoja_modulo(ws, modulo: Modulo, periodo: PeriodoAcademico, horarios: list, db: AsyncSession):
    docentes_map, asignaturas_map, carreras_map, niveles_map = await cargar_catalogos(db)

    # Ajuste de alturas
    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 18
    ws.row_dimensions[4].height = 18
    ws.row_dimensions[5].height = 18

    # Encabezado institucional
    celda_titulo(ws, 1, 1, 10, f"CARRERA: {carreras_map.get(horarios[0].carrera_id, 'ITQ') if horarios else 'ITQ'}", "1F3864", 13)
    celda_titulo(ws, 2, 1, 10, "PLANIFICACIÓN ACADÉMICA", "1F3864", 11)
    celda_titulo(ws, 3, 1, 10, f"PERIODO: {periodo.nombre}", "1F3864", 11)
    celda_titulo(ws, 4, 1, 10, f"{modulo.nombre.upper()}  ({modulo.fecha_inicio} al {modulo.fecha_fin})", "2E75B6", 12)

    fila_actual = 6

    # Separar por jornada
    for jornada_label, jornada_key, horario_txt in [
        ("MODALIDAD PRESENCIAL QUITO — MATUTINO (LUNES A VIERNES)", "matutina", "08H00 - 12H00"),
        ("MODALIDAD PRESENCIAL QUITO — NOCTURNO (LUNES A VIERNES)", "nocturna", "18H30 - 21H30"),
    ]:
        horarios_jornada = [h for h in horarios if h.jornada == jornada_key]
        if not horarios_jornada:
            continue

        # Subtítulo jornada
        ws.row_dimensions[fila_actual].height = 18
        celda_subtitulo(ws, fila_actual, 1, 10, jornada_label, "2E75B6")
        fila_actual += 1

        # Encabezados columnas
        ws.row_dimensions[fila_actual].height = 30
        encabezados = ["MÓDULO", "FECHA INICIO", "FECHA FIN", "ASIGNATURA", "NIVEL", "PARALELO", "HORAS", "HORARIO", "DOCENTE", "OBSERVACIÓN"]
        for col, enc in enumerate(encabezados, 1):
            celda_encabezado(ws.cell(row=fila_actual, column=col, value=enc))
        fila_actual += 1

        # Datos
        for idx, h in enumerate(horarios_jornada):
            ws.row_dimensions[fila_actual].height = 18
            asig = asignaturas_map.get(h.asignatura_id)
            asig_nombre = asig.nombre if asig else "N/A"
            nivel_num = niveles_map.get(h.nivel_id, "")
            docente_nombre = docentes_map.get(h.docente_id, "POR DEFINIR")
            horas = asig.horas_modulo if asig else 0
            par = idx % 2 == 0

            datos = [
                modulo.numero,
                str(modulo.fecha_inicio),
                str(modulo.fecha_fin),
                asig_nombre,
                nivel_num,
                h.paralelo,
                horas,
                f"{h.hora_inicio} - {h.hora_fin}",
                docente_nombre.upper(),
                h.observaciones or "",
            ]

            for col, val in enumerate(datos, 1):
                c = ws.cell(row=fila_actual, column=col, value=val)
                if col in [1, 5, 6, 7]:
                    celda_centro(c, par)
                else:
                    celda_dato(c, par)

            fila_actual += 1

        fila_actual += 1  # Espacio entre jornadas

    # Anchos de columna
    autoajustar(ws, {1: 10, 2: 14, 3: 14, 4: 35, 5: 8, 6: 10, 7: 8, 8: 16, 9: 25, 10: 20})


# ─── HOJA CARGA HORARIA POR MÓDULO ────────────────────────────────────────────

async def escribir_hoja_carga_modulos(ws, periodo: PeriodoAcademico, modulos: list, db: AsyncSession):
    docentes_map, _, carreras_map, _ = await cargar_catalogos(db)

    ws.row_dimensions[1].height = 22
    ws.row_dimensions[2].height = 18
    ws.row_dimensions[3].height = 18
    ws.row_dimensions[4].height = 18

    # Obtener nombre carrera del período
    r = await db.execute(select(Horario).where(Horario.periodo_id == periodo.id).limit(1))
    primer_horario = r.scalar_one_or_none()
    carrera_nombre = carreras_map.get(primer_horario.carrera_id, "ITQ") if primer_horario else "ITQ"

    celda_titulo(ws, 1, 1, 8, f"CARRERA: {carrera_nombre}", "1F3864", 13)
    celda_titulo(ws, 2, 1, 8, "PLANIFICACIÓN ACADÉMICA DOCENTES A TIEMPO COMPLETO & PARCIAL", "1F3864", 11)
    celda_titulo(ws, 3, 1, 8, f"PERIODO: {periodo.nombre}", "1F3864", 11)

    fila = 5
    # Encabezados
    encabezados = ["DOCENTES", "TIPO", "MÓDULO 1\n(asig)", "MÓDULO 2\n(asig)", "MÓDULO 3\n(asig)", "TOTAL\nASIG", "HORAS TC", "HORAS TP"]
    ws.row_dimensions[fila].height = 35
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws.cell(row=fila, column=col, value=enc))
    fila += 1

    r = await db.execute(select(Docente).where(Docente.activo == True).order_by(Docente.apellido))
    docentes = r.scalars().all()

    for idx, docente in enumerate(docentes):
        ws.row_dimensions[fila].height = 18
        par = idx % 2 == 0
        nombre = f"{docente.nombre} {docente.apellido}".upper()
        tipo = "TC" if docente.tipo.value == "tiempo_completo" else "TP"

        c1 = ws.cell(row=fila, column=1, value=nombre)
        celda_dato(c1, par)
        c2 = ws.cell(row=fila, column=2, value=tipo)
        celda_centro(c2, par)

        total_asig = 0
        total_horas_tc = 0
        total_horas_tp = 0

        for i, modulo in enumerate(modulos[:3], 3):
            r2 = await db.execute(
                select(CargaHoraria).where(and_(
                    CargaHoraria.docente_id == docente.id,
                    CargaHoraria.modulo_id == modulo.id,
                ))
            )
            carga = r2.scalar_one_or_none()
            asig = carga.total_asignaturas if carga else 0
            horas = carga.total_horas if carga else 0
            total_asig += asig
            if tipo == "TC":
                total_horas_tc += horas
            else:
                total_horas_tp += horas

            c = ws.cell(row=fila, column=i, value=asig)
            celda_centro(c, par)
            if asig >= 3:
                c.fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")

        ct = ws.cell(row=fila, column=6, value=total_asig)
        celda_centro(ct, par)
        ct.font = Font(bold=True, size=10)

        ctc = ws.cell(row=fila, column=7, value=round(total_horas_tc, 1))
        celda_centro(ctc, par)

        ctp = ws.cell(row=fila, column=8, value=round(total_horas_tp, 1))
        celda_centro(ctp, par)

        fila += 1

    autoajustar(ws, {1: 30, 2: 8, 3: 14, 4: 14, 5: 14, 6: 10, 7: 10, 8: 10})


# ─── HOJA CARGA TOTAL ─────────────────────────────────────────────────────────

async def escribir_hoja_carga_total(ws, periodo: PeriodoAcademico, db: AsyncSession):
    docentes_map, _, carreras_map, _ = await cargar_catalogos(db)

    ws.row_dimensions[1].height = 22

    r = await db.execute(select(Horario).where(Horario.periodo_id == periodo.id).limit(1))
    primer_horario = r.scalar_one_or_none()
    carrera_nombre = carreras_map.get(primer_horario.carrera_id, "ITQ") if primer_horario else "ITQ"

    celda_titulo(ws, 1, 1, 7, f"CARRERA: {carrera_nombre}", "1F3864", 13)
    celda_titulo(ws, 2, 1, 7, "DISTRIBUCIÓN DE CARGA HORARIA DE DOCENCIA TIEMPO COMPLETO", "1F3864", 11)
    celda_titulo(ws, 3, 1, 7, f"PERIODO: {periodo.nombre}", "1F3864", 11)

    fila = 5
    encabezados = ["DOCENTES", "MÓDULO 1", "MÓDULO 2", "MÓDULO 3", "TOTAL", "MÍNIMO", "ESTADO"]
    ws.row_dimensions[fila].height = 30
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws.cell(row=fila, column=col, value=enc))

    # Fila de referencia mínimo/máximo
    fila += 1
    ws.cell(row=fila, column=6, value=272).font = Font(bold=True, color="FF0000", size=10)
    ws.cell(row=fila, column=6).alignment = Alignment(horizontal="center")
    fila += 1

    r = await db.execute(
        select(Docente)
        .where(Docente.activo == True)
        .order_by(Docente.apellido)
    )
    docentes = r.scalars().all()

    r2 = await db.execute(
        select(Modulo)
        .where(Modulo.periodo_id == periodo.id)
        .order_by(Modulo.numero)
    )
    modulos = r2.scalars().all()

    for idx, docente in enumerate(docentes):
        ws.row_dimensions[fila].height = 18
        par = idx % 2 == 0
        nombre = f"{docente.nombre} {docente.apellido}".upper()
        es_tc = docente.tipo.value == "tiempo_completo"

        c1 = ws.cell(row=fila, column=1, value=nombre)
        celda_dato(c1, par)

        total_horas = 0
        for i, modulo in enumerate(modulos[:3], 2):
            r3 = await db.execute(
                select(CargaHoraria).where(and_(
                    CargaHoraria.docente_id == docente.id,
                    CargaHoraria.modulo_id == modulo.id,
                ))
            )
            carga = r3.scalar_one_or_none()
            horas = round(carga.total_horas, 1) if carga else 0
            total_horas += horas
            c = ws.cell(row=fila, column=i, value=horas)
            celda_centro(c, par)

        ct = ws.cell(row=fila, column=5, value=round(total_horas, 1))
        celda_centro(ct, par)
        ct.font = Font(bold=True, size=10)

        ws.cell(row=fila, column=6, value=272 if es_tc else "N/A").border = borde_completo()

        if es_tc:
            if total_horas < 272:
                estado = "⚠ BAJO MÍNIMO"
                color_txt = "FF0000"
            elif total_horas > 380:
                estado = "⚠ EXCEDE MÁXIMO"
                color_txt = "FF0000"
            else:
                estado = "✓ OK"
                color_txt = "375623"
        else:
            estado = "TIEMPO PARCIAL"
            color_txt = "2E75B6"

        ce = ws.cell(row=fila, column=7, value=estado)
        ce.font = Font(bold=True, color=color_txt, size=10)
        ce.border = borde_completo()
        ce.alignment = Alignment(horizontal="center", vertical="center")

        fila += 1

    autoajustar(ws, {1: 30, 2: 12, 3: 12, 4: 12, 5: 10, 6: 10, 7: 18})


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

async def generar_excel(periodo_id: str, db: AsyncSession) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)

    r = await db.execute(select(PeriodoAcademico).where(PeriodoAcademico.id == periodo_id))
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise Exception("Período no encontrado")

    r = await db.execute(
        select(Modulo)
        .where(Modulo.periodo_id == periodo_id)
        .order_by(Modulo.numero)
    )
    modulos = r.scalars().all()
    if not modulos:
        raise Exception("No hay módulos registrados para este período")

    # Hojas por módulo
    for modulo in modulos[:3]:
        ws = wb.create_sheet(title=f"MÓDULO {modulo.numero}")
        r = await db.execute(
            select(Horario)
            .where(Horario.modulo_id == modulo.id)
            .order_by(Horario.jornada, Horario.nivel_id, Horario.paralelo, Horario.hora_inicio)
        )
        horarios = r.scalars().all()
        if horarios:
            await escribir_hoja_modulo(ws, modulo, periodo, horarios, db)
        else:
            ws.cell(row=1, column=1, value=f"Sin horarios para {modulo.nombre}")

    # Hoja carga por módulos
    ws_carga = wb.create_sheet(title="Carga horaria por modulos")
    await escribir_hoja_carga_modulos(ws_carga, periodo, modulos, db)

    # Hoja carga total
    ws_total = wb.create_sheet(title="Carga horaria total")
    await escribir_hoja_carga_total(ws_total, periodo, db)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()

# ─── REPORTE POR DOCENTE ──────────────────────────────────────────────────────

async def generar_excel_por_docente(periodo_id: str, docente_id: str, db: AsyncSession) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)

    r = await db.execute(select(PeriodoAcademico).where(PeriodoAcademico.id == periodo_id))
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise Exception("Período no encontrado")

    r = await db.execute(select(Docente).where(Docente.id == docente_id))
    docente = r.scalar_one_or_none()
    if not docente:
        raise Exception("Docente no encontrado")

    r = await db.execute(
        select(Modulo).where(Modulo.periodo_id == periodo_id).order_by(Modulo.numero)
    )
    modulos = r.scalars().all()

    docentes_map, asignaturas_map, carreras_map, niveles_map = await cargar_catalogos(db)

    # Hoja por cada módulo
    for modulo in modulos:
        ws = wb.create_sheet(title=f"MÓDULO {modulo.numero}")
        ws.row_dimensions[1].height = 22
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[3].height = 18
        ws.row_dimensions[4].height = 18

        celda_titulo(ws, 1, 1, 9, f"DOCENTE: {docente.nombre} {docente.apellido}".upper(), "1F3864", 13)
        celda_titulo(ws, 2, 1, 9, f"TIPO: {docente.tipo.value.replace('_', ' ').upper()}", "1F3864", 11)
        celda_titulo(ws, 3, 1, 9, f"PERIODO: {periodo.nombre}", "1F3864", 11)
        celda_titulo(ws, 4, 1, 9, f"{modulo.nombre.upper()} ({modulo.fecha_inicio} al {modulo.fecha_fin})", "2E75B6", 12)

        r = await db.execute(
            select(Horario)
            .where(Horario.modulo_id == modulo.id, Horario.docente_id == docente_id)
            .order_by(Horario.jornada, Horario.dia, Horario.hora_inicio)
        )
        horarios = r.scalars().all()

        fila = 6
        for jornada_key, jornada_label, horario_txt in [
            ("matutina", "MATUTINO (LUNES A VIERNES)", "08:00 - 12:00"),
            ("nocturna", "NOCTURNO (LUNES A VIERNES)", "18:30 - 21:30"),
        ]:
            h_jornada = [h for h in horarios if h.jornada == jornada_key]
            if not h_jornada:
                continue

            ws.row_dimensions[fila].height = 18
            celda_subtitulo(ws, fila, 1, 9, f"MODALIDAD PRESENCIAL — {jornada_label}", "2E75B6")
            fila += 1

            encabezados = ["MÓDULO", "FECHA INICIO", "FECHA FIN", "ASIGNATURA", "NIVEL", "PARALELO", "HORARIO", "CARRERA", "OBSERVACIÓN"]
            ws.row_dimensions[fila].height = 30
            for col, enc in enumerate(encabezados, 1):
                celda_encabezado(ws.cell(row=fila, column=col, value=enc))
            fila += 1

            for idx, h in enumerate(h_jornada):
                par = idx % 2 == 0
                asig = asignaturas_map.get(h.asignatura_id)
                datos = [
                    modulo.numero,
                    modulo.fecha_inicio,
                    modulo.fecha_fin,
                    asig.nombre if asig else "N/A",
                    niveles_map.get(h.nivel_id, ""),
                    h.paralelo,
                    f"{h.hora_inicio} - {h.hora_fin}",
                    carreras_map.get(h.carrera_id, "N/A"),
                    h.observaciones or "",
                ]
                for col, val in enumerate(datos, 1):
                    c = ws.cell(row=fila, column=col, value=val)
                    if col in [1, 2, 3, 5, 6]:
                        celda_centro(c, par)
                    else:
                        celda_dato(c, par)
                fila += 1
            fila += 1

        autoajustar(ws, {1: 10, 2: 14, 3: 14, 4: 35, 5: 8, 6: 10, 7: 16, 8: 30, 9: 20})

    # Hoja carga horaria del docente
    ws_carga = wb.create_sheet(title="Carga horaria")
    ws_carga.row_dimensions[1].height = 22

    celda_titulo(ws_carga, 1, 1, 6, f"CARGA HORARIA — {docente.nombre} {docente.apellido}".upper(), "1F3864", 13)
    celda_titulo(ws_carga, 2, 1, 6, f"PERIODO: {periodo.nombre}", "1F3864", 11)

    fila = 4
    encabezados = ["MÓDULO", "ASIGNATURAS", "HORAS", "MÍNIMO", "MÁXIMO", "ESTADO"]
    ws_carga.row_dimensions[fila].height = 30
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws_carga.cell(row=fila, column=col, value=enc))
    fila += 1

    total_horas = 0
    es_tc = docente.tipo.value == "tiempo_completo"

    for modulo in modulos:
        r = await db.execute(
            select(CargaHoraria).where(
                CargaHoraria.docente_id == docente_id,
                CargaHoraria.modulo_id == modulo.id,
            )
        )
        carga = r.scalar_one_or_none()
        asig = carga.total_asignaturas if carga else 0
        horas = round(carga.total_horas, 1) if carga else 0
        total_horas += horas

        ws_carga.cell(row=fila, column=1, value=modulo.nombre).border = borde_completo()
        celda_centro(ws_carga.cell(row=fila, column=2, value=asig))
        celda_centro(ws_carga.cell(row=fila, column=3, value=horas))
        celda_centro(ws_carga.cell(row=fila, column=4, value=272 if es_tc else "N/A"))
        celda_centro(ws_carga.cell(row=fila, column=5, value=380 if es_tc else "N/A"))

        if es_tc:
            estado = "✓ OK" if 272 <= total_horas <= 380 else "⚠ Revisar"
            color = "375623" if 272 <= total_horas <= 380 else "FF0000"
        else:
            estado = "Tiempo Parcial"
            color = "2E75B6"

        ce = ws_carga.cell(row=fila, column=6, value=estado)
        ce.font = Font(bold=True, color=color, size=10)
        ce.border = borde_completo()
        ce.alignment = Alignment(horizontal="center")
        fila += 1

        # Hoja carga total
    ws_total = wb.create_sheet(title="Carga horaria total")
    ws_total.row_dimensions[1].height = 22
    celda_titulo(ws_total, 1, 1, 6, f"CARGA HORARIA TOTAL — {docente.nombre} {docente.apellido}".upper(), "7B2C2C", 13)
    celda_titulo(ws_total, 2, 1, 6, f"PERIODO: {periodo.nombre}", "7B2C2C", 11)

    fila = 4
    encabezados = ["MÓDULO", "ASIGNATURAS", "HORAS", "MÍNIMO", "MÁXIMO", "ESTADO"]
    ws_total.row_dimensions[fila].height = 30
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws_total.cell(row=fila, column=col, value=enc))
    fila += 1

    total_horas_final = 0
    for modulo in modulos:
        r = await db.execute(
            select(CargaHoraria).where(
                CargaHoraria.docente_id == docente_id,
                CargaHoraria.modulo_id == modulo.id,
            )
        )
        carga = r.scalar_one_or_none()
        asig = carga.total_asignaturas if carga else 0
        horas = round(carga.total_horas, 1) if carga else 0
        total_horas_final += horas

        ws_total.cell(row=fila, column=1, value=modulo.nombre).border = borde_completo()
        celda_centro(ws_total.cell(row=fila, column=2, value=asig))
        celda_centro(ws_total.cell(row=fila, column=3, value=horas))
        celda_centro(ws_total.cell(row=fila, column=4, value=272 if es_tc else "N/A"))
        celda_centro(ws_total.cell(row=fila, column=5, value=380 if es_tc else "N/A"))

        if es_tc:
            estado = "✓ OK" if 272 <= total_horas_final <= 380 else "⚠ Revisar"
            color = "375623" if 272 <= total_horas_final <= 380 else "FF0000"
        else:
            estado = "Tiempo Parcial"
            color = "2E75B6"

        ce = ws_total.cell(row=fila, column=6, value=estado)
        ce.font = Font(bold=True, color=color, size=10)
        ce.border = borde_completo()
        ce.alignment = Alignment(horizontal="center")
        fila += 1

    # Fila total
    ct = ws_total.cell(row=fila, column=1, value="TOTAL")
    ct.font = Font(bold=True, size=11)
    ct.border = borde_completo()
    celda_centro(ws_total.cell(row=fila, column=3, value=round(total_horas_final, 1)))
    ws_total.cell(row=fila, column=3).font = Font(bold=True, size=11)
    autoajustar(ws_total, {1: 20, 2: 14, 3: 12, 4: 12, 5: 12, 6: 16})




    # Fila total
    ct = ws_carga.cell(row=fila, column=1, value="TOTAL")
    ct.font = Font(bold=True, size=11)
    ct.border = borde_completo()
    celda_centro(ws_carga.cell(row=fila, column=3, value=round(total_horas, 1)))
    ws_carga.cell(row=fila, column=3).font = Font(bold=True, size=11)

    autoajustar(ws_carga, {1: 20, 2: 14, 3: 12, 4: 12, 5: 12, 6: 16})

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


# ─── REPORTE POR CARRERA ──────────────────────────────────────────────────────

async def generar_excel_por_carrera(periodo_id: str, carrera_id: str, db: AsyncSession) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)

    r = await db.execute(select(PeriodoAcademico).where(PeriodoAcademico.id == periodo_id))
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise Exception("Período no encontrado")

    r = await db.execute(select(Carrera).where(Carrera.id == carrera_id))
    carrera = r.scalar_one_or_none()
    if not carrera:
        raise Exception("Carrera no encontrada")

    r = await db.execute(
        select(Modulo).where(Modulo.periodo_id == periodo_id).order_by(Modulo.numero)
    )
    modulos = r.scalars().all()

    # Hojas por módulo filtradas por carrera
    for modulo in modulos:
        ws = wb.create_sheet(title=f"MÓDULO {modulo.numero}")
        r = await db.execute(
            select(Horario)
            .where(Horario.modulo_id == modulo.id, Horario.carrera_id == carrera_id)
            .order_by(Horario.jornada, Horario.nivel_id, Horario.paralelo, Horario.hora_inicio)
        )
        horarios = r.scalars().all()
        if horarios:
            await escribir_hoja_modulo(ws, modulo, periodo, horarios, db)
        else:
            ws.cell(row=1, column=1, value=f"Sin horarios para {modulo.nombre}")

    # Carga horaria solo de docentes que tienen clases en esta carrera
    ws_carga = wb.create_sheet(title="Carga horaria por modulos")
    await escribir_hoja_carga_modulos(ws_carga, periodo, modulos, db)

    ws_total = wb.create_sheet(title="Carga horaria total")
    await escribir_hoja_carga_total(ws_total, periodo, db)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


# ─── REPORTE POR NIVEL ────────────────────────────────────────────────────────

async def generar_excel_por_nivel(periodo_id: str, nivel_id: str, db: AsyncSession) -> bytes:
    wb = Workbook()
    wb.remove(wb.active)

    r = await db.execute(select(PeriodoAcademico).where(PeriodoAcademico.id == periodo_id))
    periodo = r.scalar_one_or_none()
    if not periodo:
        raise Exception("Período no encontrado")

    r = await db.execute(select(Nivel).where(Nivel.id == nivel_id))
    nivel = r.scalar_one_or_none()
    if not nivel:
        raise Exception("Nivel no encontrado")

    r = await db.execute(
        select(Modulo).where(Modulo.periodo_id == periodo_id).order_by(Modulo.numero)
    )
    modulos = r.scalars().all()
    docentes_map, asignaturas_map, carreras_map, niveles_map = await cargar_catalogos(db)

    # Hojas por módulo
    for modulo in modulos:
        ws = wb.create_sheet(title=f"MÓDULO {modulo.numero}")
        ws.row_dimensions[1].height = 22
        ws.row_dimensions[4].height = 18

        celda_titulo(ws, 1, 1, 9, f"NIVEL: {nivel.nombre or f'Nivel {nivel.numero}'}", "1F3864", 13)
        celda_titulo(ws, 2, 1, 9, f"PERIODO: {periodo.nombre}", "1F3864", 11)
        celda_titulo(ws, 3, 1, 9, f"{modulo.nombre.upper()} ({modulo.fecha_inicio} al {modulo.fecha_fin})", "2E75B6", 12)

        r = await db.execute(
            select(Horario)
            .where(Horario.modulo_id == modulo.id, Horario.nivel_id == nivel_id)
            .order_by(Horario.jornada, Horario.paralelo, Horario.hora_inicio)
        )
        horarios = r.scalars().all()

        fila = 5
        for jornada_key, jornada_label in [
            ("matutina", "MATUTINO (LUNES A VIERNES)"),
            ("nocturna", "NOCTURNO (LUNES A VIERNES)"),
        ]:
            h_jornada = [h for h in horarios if h.jornada == jornada_key]
            if not h_jornada:
                continue

            celda_subtitulo(ws, fila, 1, 9, f"MODALIDAD PRESENCIAL — {jornada_label}", "2E75B6")
            fila += 1

            encabezados = ["MÓDULO", "FECHA INICIO", "FECHA FIN", "ASIGNATURA", "PARALELO", "HORAS", "HORARIO", "DOCENTE", "OBSERVACIÓN"]
            ws.row_dimensions[fila].height = 30
            for col, enc in enumerate(encabezados, 1):
                celda_encabezado(ws.cell(row=fila, column=col, value=enc))
            fila += 1

            for idx, h in enumerate(h_jornada):
                par = idx % 2 == 0
                asig = asignaturas_map.get(h.asignatura_id)
                datos = [
                    modulo.numero,
                    modulo.fecha_inicio,
                    modulo.fecha_fin,
                    asig.nombre if asig else "N/A",
                    h.paralelo,
                    asig.horas_modulo if asig else 0,
                    f"{h.hora_inicio} - {h.hora_fin}",
                    docentes_map.get(h.docente_id, "POR DEFINIR").upper(),
                    h.observaciones or "",
                ]
                for col, val in enumerate(datos, 1):
                    c = ws.cell(row=fila, column=col, value=val)
                    if col in [1, 2, 3, 5, 6]:
                        celda_centro(c, par)
                    else:
                        celda_dato(c, par)
                    if col in [2, 3]:
                        c.number_format = 'DD/MM/YYYY'
                fila += 1
            fila += 1

        autoajustar(ws, {1: 10, 2: 14, 3: 14, 4: 35, 5: 10, 6: 8, 7: 16, 8: 25, 9: 20})

    # Obtener docentes que tienen horarios en este nivel
    r = await db.execute(
        select(Docente.id).join(Horario, Horario.docente_id == Docente.id)
        .where(Horario.periodo_id == periodo_id, Horario.nivel_id == nivel_id)
        .distinct()
    )
    docente_ids = [row[0] for row in r.fetchall()]

    r = await db.execute(
        select(Docente).where(Docente.id.in_(docente_ids)).order_by(Docente.apellido)
    )
    docentes_nivel = r.scalars().all()

    # Hoja carga por módulos
    ws_carga = wb.create_sheet(title="Carga horaria por modulos")
    ws_carga.row_dimensions[1].height = 22
    celda_titulo(ws_carga, 1, 1, 8, f"CARGA HORARIA POR MÓDULO — {nivel.nombre or f'Nivel {nivel.numero}'}", "375623", 13)
    celda_titulo(ws_carga, 2, 1, 8, f"PERIODO: {periodo.nombre}", "375623", 11)

    fila = 4
    encabezados = ["DOCENTES", "TIPO", "MÓDULO 1\n(asig)", "MÓDULO 2\n(asig)", "MÓDULO 3\n(asig)", "TOTAL\nASIG", "HORAS TC", "HORAS TP"]
    ws_carga.row_dimensions[fila].height = 35
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws_carga.cell(row=fila, column=col, value=enc))
    fila += 1

    for idx, docente in enumerate(docentes_nivel):
        par = idx % 2 == 0
        nombre = f"{docente.nombre} {docente.apellido}".upper()
        tipo = "TC" if docente.tipo.value == "tiempo_completo" else "TP"

        celda_dato(ws_carga.cell(row=fila, column=1, value=nombre), par)
        celda_centro(ws_carga.cell(row=fila, column=2, value=tipo), par)

        total_asig = 0
        total_horas_tc = 0
        total_horas_tp = 0

        for i, modulo in enumerate(modulos[:3], 3):
            r2 = await db.execute(
                select(CargaHoraria).where(
                    CargaHoraria.docente_id == docente.id,
                    CargaHoraria.modulo_id == modulo.id,
                )
            )
            carga = r2.scalar_one_or_none()
            asig = carga.total_asignaturas if carga else 0
            horas = carga.total_horas if carga else 0
            total_asig += asig
            if tipo == "TC":
                total_horas_tc += horas
            else:
                total_horas_tp += horas

            c = ws_carga.cell(row=fila, column=i, value=asig)
            celda_centro(c, par)
            if asig >= 3:
                c.fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")

        ct = ws_carga.cell(row=fila, column=6, value=total_asig)
        celda_centro(ct, par)
        ct.font = Font(bold=True, size=10)
        celda_centro(ws_carga.cell(row=fila, column=7, value=round(total_horas_tc, 1)), par)
        celda_centro(ws_carga.cell(row=fila, column=8, value=round(total_horas_tp, 1)), par)
        fila += 1

    autoajustar(ws_carga, {1: 30, 2: 8, 3: 14, 4: 14, 5: 14, 6: 10, 7: 10, 8: 10})

    # Hoja carga total
    ws_total = wb.create_sheet(title="Carga horaria total")
    ws_total.row_dimensions[1].height = 22
    celda_titulo(ws_total, 1, 1, 7, f"CARGA HORARIA TOTAL — {nivel.nombre or f'Nivel {nivel.numero}'}", "7B2C2C", 13)
    celda_titulo(ws_total, 2, 1, 7, f"PERIODO: {periodo.nombre}", "7B2C2C", 11)

    fila = 4
    encabezados = ["DOCENTES", "MÓDULO 1", "MÓDULO 2", "MÓDULO 3", "TOTAL", "MÍNIMO", "ESTADO"]
    ws_total.row_dimensions[fila].height = 30
    for col, enc in enumerate(encabezados, 1):
        celda_encabezado(ws_total.cell(row=fila, column=col, value=enc))
    fila += 1

    ws_total.cell(row=fila, column=6, value=272).font = Font(bold=True, color="FF0000", size=10)
    ws_total.cell(row=fila, column=6).alignment = Alignment(horizontal="center")
    fila += 1

    for idx, docente in enumerate(docentes_nivel):
        par = idx % 2 == 0
        nombre = f"{docente.nombre} {docente.apellido}".upper()
        es_tc = docente.tipo.value == "tiempo_completo"

        celda_dato(ws_total.cell(row=fila, column=1, value=nombre), par)

        total_horas = 0
        for i, modulo in enumerate(modulos[:3], 2):
            r3 = await db.execute(
                select(CargaHoraria).where(
                    CargaHoraria.docente_id == docente.id,
                    CargaHoraria.modulo_id == modulo.id,
                )
            )
            carga = r3.scalar_one_or_none()
            horas = round(carga.total_horas, 1) if carga else 0
            total_horas += horas
            celda_centro(ws_total.cell(row=fila, column=i, value=horas), par)

        ct = ws_total.cell(row=fila, column=5, value=round(total_horas, 1))
        celda_centro(ct, par)
        ct.font = Font(bold=True, size=10)
        ws_total.cell(row=fila, column=6, value=272 if es_tc else "N/A").border = borde_completo()

        if es_tc:
            if total_horas < 272:
                estado = "⚠ BAJO MÍNIMO"
                color_txt = "FF0000"
            elif total_horas > 380:
                estado = "⚠ EXCEDE MÁXIMO"
                color_txt = "FF0000"
            else:
                estado = "✓ OK"
                color_txt = "375623"
        else:
            estado = "TIEMPO PARCIAL"
            color_txt = "2E75B6"

        ce = ws_total.cell(row=fila, column=7, value=estado)
        ce.font = Font(bold=True, color=color_txt, size=10)
        ce.border = borde_completo()
        ce.alignment = Alignment(horizontal="center", vertical="center")
        fila += 1

    autoajustar(ws_total, {1: 30, 2: 12, 3: 12, 4: 12, 5: 10, 6: 10, 7: 18})

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()