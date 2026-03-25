from pydantic import BaseModel, field_validator
from typing import Optional, List


class NivelCreate(BaseModel):
    numero: int
    nombre: Optional[str] = None
    paralelos: int = 1

    @field_validator("numero")
    @classmethod
    def numero_positivo(cls, v):
        if v < 1:
            raise ValueError("El número de nivel debe ser mayor a 0")
        return v

    @field_validator("paralelos")
    @classmethod
    def paralelos_valido(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Los paralelos deben estar entre 1 y 10")
        return v



class NivelResponse(BaseModel):
    id: str
    numero: int
    nombre: Optional[str]
    paralelos: int
    carrera_id: str

    model_config = {"from_attributes": True}


class CarreraCreate(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    niveles: Optional[List[NivelCreate]] = []

    @field_validator("codigo")
    @classmethod
    def codigo_upper(cls, v):
        return v.strip().upper()


class CarreraUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CarreraResponse(BaseModel):
    id: str
    nombre: str
    codigo: str
    descripcion: Optional[str]
    activo: bool
    niveles: List[NivelResponse] = []

    model_config = {"from_attributes": True}


class CarreraListResponse(BaseModel):
    id: str
    nombre: str
    codigo: str
    activo: bool

    model_config = {"from_attributes": True}

class CarreraConNivelesResponse(BaseModel):
    id: str
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    activo: bool
    niveles: List[NivelResponse] = []

    model_config = {"from_attributes": True}

class AsignaturaCreate(BaseModel):
    carrera_id: str
    nivel_id: str
    nombre: str
    codigo: Optional[str] = None
    numero_modulo: int = 1
    horas_modulo: float = 32.0

    @field_validator("numero_modulo")
    @classmethod
    def modulo_valido(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("El módulo debe ser 1, 2 o 3")
        return v

    @field_validator("horas_modulo")
    @classmethod
    def horas_positivas(cls, v):
        if v <= 0:
            raise ValueError("Las horas deben ser mayores a 0")
        return v


class AsignaturaUpdate(BaseModel):
    nombre: Optional[str] = None
    horas_semanales: Optional[float] = None
    horas_modulo: Optional[float] = None
    activo: Optional[bool] = None


class AsignaturaResponse(BaseModel):
    id: str
    nombre: str
    codigo: Optional[str]
    numero_modulo: int
    horas_modulo: float
    horas_semanales: float
    carrera_id: str
    nivel_id: str
    activo: bool

    model_config = {"from_attributes": True}