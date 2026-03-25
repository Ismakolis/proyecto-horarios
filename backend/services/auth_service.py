from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from models.models import Usuario, RolUsuario
from schemas.auth import UsuarioCreate, LoginRequest
from utils.jwt import hash_password, verify_password, create_access_token
import uuid


async def registrar_usuario(data: UsuarioCreate, db: AsyncSession) -> dict:
    # Verificar email único
    result = await db.execute(select(Usuario).where(Usuario.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email"
        )

    usuario = Usuario(
        id=str(uuid.uuid4()),
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        password_hash=hash_password(data.password),
        rol=data.rol,
    )
    db.add(usuario)
    await db.flush()
    await db.refresh(usuario)
    return usuario


async def login_usuario(data: LoginRequest, db: AsyncSession) -> dict:
    result = await db.execute(select(Usuario).where(Usuario.email == data.email))
    usuario = result.scalar_one_or_none()

    if not usuario or not verify_password(data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador"
        )

    # Buscar docente_id si es docente
    docente_id = None
    if usuario.rol.value == "docente":
        from models.models import Docente
        r = await db.execute(select(Docente).where(Docente.email == usuario.email))
        docente = r.scalar_one_or_none()
        if docente:
            docente_id = docente.id

    token = create_access_token({"sub": usuario.id, "rol": usuario.rol.value})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "email": usuario.email,
            "rol": usuario.rol,
            "activo": usuario.activo,
            "docente_id": docente_id,
        }
    }

async def cambiar_password(usuario: Usuario, password_actual: str, password_nueva: str, db: AsyncSession):
    if not verify_password(password_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    usuario.password_hash = hash_password(password_nueva)
    await db.flush()
    return {"mensaje": "Contraseña actualizada correctamente"}