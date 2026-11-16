"""Componentes de datos (solo guardan información, sin lógica)."""
from dataclasses import dataclass
from typing import Optional

# Estados de la rutina del PNJ
ESTADO_INACTIVO = "inactivo"
ESTADO_MOVIENDOSE = "moviendose"
ESTADO_YENDO_AL_RECURSO = "yendo_al_recurso"
ESTADO_RECOLECTANDO = "recolectando"
ESTADO_YENDO_A_CASA = "yendo_a_casa"
ESTADO_DEPOSITANDO = "depositando"
ESTADO_HAMBRIENTO = "hambriento"       # parado, con el ícono, esperando el clic
ESTADO_YENDO_A_COMER = "yendo_a_comer"
ESTADO_COMIENDO = "comiendo"
ESTADO_MUERTO = "muerto"
ESTADO_CAZANDO = "cazando"

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
    sprite: Optional[str] = None


@dataclass
class ComponenteAlmacen:
    agua: int = 0
    comida: int = 0
    segundos_sin_agua: float = 0.0
    segundos_sin_recursos: float = 0.0


@dataclass
class ComponenteObstaculo:
    """Entidad sólida que los PNJ no pueden atravesar (piedra.png)."""
    bloquea: bool = True


@dataclass
class ComponenteSeleccionable:
    seleccionado: bool = False


@dataclass
class ComponenteNodoRecurso:
    tipo: str         # "agua" o "comida"
    cantidad: int
    maximo: int
    segundos_regeneracion: float = 0.0   # avance hacia la próxima unidad
    agotado: bool = False                # se vació a 0 y está en recuperación
    segundos_recuperacion: float = 0.0   # avance de la recuperación larga


@dataclass
class ComponenteRutinaTrabajador:
    estado: str = ESTADO_INACTIVO
    objetivo: Optional[int] = None     # id del recurso asignado
    casa: Optional[int] = None         # id de la Casa de Campaña (activa el ciclo)
    destino: Optional[tuple] = None    # (x, y) libre en el mapa al hacer clic
    carga: int = 0                     # unidades que lleva encima
    tipo_carga: Optional[str] = None   # "agua" o "comida"
    temporizador: float = 0.0          # avance de la extracción
    genero: str = "h"                  # "h" (hombre) o "m" (mujer)
    mirando_izquierda: bool = False    # dirección horizontal del sprite
    tiempo_animacion: float = 0.0      # reloj para alternar cuadros al caminar
    segundos_inactivo: float = 0.0     # tiempo quieto sin selección para sentarse
    viendo_animal: bool = False        # evita repetir el audio de ver animal en cada fotograma


@dataclass
class ComponenteAnimal:
    vivo: bool = True
    golpes: int = 0                      # golpes recibidos
    segundos_huida: float = 0.0          # tiempo que le queda corriendo
    direccion: tuple = (0.0, 0.0)        # (0, 0) = parado
    segundos_paseo: float = 0.0          # tiempo hasta cambiar de rumbo
    mirando_izquierda: bool = False

@dataclass
class ComponenteReloj:
    dia: int = 1
    segundos_dia: float = 0.0   # segundos de juego dentro del día actual
    velocidad: float = 1        # x1, x2 o x5

@dataclass
class ComponenteNecesidades:
    segundos_ciclo: float = 0.0                # avance hacia el próximo hambre
    estado_previo: str = ESTADO_INACTIVO       # qué hacía al sentir hambre
    casa: Optional[int] = None                 # id de la Casa donde come
    descanso: float = 0.0                      # avance del descanso al comer
    segundos_hambre: float = 0.0               # tiempo con el ícono sin atender
    segundos_muerto: float = 0.0               # tiempo desde que murió