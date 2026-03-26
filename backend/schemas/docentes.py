import re
from pydantic import BaseModel, EmailStr, field_validator
from models.models import TipoDocente
from typing import Optional, List


class DocenteCreate(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    email: EmailStr
    tipo: TipoDocente
    titulo: Optional[str] = None

    @field_validator("cedula")
    @classmethod
    def cedula_valida(cls, v):
        v = v.strip()
        if not v.isdigit() or len(v) != 10:
            raise ValueError("La cedula debe tener exactamente 10 digitos numericos")
        return v

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

    @field_validator("titulo")
    @classmethod
    def titulo_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\-'0-9,]+$", v):
            raise ValueError("El titulo contiene caracteres no permitidos")
        return v


class DocenteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo: Optional[TipoDocente] = None
    titulo: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El nombre solo puede contener letras")
        return v.title()

    @field_validator("apellido")
    @classmethod
    def apellido_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El apellido debe tener al menos 2 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El apellido solo puede contener letras")
        return v.title()


class CrearAccesoDocente(BaseModel):
    """Schema para crear usuario/acceso a un docente existente"""
    docente_id: str
    password: str

    @field_validator("password")
    @classmethod
    def password_minimo(cls, v):
        if len(v) < 6:
            raise ValueError("La contrasena debe tener al menos 6 caracteres")
        return v


class HabilidadDocenteCreate(BaseModel):
    """Asignar asignaturas que puede dictar un docente"""
    asignatura_ids: List[str]


class HabilidadDocenteResponse(BaseModel):
    id: str
    asignatura_id: str
    nombre_asignatura: Optional[str] = None

    model_config = {"from_attributes": True}


class DocenteResponse(BaseModel):
    id: str
    cedula: str
    nombre: str
    apellido: str
    email: str
    tipo: TipoDocente
    titulo: Optional[str]
    activo: bool
    tiene_acceso: Optional[bool] = False

    model_config = {"from_attributes": True}


class DocenteListResponse(BaseModel):
    id: str
    cedula: str
    nombre: str
    apellido: str
    email: str
    tipo: TipoDocente
    activo: bool
    tiene_acceso: Optional[bool] = False

    model_config = {"from_attributes": True}
