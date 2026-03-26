from sqlalchemy import (
    Column, String, Integer, Boolean, Float, Enum,
    ForeignKey, DateTime, Date, Text, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from database import Base


# ─── ENUMS ────────────────────────────────────────────────────────────────────

class RolUsuario(str, enum.Enum):
    COORDINADOR = "coordinador"
    DOCENTE = "docente"
    ADMINISTRATIVO = "administrativo"

class TipoDocente(str, enum.Enum):
    TIEMPO_COMPLETO = "tiempo_completo"
    TIEMPO_PARCIAL = "tiempo_parcial"

class Jornada(str, enum.Enum):
    MATUTINA = "matutina"    # 08:00 - 12:00
    NOCTURNA = "nocturna"    # 18:30 - 21:30

class DiaSemana(str, enum.Enum):
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"

class EstadoHorario(str, enum.Enum):
    BORRADOR = "borrador"
    PUBLICADO = "publicado"
    ARCHIVADO = "archivado"


# ─── USUARIO ──────────────────────────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con docente (si el usuario es docente)
    docente = relationship("Docente", back_populates="usuario", uselist=False)

    def __repr__(self):
        return f"<Usuario {self.email} - {self.rol}>"


# ─── CARRERA ──────────────────────────────────────────────────────────────────

class Carrera(Base):
    __tablename__ = "carreras"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(150), nullable=False)
    codigo = Column(String(20), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    sede = Column(String(50), nullable=False, default="Quito")  # Quito, Conocoto, etc.
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    niveles = relationship("Nivel", back_populates="carrera", cascade="all, delete-orphan")
    asignaturas = relationship("Asignatura", back_populates="carrera")

    __table_args__ = (
        UniqueConstraint("nombre", "sede", name="uq_carrera_nombre_sede"),
    )

    def __repr__(self):
        return f"<Carrera {self.codigo} - {self.nombre}>"


# ─── NIVEL ────────────────────────────────────────────────────────────────────

class Nivel(Base):
    """Representa un nivel/semestre dentro de una carrera (ej: Nivel 1, Nivel 2...)"""
    __tablename__ = "niveles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    carrera_id = Column(String, ForeignKey("carreras.id"), nullable=False)
    numero = Column(Integer, nullable=False)  # 1, 2, 3...
    nombre = Column(String(50), nullable=True)  # "Primer Nivel", etc.
    paralelos_matutina = Column(Integer, nullable=False, default=1)
    paralelos_nocturna = Column(Integer, nullable=False, default=1)
    jornada_habilitada = Column(String(10), nullable=False, default="ambas")  # matutina, nocturna, ambas
    jornada_habilitada = Column(String(10), nullable=False, default="ambas")  # matutina, nocturna, ambas

    # Relaciones
    carrera = relationship("Carrera", back_populates="niveles")
    asignaturas = relationship("Asignatura", back_populates="nivel")

    __table_args__ = (
        UniqueConstraint("carrera_id", "numero", name="uq_carrera_nivel"),
    )

    def __repr__(self):
        return f"<Nivel {self.numero} - {self.carrera_id}>"


# ─── PERIODO ACADÉMICO ────────────────────────────────────────────────────────

class PeriodoAcademico(Base):
    """Hay 2 períodos por año. Cada período tiene 3 módulos."""
    __tablename__ = "periodos_academicos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(100), nullable=False)       # "2024-I", "2024-II"
    anio = Column(Integer, nullable=False)
    numero = Column(Integer, nullable=False)            # 1 o 2
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    paralelos_por_nivel = Column(Integer, default=1)    # Configurable por período
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    modulos = relationship("Modulo", back_populates="periodo", cascade="all, delete-orphan")
    horarios = relationship("Horario", back_populates="periodo")

    __table_args__ = (
        UniqueConstraint("anio", "numero", name="uq_periodo_anio_numero"),
        CheckConstraint("numero IN (1, 2)", name="ck_periodo_numero"),
    )

    def __repr__(self):
        return f"<Periodo {self.nombre}>"


# ─── MÓDULO ───────────────────────────────────────────────────────────────────

class Modulo(Base):
    """Cada período tiene 3 módulos"""
    __tablename__ = "modulos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    periodo_id = Column(String, ForeignKey("periodos_academicos.id"), nullable=False)
    numero = Column(Integer, nullable=False)    # 1, 2 o 3
    nombre = Column(String(50), nullable=True)  # "Módulo 1", etc.
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)

    # Relaciones
    periodo = relationship("PeriodoAcademico", back_populates="modulos")
    horarios = relationship("Horario", back_populates="modulo")

    __table_args__ = (
        UniqueConstraint("periodo_id", "numero", name="uq_modulo_periodo_numero"),
        CheckConstraint("numero IN (1, 2, 3)", name="ck_modulo_numero"),
    )

    def __repr__(self):
        return f"<Modulo {self.numero} del periodo {self.periodo_id}>"


