"""Sistemas: la lógica que procesa los componentes."""
import math

import pygame

from codigo import configuracion as cfg
from codigo.ecs.componentes import (
    ESTADO_INACTIVO,
    ESTADO_MOVIENDOSE,
    ESTADO_RECOLECTANDO,
    ESTADO_YENDO_A_CASA,
    ESTADO_YENDO_AL_RECURSO,
    ComponenteAlmacen,
    ComponenteNodoRecurso,
    ComponenteRenderizado,
    ComponenteRutinaTrabajador,
    ComponenteSeleccionable,
    ComponenteTransformacion,
)


class SistemaEntradaYSeleccion:
    """Clic en un PNJ lo selecciona; clic en el mapa, recurso o Casa le da órdenes."""

    def manejar_evento(self, mundo, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
            self._deseleccionar_todos(mundo)
            return
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return
        if evento.pos[0] >= cfg.ANCHO_MAPA:
            return  # clic en el panel de interfaz (después tendrá botones)

        id_clic = self._entidad_en(mundo, evento.pos)
        id_pnj = self._pnj_seleccionado(mundo)

        if id_clic is not None and mundo.obtener(id_clic, ComponenteRutinaTrabajador) is not None:
            if id_clic == id_pnj:
                self._deseleccionar_todos(mundo)
            else:
                self._deseleccionar_todos(mundo)
                mundo.obtener(id_clic, ComponenteSeleccionable).seleccionado = True
            return

        if id_pnj is None:
            return
        rutina = mundo.obtener(id_pnj, ComponenteRutinaTrabajador)

        if id_clic is None:
            rutina.destino = evento.pos
            rutina.estado = ESTADO_MOVIENDOSE
            return

        nodo = mundo.obtener(id_clic, ComponenteNodoRecurso)
        if nodo is not None:
            if rutina.tipo_carga != nodo.tipo:
                rutina.carga = 0  # no mezcla agua con comida
                rutina.tipo_carga = nodo.tipo
            rutina.objetivo = id_clic
            rutina.destino = None
            rutina.estado = ESTADO_YENDO_AL_RECURSO
        elif mundo.obtener(id_clic, ComponenteAlmacen) is not None:
            rutina.casa = id_clic  # activa el ciclo automático
            rutina.destino = None
            if rutina.estado in (ESTADO_INACTIVO, ESTADO_MOVIENDOSE):
                if rutina.carga > 0:
                    rutina.estado = ESTADO_YENDO_A_CASA
                elif rutina.objetivo is not None:
                    rutina.estado = ESTADO_YENDO_AL_RECURSO
                else:
                    rutina.estado = ESTADO_YENDO_A_CASA

    def _entidad_en(self, mundo, punto):
        """Entidad bajo el clic (la dibujada encima gana)."""
        encontrada = None
        for id_entidad, (pos, imagen) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado
        ):
            rect = pygame.Rect(pos.x, pos.y, imagen.ancho, imagen.alto)
            if rect.collidepoint(punto):
                encontrada = id_entidad
        return encontrada

    def _pnj_seleccionado(self, mundo):
        for id_entidad, (sel,) in mundo.entidades_con(ComponenteSeleccionable):
            if sel.seleccionado:
                return id_entidad
        return None

    def _deseleccionar_todos(self, mundo):
        for _, (sel,) in mundo.entidades_con(ComponenteSeleccionable):
            sel.seleccionado = False


