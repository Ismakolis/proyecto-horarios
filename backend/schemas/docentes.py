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
            raise ValueError("La cédula debe tener exactamente 10 dígitos")
        return v


class DocenteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    tipo: Optional[TipoDocente] = None
    titulo: Optional[str] = None
    activo: Optional[bool] = None


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