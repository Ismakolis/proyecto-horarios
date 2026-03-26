import re
from pydantic import BaseModel, field_validator, model_validator
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
            raise ValueError("El numero de modulo debe ser 1, 2 o 3")
        return v

    @model_validator(mode="after")
    def fechas_validas(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin del modulo debe ser posterior a la fecha de inicio")
        return self


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

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre del periodo debe tener al menos 3 caracteres")
        if len(v) > 100:
            raise ValueError("El nombre no puede superar los 100 caracteres")
        return v

    @field_validator("anio")
    @classmethod
    def anio_valido(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("El ano debe estar entre 2000 y 2100")
        return v

    @field_validator("numero")
    @classmethod
    def numero_valido(cls, v):
        if v not in [1, 2]:
            raise ValueError("El numero de periodo debe ser 1 o 2")
        return v

    @field_validator("paralelos_por_nivel")
    @classmethod
    def paralelos_valido(cls, v):
        if v < 1 or v > 10:
            raise ValueError("Los paralelos deben estar entre 1 y 10")
        return v

    @model_validator(mode="after")
    def fechas_validas(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha de fin del periodo debe ser posterior a la fecha de inicio")
        return self


class PeriodoUpdate(BaseModel):
    nombre: Optional[str] = None
    paralelos_por_nivel: Optional[int] = None
    activo: Optional[bool] = None

    @field_validator("paralelos_por_nivel")
    @classmethod
    def paralelos_valido(cls, v):
        if v is None:
            return v
        if v < 1 or v > 10:
            raise ValueError("Los paralelos deben estar entre 1 y 10")
        return v


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
