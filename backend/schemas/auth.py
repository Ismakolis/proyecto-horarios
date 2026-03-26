import re
from pydantic import BaseModel, EmailStr, field_validator
from models.models import RolUsuario
from typing import Optional


class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    rol: RolUsuario = RolUsuario.ADMINISTRATIVO

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El nombre solo puede contener letras")
        return v.title()

    @field_validator("apellido")
    @classmethod
    def apellido_valido(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El apellido debe tener al menos 2 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El apellido solo puede contener letras")
        return v.title()

    @field_validator("password")
    @classmethod
    def password_minimo(cls, v):
        if len(v) < 6:
            raise ValueError("La contrasena debe tener al menos 6 caracteres")
        return v


class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    apellido: str
    email: str
    rol: RolUsuario
    activo: bool
    docente_id: Optional[str] = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class ChangePasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def password_minimo(cls, v):
        if len(v) < 6:
            raise ValueError("La contrasena nueva debe tener al menos 6 caracteres")
        return v
