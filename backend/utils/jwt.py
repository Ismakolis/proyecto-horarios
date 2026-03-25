from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.models import Usuario, RolUsuario
import os

SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-cambiar-en-produccion-12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido")

    result = await db.execute(select(Usuario).where(Usuario.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


def require_roles(*roles: RolUsuario):
    async def checker(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        token = credentials.credentials
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        result = await db.execute(select(Usuario).where(Usuario.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.activo:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        if user.rol not in roles:
            raise HTTPException(status_code=403, detail=f"Acceso denegado")
        return user
    return checker


solo_coordinador = require_roles(RolUsuario.COORDINADOR)
coordinador_o_admin = require_roles(RolUsuario.COORDINADOR, RolUsuario.ADMINISTRATIVO)
cualquier_rol = require_roles(RolUsuario.COORDINADOR, RolUsuario.ADMINISTRATIVO, RolUsuario.DOCENTE)