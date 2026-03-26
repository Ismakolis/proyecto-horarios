import re
from pydantic import BaseModel, field_validator
from typing import Optional, List


class NivelCreate(BaseModel):
    numero: int
    nombre: Optional[str] = None
    paralelos_matutina: int = 1
    paralelos_nocturna: int = 1

    @field_validator("numero")
    @classmethod
    def numero_positivo(cls, v):
        if v < 1 or v > 20:
            raise ValueError("El numero de nivel debe estar entre 1 y 20")
        return v

    @field_validator("paralelos_matutina", "paralelos_nocturna")
    @classmethod
    def paralelos_valido(cls, v):
        if v < 0 or v > 10:
            raise ValueError("Los paralelos deben estar entre 0 y 10")
        return v


class NivelUpdate(BaseModel):
    paralelos_matutina: Optional[int] = None
    paralelos_nocturna: Optional[int] = None

    @field_validator("paralelos_matutina", "paralelos_nocturna")
    @classmethod
    def paralelos_valido(cls, v):
        if v is None:
            return v
        if v < 0 or v > 10:
            raise ValueError("Los paralelos deben estar entre 0 y 10")
        return v


class NivelResponse(BaseModel):
    id: str
    numero: int
    nombre: Optional[str]
    paralelos_matutina: int
    paralelos_nocturna: int
    carrera_id: str

    model_config = {"from_attributes": True}


class CarreraCreate(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    niveles: Optional[List[NivelCreate]] = []

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre de la carrera debe tener al menos 3 caracteres")
        if len(v) > 150:
            raise ValueError("El nombre no puede superar los 150 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.\(\)0-9]+$", v):
            raise ValueError("El nombre de la carrera contiene caracteres no permitidos")
        return v

    @field_validator("codigo")
    @classmethod
    def codigo_valido(cls, v):
        v = v.strip().upper()
        if len(v) < 2:
            raise ValueError("El codigo debe tener al menos 2 caracteres")
        if len(v) > 20:
            raise ValueError("El codigo no puede superar los 20 caracteres")
        if not re.match(r"^[A-Z0-9\-_]+$", v):
            raise ValueError("El codigo solo puede contener letras mayusculas, numeros, guiones y guiones bajos")
        return v

    @field_validator("descripcion")
    @classmethod
    def descripcion_valida(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError("La descripcion no puede superar los 500 caracteres")
        return v


class CarreraUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("El nombre de la carrera debe tener al menos 3 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.\(\)0-9]+$", v):
            raise ValueError("El nombre de la carrera contiene caracteres no permitidos")
        return v


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

    @field_validator("nombre")
    @classmethod
    def nombre_valido(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("El nombre de la asignatura debe tener al menos 2 caracteres")
        if len(v) > 150:
            raise ValueError("El nombre no puede superar los 150 caracteres")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.\(\)0-9,/]+$", v):
            raise ValueError("El nombre de la asignatura contiene caracteres no permitidos")
        return v

    @field_validator("codigo")
    @classmethod
    def codigo_valido(cls, v):
        if v is None:
            return v
        v = v.strip().upper()
        if len(v) > 20:
            raise ValueError("El codigo no puede superar los 20 caracteres")
        if not re.match(r"^[A-Z0-9\-_]+$", v):
            raise ValueError("El codigo solo puede contener letras mayusculas, numeros y guiones")
        return v

    @field_validator("numero_modulo")
    @classmethod
    def modulo_valido(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("El modulo debe ser 1, 2 o 3")
        return v

    @field_validator("horas_modulo")
    @classmethod
    def horas_validas(cls, v):
        if v <= 0:
            raise ValueError("Las horas deben ser mayores a 0")
        if v > 500:
            raise ValueError("Las horas del modulo no pueden superar 500")
        return v


class AsignaturaUpdate(BaseModel):
    nombre: Optional[str] = None
    horas_semanales: Optional[float] = None
    horas_modulo: Optional[float] = None
    activo: Optional[bool] = None

    @field_validator("horas_modulo", "horas_semanales")
    @classmethod
    def horas_validas(cls, v):
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Las horas deben ser mayores a 0")
        if v > 500:
            raise ValueError("Las horas no pueden superar 500")
        return v


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
