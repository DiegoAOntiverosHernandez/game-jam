"""Sistemas: la lógica que procesa los componentes."""
import math

import pygame

from codigo import configuracion as cfg
from codigo.ecs.componentes import (
    ESTADO_COMIENDO,
    ESTADO_DEPOSITANDO,
    ESTADO_HAMBRIENTO,
    ESTADO_INACTIVO,
    ESTADO_MOVIENDOSE,
    ESTADO_RECOLECTANDO,
    ESTADO_YENDO_A_CASA,
    ESTADO_YENDO_A_COMER,
    ESTADO_YENDO_AL_RECURSO,
    ESTADO_MUERTO,
    ComponenteAlmacen,
    ComponenteNecesidades,
    ComponenteNodoRecurso,
    ComponenteReloj,
    ComponenteRenderizado,
    ComponenteRutinaTrabajador,
    ComponenteSeleccionable,
    ComponenteTransformacion,
)

ESTADOS_NECESIDAD = (ESTADO_HAMBRIENTO, ESTADO_YENDO_A_COMER, ESTADO_COMIENDO)
ESTADOS_TRABAJO = (
    ESTADO_YENDO_AL_RECURSO,
    ESTADO_RECOLECTANDO,
    ESTADO_YENDO_A_CASA,
    ESTADO_DEPOSITANDO,
)


def rect_icono_hambre(pos, imagen):
    """Rectángulo del ícono de hambre, encima del PNJ."""
    lado = cfg.TAMANO_ICONO_HAMBRE
    return pygame.Rect(pos.x + imagen.ancho / 2 - lado / 2, pos.y - lado - 4, lado, lado)


class SistemaEntradaYSeleccion:
    """Clic en un PNJ lo selecciona; clic en el mapa, recurso o Casa le da órdenes."""

    def manejar_evento(self, mundo, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
            self._deseleccionar_todos(mundo)
            return
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return
        if evento.pos[0] >= cfg.ANCHO_MAPA:
            return  # clic en el panel de interfaz
        if self._clic_en_icono_hambre(mundo, evento.pos):
            return

        id_clic = self._entidad_en(mundo, evento.pos)
        id_pnj = self._pnj_seleccionado(mundo)

        rutina_clic = (
            mundo.obtener(id_clic, ComponenteRutinaTrabajador)
            if id_clic is not None
            else None
        )
        if rutina_clic is not None:
            if rutina_clic.estado == ESTADO_MUERTO:
                return  # un PNJ muerto no se puede seleccionar
            if id_clic == id_pnj:
                self._deseleccionar_todos(mundo)
            else:
                self._deseleccionar_todos(mundo)
                mundo.obtener(id_clic, ComponenteSeleccionable).seleccionado = True
            return

        if id_pnj is None:
            return
        rutina = mundo.obtener(id_pnj, ComponenteRutinaTrabajador)
        if rutina.estado in ESTADOS_NECESIDAD:
            return

        if id_clic is None:
            rutina.destino = evento.pos
            rutina.estado = ESTADO_MOVIENDOSE
            return

        nodo = mundo.obtener(id_clic, ComponenteNodoRecurso)
        if nodo is not None:
            if rutina.carga > 0 and rutina.tipo_carga != nodo.tipo:
                if rutina.casa is None:
                    return  # no puede mezclar y no sabe dónde dejar la carga
                rutina.objetivo = id_clic
                rutina.destino = None
                rutina.estado = ESTADO_YENDO_A_CASA  # deposita y luego va al nuevo
                return
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

    def _clic_en_icono_hambre(self, mundo, punto):
        for _, (pos, imagen, rutina) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado, ComponenteRutinaTrabajador
        ):
            if rutina.estado == ESTADO_HAMBRIENTO and rect_icono_hambre(
                pos, imagen
            ).collidepoint(punto):
                rutina.estado = ESTADO_YENDO_A_COMER
                return True
        return False