# ─── DOCENTE ──────────────────────────────────────────────────────────────────

class Docente(Base):
    __tablename__ = "docentes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"), nullable=True)
    cedula = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    tipo = Column(Enum(TipoDocente), nullable=False)
    titulo = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="docente")
    disponibilidades = relationship("DisponibilidadDocente", back_populates="docente", cascade="all, delete-orphan")
    asignaturas_puede_dictar = relationship("DocenteAsignatura", back_populates="docente", cascade="all, delete-orphan")
    horarios = relationship("Horario", back_populates="docente")

    def __repr__(self):
        return f"<Docente {self.nombre} {self.apellido} - {self.tipo}>"


# ─── DISPONIBILIDAD DEL DOCENTE ───────────────────────────────────────────────

class DisponibilidadDocente(Base):
    """Define en qué días y jornadas puede trabajar cada docente"""
    __tablename__ = "disponibilidad_docentes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    docente_id = Column(String, ForeignKey("docentes.id"), nullable=False)
    dia = Column(Enum(DiaSemana), nullable=False)
    jornada = Column(Enum(Jornada), nullable=False)
    disponible = Column(Boolean, default=True)

    # Relaciones
    docente = relationship("Docente", back_populates="disponibilidades")

    __table_args__ = (
        UniqueConstraint("docente_id", "dia", "jornada", name="uq_disponibilidad_docente"),
    )


# ─── ASIGNATURA ───────────────────────────────────────────────────────────────

class Asignatura(Base):
    __tablename__ = "asignaturas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    carrera_id = Column(String, ForeignKey("carreras.id"), nullable=False)
    nivel_id = Column(String, ForeignKey("niveles.id"), nullable=False)
    nombre = Column(String(150), nullable=False)
    codigo = Column(String(20), nullable=True)
    horas_semanales = Column(Float, nullable=False)   # horas por semana
    horas_modulo = Column(Float, nullable=False)      # total horas en el módulo
    activo = Column(Boolean, default=True)
    numero_modulo = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    carrera = relationship("Carrera", back_populates="asignaturas")
    nivel = relationship("Nivel", back_populates="asignaturas")
    docentes_habilitados = relationship("DocenteAsignatura", back_populates="asignatura")
    horarios = relationship("Horario", back_populates="asignatura")

    def __repr__(self):
        return f"<Asignatura {self.codigo} - {self.nombre}>"


# ─── DOCENTE ↔ ASIGNATURA (perfil) ────────────────────────────────────────────

class DocenteAsignatura(Base):
    """Define qué asignaturas puede dictar cada docente (perfil/habilitación)"""
    __tablename__ = "docente_asignaturas"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    docente_id = Column(String, ForeignKey("docentes.id"), nullable=False)
    asignatura_id = Column(String, ForeignKey("asignaturas.id"), nullable=False)
    prioridad = Column(Integer, default=1)  # 1=alta, 2=media, 3=baja

    # Relaciones
    docente = relationship("Docente", back_populates="asignaturas_puede_dictar")
    asignatura = relationship("Asignatura", back_populates="docentes_habilitados")

    __table_args__ = (
        UniqueConstraint("docente_id", "asignatura_id", name="uq_docente_asignatura"),
    )


