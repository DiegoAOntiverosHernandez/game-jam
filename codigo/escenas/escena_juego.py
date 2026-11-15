"""Escena principal del juego."""
import pygame
import random

from codigo import configuracion as cfg
from codigo.ecs.componentes import (
    ComponenteAlmacen,
    ComponenteNodoRecurso,
    ComponenteRenderizado,
    ComponenteRutinaTrabajador,
    ComponenteSeleccionable,
    ComponenteTransformacion,
    ComponenteReloj,
    ComponenteNecesidades,
    ESTADO_HAMBRIENTO,
    ESTADO_MUERTO,
)
from codigo.ecs.mundo import Mundo
from codigo.ecs.sistemas import (
    SistemaEntradaYSeleccion,
    SistemaRenderizado,
    SistemaRutinaTrabajador,
    SistemaCicloDia,
    SistemaNecesidades,
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

        self.mundo.agregar_sistema(SistemaNecesidades())

        self.reloj = ComponenteReloj(
            segundos_dia=cfg.HORA_INICIAL / cfg.HORAS_POR_DIA * cfg.SEGUNDOS_POR_DIA
        )
        self.filtro_noche = pygame.Surface((cfg.ANCHO_MAPA, cfg.ALTO_MAPA))
        self.filtro_noche.fill(cfg.COLOR_NOCHE)

        self.mundo.crear_entidad(self.reloj)
        self.mundo.agregar_sistema(SistemaCicloDia())
        self.botones_velocidad = self._crear_botones_velocidad()
        self.boton_pnj = pygame.Rect(cfg.ANCHO_MAPA + 16, 192, 160, 36)

        self._crear_campamento()
        self._crear_aguaje(4, 4)
        self._crear_cardon(18, 5)
        for columna, fila in ((10, 10), (13, 10)):  # los 2 PNJ iniciales
            self._crear_cochimi(columna * cfg.TAMANO_CASILLA, fila * cfg.TAMANO_CASILLA)

    def _crear_campamento(self):
        t = cfg.TAMANO_CASILLA
        self.id_campamento = self.mundo.crear_entidad(
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

    def _crear_cochimi(self, x, y):
        self.mundo.crear_entidad(
            ComponenteTransformacion(x, y, cfg.PNJ_VELOCIDAD),
            ComponenteRenderizado(*cfg.TAMANO_SPRITE_PNJ, COLOR_COCHIMI),
            ComponenteSeleccionable(),
            ComponenteRutinaTrabajador(),
            ComponenteNecesidades(
                casa=self.id_campamento,
                segundos_ciclo=random.uniform(0, cfg.SEGUNDOS_CICLO_CONSUMO),
            ),
        )

    def _hay_hambre(self):
        return any(
            rutina.estado == ESTADO_HAMBRIENTO
            for _, (rutina,) in self.mundo.entidades_con(ComponenteRutinaTrabajador)
        )

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.boton_pnj.collidepoint(evento.pos):
                self._crear_pnj_nuevo()
                return
            for velocidad, rect in self.botones_velocidad.items():
                if rect.collidepoint(evento.pos):
                    if not self._hay_hambre():  # con hambre pendiente no se acelera
                        self.reloj.velocidad = velocidad
                    return
        self.sistema_entrada.manejar_evento(self.mundo, evento)

    def actualizar(self, dt):
        if self._hay_hambre():
            self.reloj.velocidad = 1  # baja a x1 para que alcance a reaccionar
        self.mundo.actualizar(dt * self.reloj.velocidad)

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

        # Filtro de noche: se dibuja sobre el mapa y debajo del panel
        alpha = int(self._oscuridad() * cfg.NOCHE_ALPHA_MAXIMA)
        if alpha > 0:
            self.filtro_noche.set_alpha(alpha)
            self.pantalla.blit(self.filtro_noche, (0, 0))

        self._dibujar_panel()

    def _dibujar_panel(self):
        x = cfg.ANCHO_MAPA + 16
        for _, (almacen,) in self.mundo.entidades_con(ComponenteAlmacen):
            agua = self.fuente.render(f"Agua: {almacen.agua}", True, (255, 255, 255))
            comida = self.fuente.render(f"Comida: {almacen.comida}", True, (255, 255, 255))
            self.pantalla.blit(agua, (x, 24))
            self.pantalla.blit(comida, (x, 56))

        dia = self.fuente.render(
            f"Día: {self.reloj.dia} / {cfg.DIAS_TOTALES}", True, (255, 255, 255)
        )
        self.pantalla.blit(dia, (x, 88))

        minutos = int(
            self.reloj.segundos_dia / cfg.SEGUNDOS_POR_DIA * cfg.HORAS_POR_DIA * 60
        )
        hora = self.fuente.render(
            f"Hora: {minutos // 60:02d}:{minutos % 60:02d}", True, (255, 255, 255)
        )
        self.pantalla.blit(hora, (x, 112))

        bloqueado = self._hay_hambre()
        for velocidad, rect in self.botones_velocidad.items():
            activo = velocidad == self.reloj.velocidad
            fondo = (90, 130, 90) if activo else (70, 64, 58)
            if bloqueado:
                fondo = (50, 46, 42)
            pygame.draw.rect(self.pantalla, fondo, rect)
            pygame.draw.rect(self.pantalla, (255, 255, 255), rect, 2 if activo else 1)
            texto = self.fuente.render(f"x{velocidad}", True, (255, 255, 255))
            self.pantalla.blit(texto, texto.get_rect(center=rect.center))   
        self._dibujar_boton_pnj()

    def _crear_botones_velocidad(self):
        ancho, alto, separacion = 52, 32, 10
        x0 = cfg.ANCHO_MAPA + 8
        return {
            velocidad: pygame.Rect(x0 + i * (ancho + separacion), 144, ancho, alto)
            for i, velocidad in enumerate(cfg.VELOCIDADES)
        }

    def _oscuridad(self):
        """0 = pleno día, 1 = noche cerrada, con transiciones suaves."""
        hora = self.reloj.segundos_dia / cfg.SEGUNDOS_POR_DIA * cfg.HORAS_POR_DIA

        def suavizar(t):
            t = max(0.0, min(1.0, t))
            return t * t * (3 - 2 * t)  # curva suave: sin cortes al inicio ni al final

        if hora < cfg.HORA_AMANECER_INICIO:
            return 1.0
        if hora < cfg.HORA_DIA_PLENO:
            duracion = cfg.HORA_DIA_PLENO - cfg.HORA_AMANECER_INICIO
            return 1.0 - suavizar((hora - cfg.HORA_AMANECER_INICIO) / duracion)
        if hora < cfg.HORA_ATARDECER_INICIO:
            return 0.0
        if hora < cfg.HORA_NOCHE_PLENA:
            duracion = cfg.HORA_NOCHE_PLENA - cfg.HORA_ATARDECER_INICIO
            return suavizar((hora - cfg.HORA_ATARDECER_INICIO) / duracion)
        return 1.0

    def _pnj_vivos(self):
        return sum(
            1
            for _, (rutina,) in self.mundo.entidades_con(ComponenteRutinaTrabajador)
            if rutina.estado != ESTADO_MUERTO
        )

    def _costo_pnj(self):
        adicionales = max(0, self._pnj_vivos() - cfg.PNJ_INICIALES)
        return cfg.COSTO_PNJ_PRIMERO + cfg.COSTO_PNJ_INCREMENTO * adicionales

    def _puede_crear_pnj(self):
        almacen = self.mundo.obtener(self.id_campamento, ComponenteAlmacen)
        return (
            self._pnj_vivos() < cfg.PNJ_MAXIMOS
            and almacen.comida >= self._costo_pnj()
        )

    def _crear_pnj_nuevo(self):
        if not self._puede_crear_pnj():
            return
        almacen = self.mundo.obtener(self.id_campamento, ComponenteAlmacen)
        almacen.comida -= self._costo_pnj()
        casa = self.mundo.obtener(self.id_campamento, ComponenteTransformacion)
        ancho_casa, alto_casa = cfg.TAMANO_CASA_CAMPANA
        x = casa.x + (ancho_casa - cfg.TAMANO_SPRITE_PNJ[0]) / 2 + random.uniform(-20, 20)
        y = casa.y + alto_casa + 4   # aparece justo debajo de la Casa
        self._crear_cochimi(x, y)

    def _dibujar_boton_pnj(self):
        vivos = self._pnj_vivos()
        fondo = (90, 130, 90) if self._puede_crear_pnj() else (50, 46, 42)
        pygame.draw.rect(self.pantalla, fondo, self.boton_pnj)
        pygame.draw.rect(self.pantalla, (255, 255, 255), self.boton_pnj, 1)
        texto = self.fuente.render("Nuevo PNJ", True, (255, 255, 255))
        self.pantalla.blit(texto, texto.get_rect(center=self.boton_pnj.center))

        if vivos >= cfg.PNJ_MAXIMOS:
            detalle = "Máximo alcanzado"
        else:
            detalle = f"Cuesta {self._costo_pnj()} comida"
        x = self.boton_pnj.x
        self.pantalla.blit(self.fuente.render(detalle, True, (255, 255, 255)), (x, 236))
        conteo = f"PNJ: {vivos}/{cfg.PNJ_MAXIMOS}"
        self.pantalla.blit(self.fuente.render(conteo, True, (255, 255, 255)), (x, 262))