class SistemaRutinaTrabajador:
    """Ciclo del PNJ: ir al recurso → recolectar → ir a la Casa → depositar."""

    def actualizar(self, mundo, dt):
        for _, (pos, imagen, rutina) in mundo.entidades_con(
            ComponenteTransformacion,
            ComponenteRenderizado,
            ComponenteRutinaTrabajador,
        ):
            if rutina.estado == ESTADO_MOVIENDOSE:
                self._mover_a_punto(pos, imagen, rutina, dt)
            elif rutina.estado == ESTADO_YENDO_AL_RECURSO:
                self._ir_al_recurso(mundo, pos, imagen, rutina, dt)
            elif rutina.estado == ESTADO_RECOLECTANDO:
                self._recolectar(mundo, rutina, dt)
            elif rutina.estado == ESTADO_YENDO_A_CASA:
                self._ir_a_casa(mundo, pos, imagen, rutina, dt)

    def _mover_a_punto(self, pos, imagen, rutina, dt):
        """Camina hacia cualquier coordenada libre (x, y) donde el usuario hizo clic."""
        if rutina.destino is None:
            rutina.estado = ESTADO_INACTIVO
            return

        dest_x, dest_y = rutina.destino
        # Mantener dentro de los límites del mapa
        mitad_ancho = imagen.ancho / 2
        mitad_alto = imagen.alto / 2
        dest_x = max(mitad_ancho, min(cfg.ANCHO_MAPA - mitad_ancho, dest_x))
        dest_y = max(mitad_alto, min(cfg.ALTO_MAPA - mitad_alto, dest_y))

        dx = dest_x - (pos.x + mitad_ancho)
        dy = dest_y - (pos.y + mitad_alto)
        distancia = math.hypot(dx, dy)
        paso = pos.velocidad * dt

        if distancia <= paso or distancia <= 1.0:
            pos.x = dest_x - mitad_ancho
            pos.y = dest_y - mitad_alto
            rutina.destino = None
            rutina.estado = ESTADO_INACTIVO
            return

        pos.x += dx / distancia * paso
        pos.y += dy / distancia * paso

    def _nodo(self, mundo, rutina):
        if rutina.objetivo is None:
            return None
        return mundo.obtener(rutina.objetivo, ComponenteNodoRecurso)

    def _mover_hacia(self, mundo, pos, imagen, id_destino, dt):
        """Camina en línea recta hacia el destino. Devuelve True al llegar."""
        destino_pos = mundo.obtener(id_destino, ComponenteTransformacion)
        destino_img = mundo.obtener(id_destino, ComponenteRenderizado)
        dx = (destino_pos.x + destino_img.ancho / 2) - (pos.x + imagen.ancho / 2)
        dy = (destino_pos.y + destino_img.alto / 2) - (pos.y + imagen.alto / 2)
        distancia = math.hypot(dx, dy)

        if distancia <= (destino_img.ancho + imagen.ancho) / 2 + 2:
            return True

        paso = pos.velocidad * dt
        pos.x += dx / distancia * paso
        pos.y += dy / distancia * paso
        return False

    def _ir_al_recurso(self, mundo, pos, imagen, rutina, dt):
        nodo = self._nodo(mundo, rutina)
        if nodo is None or nodo.cantidad <= 0:
            self._terminar_recoleccion(rutina)
            return
        if self._mover_hacia(mundo, pos, imagen, rutina.objetivo, dt):
            rutina.estado = ESTADO_RECOLECTANDO
            rutina.temporizador = 0.0

    def _recolectar(self, mundo, rutina, dt):
        nodo = self._nodo(mundo, rutina)
        if nodo is None:
            self._terminar_recoleccion(rutina)
            return

        rutina.temporizador += dt
        while (
            rutina.temporizador >= cfg.SEGUNDOS_POR_UNIDAD_EXTRAIDA
            and rutina.carga < cfg.CARGA_POR_VIAJE
            and nodo.cantidad > 0
        ):
            rutina.temporizador -= cfg.SEGUNDOS_POR_UNIDAD_EXTRAIDA
            nodo.cantidad -= 1
            rutina.carga += 1

        if rutina.carga >= cfg.CARGA_POR_VIAJE or nodo.cantidad <= 0:
            self._terminar_recoleccion(rutina)

    def _terminar_recoleccion(self, rutina):
        """Con la Casa asignada va a depositar; si no, espera con su carga."""
        if rutina.carga > 0 and rutina.casa is not None:
            rutina.estado = ESTADO_YENDO_A_CASA
        else:
            rutina.estado = ESTADO_INACTIVO

    def _ir_a_casa(self, mundo, pos, imagen, rutina, dt):
        almacen = mundo.obtener(rutina.casa, ComponenteAlmacen)
        if almacen is None:
            rutina.estado = ESTADO_INACTIVO
            return
        if not self._mover_hacia(mundo, pos, imagen, rutina.casa, dt):
            return

        if rutina.tipo_carga == "agua":
            almacen.agua = min(cfg.RESERVA_MAXIMA, almacen.agua + rutina.carga)
        else:
            almacen.comida = min(cfg.RESERVA_MAXIMA, almacen.comida + rutina.carga)
        rutina.carga = 0

        nodo = self._nodo(mundo, rutina)
        if nodo is not None and nodo.cantidad > 0:
            rutina.estado = ESTADO_YENDO_AL_RECURSO  # repite el ciclo
        else:
            rutina.estado = ESTADO_INACTIVO  # el recurso se agotó


class SistemaRenderizado:
    def __init__(self):
        self.fuente = pygame.font.Font(None, 20)

    def dibujar(self, mundo, pantalla):
        # Se dibuja en orden de creación: la Casa queda debajo de los PNJ
        for id_entidad, (pos, imagen) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado
        ):
            rect = pygame.Rect(pos.x, pos.y, imagen.ancho, imagen.alto)
            pygame.draw.rect(pantalla, imagen.color, rect)

            sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
            if sel is not None and sel.seleccionado:
                pygame.draw.rect(pantalla, (255, 255, 255), rect, 2)

            # Textos de depuración: cantidad del recurso y carga del PNJ
            nodo = mundo.obtener(id_entidad, ComponenteNodoRecurso)
            if nodo is not None:
                self._texto(pantalla, str(nodo.cantidad), rect.center)
            rutina = mundo.obtener(id_entidad, ComponenteRutinaTrabajador)
            if rutina is not None and rutina.carga > 0:
                self._texto(pantalla, str(rutina.carga), (rect.centerx, rect.top - 8))

    def _texto(self, pantalla, texto, centro):
        imagen = self.fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(imagen, imagen.get_rect(center=centro))