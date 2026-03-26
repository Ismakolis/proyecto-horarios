from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from utils.excel import generar_excel, generar_excel_por_docente, generar_excel_por_carrera, generar_excel_por_nivel
from utils.jwt import coordinador_o_admin
from models.models import Usuario
import io

router = APIRouter()


@router.get("/excel/{periodo_id}")
async def exportar_excel_general(
    periodo_id: str,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(coordinador_o_admin),
):
    """Excel general con todos los módulos + carga horaria"""
    try:
        contenido = await generar_excel(periodo_id, db)
        return StreamingResponse(
            io.BytesIO(contenido),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=horarios_general_{periodo_id}.xlsx"}
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/excel/docente/{docente_id}")
async def exportar_excel_docente(
    docente_id: str,
    periodo_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(coordinador_o_admin),
):
    """Excel con horarios y carga horaria de un docente específico"""
    try:
        contenido = await generar_excel_por_docente(periodo_id, docente_id, db)
        return StreamingResponse(
            io.BytesIO(contenido),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=horario_docente_{docente_id}.xlsx"}
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/excel/carrera/{carrera_id}")
async def exportar_excel_carrera(
    carrera_id: str,
    periodo_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(coordinador_o_admin),
):
    """Excel con horarios por carrera incluyendo todas las sedes + carga horaria"""
    try:
        from sqlalchemy import select
        from models.models import Carrera
        r = await db.execute(select(Carrera).where(Carrera.id == carrera_id))
        carrera = r.scalar_one_or_none()
        nombre_archivo = carrera.nombre.replace(' ', '_') if carrera else carrera_id

        contenido = await generar_excel_por_carrera(periodo_id, carrera_id, db)
        return StreamingResponse(
            io.BytesIO(contenido),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=horario_{nombre_archivo}_todas_sedes.xlsx"}
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/excel/nivel/{nivel_id}")
async def exportar_excel_nivel(
    nivel_id: str,
    periodo_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(coordinador_o_admin),
):
    """Excel con horarios de un nivel específico + carga horaria"""
    try:
        contenido = await generar_excel_por_nivel(periodo_id, nivel_id, db)
        return StreamingResponse(
            io.BytesIO(contenido),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=horario_nivel_{nivel_id}.xlsx"}
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))