class SistemaRutinaTrabajador:
    """Ciclo del PNJ: ir al recurso → recolectar → ir a la Casa → depositar."""

    def actualizar(self, mundo, dt):
        for id_entidad, (pos, imagen, rutina) in mundo.entidades_con(
            ComponenteTransformacion,
            ComponenteRenderizado,
            ComponenteRutinaTrabajador,
        ):
            necesidades = mundo.obtener(id_entidad, ComponenteNecesidades)
            if rutina.estado == ESTADO_MOVIENDOSE:
                self._mover_a_punto(pos, imagen, rutina, dt)
            elif rutina.estado == ESTADO_YENDO_AL_RECURSO:
                self._ir_al_recurso(mundo, pos, imagen, rutina, dt)
            elif rutina.estado == ESTADO_RECOLECTANDO:
                self._recolectar(mundo, rutina, dt)
            elif rutina.estado == ESTADO_YENDO_A_CASA:
                self._ir_a_casa(mundo, pos, imagen, rutina, dt)
            elif rutina.estado == ESTADO_DEPOSITANDO:
                self._depositar(mundo, rutina, dt)
            elif rutina.estado == ESTADO_YENDO_A_COMER:
                self._ir_a_comer(mundo, pos, imagen, rutina, necesidades, dt)
            elif rutina.estado == ESTADO_COMIENDO:
                self._comer(rutina, necesidades, dt)

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
        if self._mover_hacia(mundo, pos, imagen, rutina.casa, dt):
            rutina.estado = ESTADO_DEPOSITANDO
            rutina.temporizador = 0.0

    def _depositar(self, mundo, rutina, dt):
        almacen = mundo.obtener(rutina.casa, ComponenteAlmacen)
        if almacen is None:
            rutina.estado = ESTADO_INACTIVO
            return

        rutina.temporizador += dt
        while (
            rutina.temporizador >= cfg.SEGUNDOS_POR_UNIDAD_DEPOSITADA
            and rutina.carga > 0
        ):
            rutina.temporizador -= cfg.SEGUNDOS_POR_UNIDAD_DEPOSITADA
            rutina.carga -= 1
            if rutina.tipo_carga == "agua":
                almacen.agua = min(cfg.RESERVA_MAXIMA, almacen.agua + 1)
            else:
                almacen.comida = min(cfg.RESERVA_MAXIMA, almacen.comida + 1)

        if rutina.carga > 0:
            return  # todavía le quedan unidades por dejar

        nodo = self._nodo(mundo, rutina)
        if nodo is not None and nodo.cantidad > 0:
            rutina.tipo_carga = nodo.tipo
            rutina.estado = ESTADO_YENDO_AL_RECURSO  # repite el ciclo
        else:
            rutina.estado = ESTADO_INACTIVO  # el recurso se agotó

    def _ir_a_comer(self, mundo, pos, imagen, rutina, necesidades, dt):
        almacen = mundo.obtener(necesidades.casa, ComponenteAlmacen)
        if almacen is None:
            rutina.estado = ESTADO_INACTIVO
            return
        if not self._mover_hacia(mundo, pos, imagen, necesidades.casa, dt):
            return

        # Al llegar come: el consumo se descuenta de las reservas en este momento
        trabajando = necesidades.estado_previo in ESTADOS_TRABAJO
        consumo = cfg.CONSUMO_TRABAJANDO if trabajando else cfg.CONSUMO_INACTIVO
        almacen.comida = max(0, almacen.comida - consumo["comida"])
        almacen.agua = max(0, almacen.agua - consumo["agua"])

        necesidades.descanso = 0.0
        rutina.estado = ESTADO_COMIENDO

    def _comer(self, rutina, necesidades, dt):
        necesidades.descanso += dt
        if necesidades.descanso < cfg.SEGUNDOS_DESCANSO_COMER:
            return

        necesidades.segundos_ciclo = 0.0
        # Retoma la rutina que tenía; si estaba junto al recurso, vuelve a él
        if necesidades.estado_previo == ESTADO_RECOLECTANDO:
            rutina.estado = ESTADO_YENDO_AL_RECURSO
        elif necesidades.estado_previo == ESTADO_DEPOSITANDO:
            rutina.estado = ESTADO_YENDO_A_CASA
        else:
            rutina.estado = necesidades.estado_previo

