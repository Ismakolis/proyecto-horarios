from pydantic import BaseModel, field_validator
from models.models import DiaSemana, Jornada, EstadoHorario
from typing import Optional, List


class HorarioCreate(BaseModel):
    periodo_id: str
    modulo_id: str
    docente_id: str
    asignatura_id: str
    carrera_id: str
    nivel_id: str
    paralelo: str
    dia: DiaSemana
    jornada: Jornada
    hora_inicio: str
    hora_fin: str

    @field_validator("paralelo")
    @classmethod
    def paralelo_valido(cls, v):
        return v.strip().upper()

    @field_validator("hora_inicio", "hora_fin")
    @classmethod
    def hora_valida(cls, v):
        try:
            h, m = v.split(":")
            assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
        except:
            raise ValueError("Hora inválida, use formato HH:MM")
        return v


class HorarioUpdate(BaseModel):
    docente_id: Optional[str] = None
    dia: Optional[DiaSemana] = None
    jornada: Optional[Jornada] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None
    estado: Optional[EstadoHorario] = None
    observaciones: Optional[str] = None


class HorarioResponse(BaseModel):
    id: str
    periodo_id: str
    modulo_id: str
    docente_id: str
    asignatura_id: str
    carrera_id: str
    nivel_id: str
    paralelo: str
    dia: DiaSemana
    jornada: Jornada
    hora_inicio: str
    hora_fin: str
    estado: EstadoHorario
    generado_por_ia: bool
    observaciones: Optional[str]

    model_config = {"from_attributes": True}


class GenerarHorarioRequest(BaseModel):
    periodo_id: str
    modulo_id: str
    carrera_id: str        # puede ser ID o nombre de carrera
    carrera_nombre: Optional[str] = None  # si se envia, busca todas las sedes
    usar_ia: bool = False