# ─── HORARIO ─────────────────────────────────────────────────────────────────

class Horario(Base):
    """
    Tabla central: una fila = una asignatura asignada a un docente
    en un módulo específico, para un paralelo de una carrera.
    
    Reglas de negocio implementadas via validaciones en servicios:
    - Max 3 asignaturas por docente por módulo
    - TC: min 272h, max 380h totales
    - Jornada matutina: 08:00-12:00 (asignaturas de 2h)
    - Jornada nocturna: 18:30-21:30 (asignaturas de 1.5h)
    - Sin choques: mismo docente no puede tener 2 asignaturas al mismo tiempo
    """
    __tablename__ = "horarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    periodo_id = Column(String, ForeignKey("periodos_academicos.id"), nullable=False)
    modulo_id = Column(String, ForeignKey("modulos.id"), nullable=False)
    docente_id = Column(String, ForeignKey("docentes.id"), nullable=False)
    asignatura_id = Column(String, ForeignKey("asignaturas.id"), nullable=False)
    carrera_id = Column(String, ForeignKey("carreras.id"), nullable=False)
    nivel_id = Column(String, ForeignKey("niveles.id"), nullable=False)

    paralelo = Column(String(5), nullable=False)      # "A", "B", "C"...
    dia = Column(Enum(DiaSemana), nullable=False)
    jornada = Column(Enum(Jornada), nullable=False)
    hora_inicio = Column(String(5), nullable=False)   # "08:00", "18:30"
    hora_fin = Column(String(5), nullable=False)      # "10:00", "20:00"

    estado = Column(Enum(EstadoHorario), default=EstadoHorario.BORRADOR)
    generado_por_ia = Column(Boolean, default=False)
    observaciones = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    periodo = relationship("PeriodoAcademico", back_populates="horarios")
    modulo = relationship("Modulo", back_populates="horarios")
    docente = relationship("Docente", back_populates="horarios")
    asignatura = relationship("Asignatura", back_populates="horarios")
    carrera = relationship("Carrera")
    nivel = relationship("Nivel")

    __table_args__ = (
        # Un docente no puede estar en dos lugares a la vez
        UniqueConstraint(
            "modulo_id", "docente_id", "dia", "hora_inicio",
            name="uq_horario_docente_tiempo"
        ),
        # Un paralelo no puede tener dos clases al mismo tiempo
        UniqueConstraint(
            "modulo_id", "carrera_id", "nivel_id", "paralelo", "dia", "hora_inicio",
            name="uq_horario_paralelo_tiempo"
        ),
    )

    def __repr__(self):
        return f"<Horario {self.docente_id} - {self.asignatura_id} - {self.dia} {self.hora_inicio}>"


# ─── CARGA HORARIA (resumen) ──────────────────────────────────────────────────

class CargaHoraria(Base):
    """
    Resumen calculado de horas por docente por módulo y período.
    Se actualiza automáticamente al modificar horarios.
    """
    __tablename__ = "carga_horaria"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    docente_id = Column(String, ForeignKey("docentes.id"), nullable=False)
    periodo_id = Column(String, ForeignKey("periodos_academicos.id"), nullable=False)
    modulo_id = Column(String, ForeignKey("modulos.id"), nullable=False)

    total_asignaturas = Column(Integer, default=0)   # Máx 3
    total_horas = Column(Float, default=0.0)          # Acumulado período: máx 380h TC

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    docente = relationship("Docente")
    periodo = relationship("PeriodoAcademico")
    modulo = relationship("Modulo")

    __table_args__ = (
        UniqueConstraint("docente_id", "periodo_id", "modulo_id", name="uq_carga_docente_modulo"),
    )