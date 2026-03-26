import re
from pydantic import BaseModel, EmailStr, field_validator
from models.models import TipoDocente, DiaSemana, Jornada
from typing import Optional, List


class DisponibilidadBase(BaseModel):
    dia: DiaSemana
    jornada: Jornada
    disponible: bool = True


class DisponibilidadResponse(DisponibilidadBase):
    id: str
    model_config = {"from_attributes": True}


class DocenteCreate(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    email: EmailStr
    tipo: TipoDocente
    titulo: Optional[str] = None
    disponibilidades: Optional[List[DisponibilidadBase]] = []

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
        if len(v) > 100:
            raise ValueError("El nombre no puede superar los 100 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El nombre solo puede contener letras, espacios y guiones")
        return v.title()

    @field_validator("apellido")
    @classmethod
    def apellido_valido(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El apellido debe tener al menos 2 caracteres")
        if len(v) > 100:
            raise ValueError("El apellido no puede superar los 100 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+$", v):
            raise ValueError("El apellido solo puede contener letras, espacios y guiones")
        return v.title()

    @field_validator("titulo")
    @classmethod
    def titulo_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 200:
            raise ValueError("El titulo no puede superar los 200 caracteres")
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

    @field_validator("titulo")
    @classmethod
    def titulo_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if v and not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\.\-'0-9,]+$", v):
            raise ValueError("El titulo contiene caracteres no permitidos")
        return v


class DocenteResponse(BaseModel):
    id: str
    cedula: str
    nombre: str
    apellido: str
    email: str
    tipo: TipoDocente
    titulo: Optional[str]
    activo: bool
    disponibilidades: List[DisponibilidadResponse] = []

    model_config = {"from_attributes": True}


class DocenteListResponse(BaseModel):
    id: str
    cedula: str
    nombre: str
    apellido: str
    email: str
    tipo: TipoDocente
    activo: bool

    model_config = {"from_attributes": True}
