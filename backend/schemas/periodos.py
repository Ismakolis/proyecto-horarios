from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date


class ModuloCreate(BaseModel):
    numero: int
    nombre: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date

    @field_validator("numero")
    @classmethod
    def numero_valido(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("El número de módulo debe ser 1, 2 o 3")
        return v


class ModuloResponse(BaseModel):
    id: str
    numero: int
    nombre: Optional[str]
    fecha_inicio: date
    fecha_fin: date
    periodo_id: str

    model_config = {"from_attributes": True}


class PeriodoCreate(BaseModel):
    nombre: str
    anio: int
    numero: int
    fecha_inicio: date
    fecha_fin: date
    paralelos_por_nivel: int = 1
    modulos: Optional[List[ModuloCreate]] = []

    @field_validator("numero")
    @classmethod
    def numero_valido(cls, v):
        if v not in [1, 2]:
            raise ValueError("El número de período debe ser 1 o 2")
        return v

    @field_validator("paralelos_por_nivel")
    @classmethod
    def paralelos_valido(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Los paralelos deben estar entre 1 y 10")
        return v


class PeriodoUpdate(BaseModel):
    nombre: Optional[str] = None
    paralelos_por_nivel: Optional[int] = None
    activo: Optional[bool] = None


class PeriodoResponse(BaseModel):
    id: str
    nombre: str
    anio: int
    numero: int
    fecha_inicio: date
    fecha_fin: date
    paralelos_por_nivel: int
    activo: bool
    modulos: List[ModuloResponse] = []

    model_config = {"from_attributes": True}


class PeriodoListResponse(BaseModel):
    id: str
    nombre: str
    anio: int
    numero: int
    paralelos_por_nivel: int
    activo: bool
    modulos: List[ModuloResponse] = []

    model_config = {"from_attributes": True}