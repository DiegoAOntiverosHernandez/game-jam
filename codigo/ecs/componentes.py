"""Componentes de datos (solo guardan información, sin lógica)."""
from dataclasses import dataclass
from typing import Optional

# Estados de la rutina del PNJ
ESTADO_INACTIVO = "inactivo"
ESTADO_MOVIENDOSE = "moviendose"
ESTADO_YENDO_AL_RECURSO = "yendo_al_recurso"
ESTADO_RECOLECTANDO = "recolectando"
ESTADO_YENDO_A_CASA = "yendo_a_casa"


@dataclass
class ComponenteTransformacion:
    x: float          # posición en píxeles (esquina superior izquierda)
    y: float
    velocidad: float = 0.0


@dataclass
class ComponenteRenderizado:
    ancho: int
    alto: int
    color: tuple      # imagen provisional hasta tener el sprite


@dataclass
class ComponenteAlmacen:
    agua: int = 0
    comida: int = 0


@dataclass
class ComponenteSeleccionable:
    seleccionado: bool = False


@dataclass
class ComponenteNodoRecurso:
    tipo: str         # "agua" o "comida"
    cantidad: int
    maximo: int


@dataclass
class ComponenteRutinaTrabajador:
    estado: str = ESTADO_INACTIVO
    objetivo: Optional[int] = None     # id del recurso asignado
    casa: Optional[int] = None         # id de la Casa de Campaña (activa el ciclo)
    destino: Optional[tuple] = None    # (x, y) libre en el mapa al hacer clic
    carga: int = 0                     # unidades que lleva encima
    tipo_carga: Optional[str] = None   # "agua" o "comida"
    temporizador: float = 0.0          # avance de la extracción
