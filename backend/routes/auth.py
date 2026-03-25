from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.auth import UsuarioCreate, LoginRequest, TokenResponse, ChangePasswordRequest
from services.auth_service import registrar_usuario, login_usuario, cambiar_password
from utils.jwt import get_current_user, solo_coordinador
from models.models import Usuario, RolUsuario

router = APIRouter()


@router.post("/registro", status_code=201)
async def registro(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(solo_coordinador),
):
    return await registrar_usuario(data, db)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_usuario(data, db)


@router.get("/me")
async def mi_perfil(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from models.models import Docente

    docente_id = None
    if current_user.rol == RolUsuario.DOCENTE:
        r = await db.execute(
            select(Docente).where(Docente.email == current_user.email)
        )
        docente = r.scalar_one_or_none()
        if docente:
            docente_id = docente.id

    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "email": current_user.email,
        "rol": current_user.rol,
        "activo": current_user.activo,
        "docente_id": docente_id,
    }


@router.put("/cambiar-password")
async def cambiar_mi_password(
    data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await cambiar_password(current_user, data.password_actual, data.password_nueva, db)


@router.post("/seed-admin", status_code=201)
async def crear_primer_admin(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    r = await db.execute(select(Usuario).where(Usuario.rol == RolUsuario.COORDINADOR))
    if r.scalar_one_or_none():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Ya existe un coordinador. Use /login")

    data = UsuarioCreate(
        nombre="Admin",
        apellido="ITQ",
        email="admin@itq.edu.ec",
        password="Admin123",
        rol=RolUsuario.COORDINADOR,
    )
    return await registrar_usuario(data, db)