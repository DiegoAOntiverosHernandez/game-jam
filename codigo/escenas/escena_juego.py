"""Escena principal del juego."""
import pygame

from codigo import configuracion as cfg
from codigo.ecs.componentes import (
    ComponenteAlmacen,
    ComponenteNodoRecurso,
    ComponenteRenderizado,
    ComponenteRutinaTrabajador,
    ComponenteSeleccionable,
    ComponenteTransformacion,
)
from codigo.ecs.mundo import Mundo
from codigo.ecs.sistemas import (
    SistemaEntradaYSeleccion,
    SistemaRenderizado,
    SistemaRutinaTrabajador,
)

# Colores provisionales (después se moverán a configuracion.py)
COLOR_PANEL = (40, 36, 32)
COLOR_SUELO = (194, 170, 120)
COLOR_LINEA = (180, 156, 108)
COLOR_CAMPAMENTO = (120, 80, 50)
COLOR_COCHIMI = (200, 60, 60)
COLOR_AGUAJE = (60, 120, 200)
COLOR_CARDON = (60, 140, 70)


class EscenaJuego:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.mundo = Mundo()
        self.sistema_entrada = SistemaEntradaYSeleccion()
        self.sistema_renderizado = SistemaRenderizado()
        self.fuente = pygame.font.Font(None, 26)   # <- línea nueva
        self.mundo.agregar_sistema(SistemaRutinaTrabajador())

        self._crear_campamento()
        self._crear_aguaje(4, 4)
        self._crear_cardon(18, 5)
        for columna, fila in ((10, 10), (13, 10)):  # los 2 PNJ iniciales
            self._crear_cochimi(columna, fila)

    def _crear_campamento(self):
        t = cfg.TAMANO_CASILLA
        self.mundo.crear_entidad(
            ComponenteTransformacion(11 * t, 8 * t),
            ComponenteRenderizado(*cfg.TAMANO_CASA_CAMPANA, COLOR_CAMPAMENTO),
            ComponenteAlmacen(cfg.RESERVA_INICIAL_AGUA, cfg.RESERVA_INICIAL_COMIDA),
        )

    def _crear_aguaje(self, columna, fila):
        t = cfg.TAMANO_CASILLA
        self.mundo.crear_entidad(
            ComponenteTransformacion(columna * t, fila * t),
            ComponenteRenderizado(t, t, COLOR_AGUAJE),
            ComponenteNodoRecurso("agua", cfg.AGUAJE_MAXIMO, cfg.AGUAJE_MAXIMO),
        )

    def _crear_cardon(self, columna, fila):
        t = cfg.TAMANO_CASILLA
        self.mundo.crear_entidad(
            ComponenteTransformacion(columna * t, fila * t),
            ComponenteRenderizado(t, t, COLOR_CARDON),
            ComponenteNodoRecurso("comida", cfg.CARDON_MAXIMO, cfg.CARDON_MAXIMO),
        )

    def _crear_cochimi(self, columna, fila):
        t = cfg.TAMANO_CASILLA
        self.mundo.crear_entidad(
            ComponenteTransformacion(columna * t, fila * t, cfg.PNJ_VELOCIDAD),
            ComponenteRenderizado(*cfg.TAMANO_SPRITE_PNJ, COLOR_COCHIMI),
            ComponenteSeleccionable(),
            ComponenteRutinaTrabajador(),
        )

    def manejar_evento(self, evento):
        self.sistema_entrada.manejar_evento(self.mundo, evento)

    def actualizar(self, dt):
        self.mundo.actualizar(dt)

    def dibujar(self):
        self.pantalla.fill(COLOR_PANEL)

        mapa = pygame.Rect(0, 0, cfg.ANCHO_MAPA, cfg.ALTO_MAPA)
        pygame.draw.rect(self.pantalla, COLOR_SUELO, mapa)
        for columna in range(cfg.COLUMNAS_MAPA + 1):
            x = columna * cfg.TAMANO_CASILLA
            pygame.draw.line(self.pantalla, COLOR_LINEA, (x, 0), (x, cfg.ALTO_MAPA))
        for fila in range(cfg.FILAS_MAPA + 1):
            y = fila * cfg.TAMANO_CASILLA
            pygame.draw.line(self.pantalla, COLOR_LINEA, (0, y), (cfg.ANCHO_MAPA, y))

        self.sistema_renderizado.dibujar(self.mundo, self.pantalla)
        self._dibujar_panel()

    def _dibujar_panel(self):
        for _, (almacen,) in self.mundo.entidades_con(ComponenteAlmacen):
            x = cfg.ANCHO_MAPA + 16
            agua = self.fuente.render(f"Agua: {almacen.agua}", True, (255, 255, 255))
            comida = self.fuente.render(f"Comida: {almacen.comida}", True, (255, 255, 255))
            self.pantalla.blit(agua, (x, 24))
            self.pantalla.blit(comida, (x, 56))