class SistemaCicloDia:
    """Reloj global: avanza los días según los segundos de juego."""

    def actualizar(self, mundo, dt):
        for _, (reloj,) in mundo.entidades_con(ComponenteReloj):
            reloj.segundos_dia += dt
            while reloj.segundos_dia >= cfg.SEGUNDOS_POR_DIA:
                reloj.segundos_dia -= cfg.SEGUNDOS_POR_DIA
                reloj.dia += 1


class SistemaNecesidades:
    """Hambre cada ciclo; si nadie atiende el ícono a tiempo, el PNJ muere."""

    def actualizar(self, mundo, dt):
        a_eliminar = []
        for id_entidad, (rutina, necesidades) in mundo.entidades_con(
            ComponenteRutinaTrabajador, ComponenteNecesidades
        ):
            if rutina.estado == ESTADO_MUERTO:
                necesidades.segundos_muerto += dt
                if necesidades.segundos_muerto >= cfg.SEGUNDOS_CUERPO_VISIBLE:
                    a_eliminar.append(id_entidad)
                continue

            if rutina.estado == ESTADO_HAMBRIENTO:
                necesidades.segundos_hambre += dt
                if necesidades.segundos_hambre >= cfg.SEGUNDOS_LIMITE_HAMBRE:
                    self._morir(mundo, id_entidad, rutina)
                continue

            if rutina.estado in ESTADOS_NECESIDAD:
                continue

            necesidades.segundos_ciclo += dt
            if necesidades.segundos_ciclo >= cfg.SEGUNDOS_CICLO_CONSUMO:
                necesidades.segundos_ciclo = 0.0
                necesidades.segundos_hambre = 0.0
                necesidades.estado_previo = rutina.estado
                rutina.estado = ESTADO_HAMBRIENTO

        for id_entidad in a_eliminar:
            mundo.eliminar_entidad(id_entidad)

    def _morir(self, mundo, id_entidad, rutina):
        rutina.estado = ESTADO_MUERTO
        rutina.carga = 0
        sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
        if sel is not None:
            sel.seleccionado = False

class SistemaRenderizado:
    def __init__(self):
        self.fuente = pygame.font.Font(None, 20)

    def dibujar(self, mundo, pantalla):
        # Se dibuja en orden de creación: la Casa queda debajo de los PNJ
        for id_entidad, (pos, imagen) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado
        ):
            rect = pygame.Rect(pos.x, pos.y, imagen.ancho, imagen.alto)
            rutina = mundo.obtener(id_entidad, ComponenteRutinaTrabajador)
            muerto = rutina is not None and rutina.estado == ESTADO_MUERTO
            pygame.draw.rect(pantalla, (70, 70, 70) if muerto else imagen.color, rect)

            sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
            if sel is not None and sel.seleccionado:
                pygame.draw.rect(pantalla, (255, 255, 255), rect, 2)

            # Textos de depuración: cantidad del recurso y carga del PNJ
            nodo = mundo.obtener(id_entidad, ComponenteNodoRecurso)
            if nodo is not None:
                self._texto(pantalla, str(nodo.cantidad), rect.center)

            if rutina is not None:
                if rutina.carga > 0:
                    self._texto(pantalla, str(rutina.carga), (rect.right + 10, rect.top + 8))
                if rutina.estado == ESTADO_HAMBRIENTO:
                    icono = rect_icono_hambre(pos, imagen)
                    pygame.draw.rect(pantalla, (255, 255, 255), icono)
                    pygame.draw.rect(pantalla, (200, 40, 40), icono, 2)

    def _texto(self, pantalla, texto, centro):
        imagen = self.fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(imagen, imagen.get_rect(center=centro))