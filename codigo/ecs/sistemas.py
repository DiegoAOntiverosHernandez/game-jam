"""Sistemas: la lógica que procesa los componentes."""
import math

import pygame

from codigo import configuracion as cfg
from codigo.gestor_recursos import (
    VOLUMENES,
    actualizar_volumenes,
    cargar_imagen,
    reproducir_sonido,
)
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
    ComponenteAnimal,
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


def _reproducir_voz_pnj(rutina, accion):
    es_mujer = rutina.genero == "m"
    carpeta = "voces de mujer" if es_mujer else "voces de hombre"
    sufijo = "mujer" if es_mujer else "hombre"

    if accion == "hola":
        reproducir_sonido(f"{carpeta}/hola_{sufijo}.mp3", canal_voz=True)
    elif accion == "adelante":
        reproducir_sonido(f"{carpeta}/adelante_{sufijo}.mp3", canal_voz=True)
    elif accion == "agua":
        reproducir_sonido(f"{carpeta}/agua_{sufijo}.mp3", canal_voz=True)
    elif accion == "comida":
        reproducir_sonido(f"{carpeta}/Pitahaya_dulce_{sufijo}.mp3", canal_voz=True)
    elif accion == "animal" and not es_mujer:
        reproducir_sonido("voces de hombre/somus_mover1.wav", canal_voz=True)
    elif accion == "muerte":
        archivo = "Female_Death.mp3" if es_mujer else "dark_souls_moan.mp3"
        reproducir_sonido(f"{carpeta}/{archivo}", canal_voz=False, categoria="voces")


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
                rutina_clic.segundos_inactivo = 0.0
                rutina_clic.tiempo_animacion = 0.0
                _reproducir_voz_pnj(rutina_clic, "hola")
            return

        if id_pnj is None:
            return
        rutina = mundo.obtener(id_pnj, ComponenteRutinaTrabajador)
        if rutina.estado in ESTADOS_NECESIDAD:
            return

        if id_clic is None:
            rutina.destino = evento.pos
            rutina.estado = ESTADO_MOVIENDOSE
            _reproducir_voz_pnj(rutina, "adelante")
            return

        if mundo.obtener(id_clic, ComponenteAnimal) is not None:
            rutina.destino = evento.pos
            rutina.estado = ESTADO_MOVIENDOSE
            if rutina.genero == "h":
                _reproducir_voz_pnj(rutina, "animal")
            else:
                _reproducir_voz_pnj(rutina, "adelante")
            return

        nodo = mundo.obtener(id_clic, ComponenteNodoRecurso)
        if nodo is not None:
            _reproducir_voz_pnj(rutina, "agua" if nodo.tipo == "agua" else "comida")
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
            _reproducir_voz_pnj(rutina, "adelante")
            if rutina.estado in (ESTADO_INACTIVO, ESTADO_MOVIENDOSE):
                if rutina.carga > 0:
                    rutina.estado = ESTADO_YENDO_A_CASA
                elif rutina.objetivo is not None:
                    rutina.estado = ESTADO_YENDO_AL_RECURSO
                else:
                    rutina.estado = ESTADO_YENDO_A_CASA
        else:
            rutina.destino = evento.pos
            rutina.estado = ESTADO_MOVIENDOSE
            _reproducir_voz_pnj(rutina, "adelante")

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

    def __init__(self):
        self._turno_comer = 0

    def actualizar(self, mundo, dt):
        for id_entidad, (pos, imagen, rutina) in mundo.entidades_con(
            ComponenteTransformacion,
            ComponenteRenderizado,
            ComponenteRutinaTrabajador,
        ):
            sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
            seleccionado = sel is not None and sel.seleccionado
            if rutina.estado == ESTADO_INACTIVO and not seleccionado:
                rutina.segundos_inactivo += dt
            else:
                rutina.segundos_inactivo = 0.0
                if rutina.estado == ESTADO_INACTIVO and seleccionado:
                    rutina.tiempo_animacion += dt

            necesidades = mundo.obtener(id_entidad, ComponenteNecesidades)
            if rutina.estado != ESTADO_MUERTO and rutina.genero == "h":
                self._verificar_vista_animal(mundo, pos, imagen, rutina)
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

    def _verificar_vista_animal(self, mundo, pos, imagen, rutina):
        """Si un PNJ hombre se acerca a ver un animal, dice somus_mover1.wav."""
        rango_vista = cfg.TAMANO_CASILLA * 3.5
        cx = pos.x + imagen.ancho / 2
        cy = pos.y + imagen.alto / 2
        cerca = False
        for _, (pos_a, img_a, _) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado, ComponenteAnimal
        ):
            ax = pos_a.x + img_a.ancho / 2
            ay = pos_a.y + img_a.alto / 2
            if math.hypot(ax - cx, ay - cy) <= rango_vista:
                cerca = True
                break
        if cerca and not rutina.viendo_animal:
            rutina.viendo_animal = True
            _reproducir_voz_pnj(rutina, "animal")
        elif not cerca:
            rutina.viendo_animal = False

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
        if abs(dx) > 0.5:
            rutina.mirando_izquierda = dx < 0
        rutina.tiempo_animacion += dt
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

    def _mover_hacia(self, mundo, pos, imagen, id_destino, dt, rutina=None):
        """Camina en línea recta hacia el destino. Devuelve True al llegar."""
        destino_pos = mundo.obtener(id_destino, ComponenteTransformacion)
        destino_img = mundo.obtener(id_destino, ComponenteRenderizado)
        dx = (destino_pos.x + destino_img.ancho / 2) - (pos.x + imagen.ancho / 2)
        dy = (destino_pos.y + destino_img.alto / 2) - (pos.y + imagen.alto / 2)
        if rutina is not None:
            if abs(dx) > 0.5:
                rutina.mirando_izquierda = dx < 0
            rutina.tiempo_animacion += dt
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
        if self._mover_hacia(mundo, pos, imagen, rutina.objetivo, dt, rutina):
            rutina.estado = ESTADO_RECOLECTANDO
            rutina.temporizador = 0.0
            if nodo.tipo == "agua":
                reproducir_sonido("sonidos ambientales/recojer_agua.wav")

    def _recolectar(self, mundo, rutina, dt):
        nodo = self._nodo(mundo, rutina)
        if nodo is None:
            self._terminar_recoleccion(rutina)
            return

        carga_maxima = (
            cfg.CARGA_POR_VIAJE_COMIDA
            if nodo.tipo == "comida"
            else cfg.CARGA_POR_VIAJE
        )
        rutina.temporizador += dt
        while (
            rutina.temporizador >= cfg.SEGUNDOS_POR_UNIDAD_EXTRAIDA
            and rutina.carga < carga_maxima
            and nodo.cantidad > 0
        ):
            rutina.temporizador -= cfg.SEGUNDOS_POR_UNIDAD_EXTRAIDA
            nodo.cantidad -= 1
            rutina.carga += 1
            if nodo.tipo == "comida" and rutina.carga <= cfg.CARGA_POR_VIAJE_COMIDA:
                reproducir_sonido("sonidos ambientales/recojer_fruta.mp3")

        if rutina.carga >= carga_maxima or nodo.cantidad <= 0:
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
        if self._mover_hacia(mundo, pos, imagen, rutina.casa, dt, rutina):
            if rutina.carga > 0:
                reproducir_sonido("sonidos ambientales/tributo.wav")
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
        if not self._mover_hacia(mundo, pos, imagen, necesidades.casa, dt, rutina):
            return

        # Al llegar come: el consumo se descuenta de las reservas en este momento
        trabajando = necesidades.estado_previo in ESTADOS_TRABAJO
        consumo = cfg.CONSUMO_TRABAJANDO if trabajando else cfg.CONSUMO_INACTIVO
        almacen.comida = max(0, almacen.comida - consumo["comida"])
        almacen.agua = max(0, almacen.agua - consumo["agua"])

        archivo_comer = "comer1.mp3" if self._turno_comer % 2 == 0 else "comer2.mp3"
        self._turno_comer += 1
        reproducir_sonido(f"sonidos ambientales/{archivo_comer}")

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
        _reproducir_voz_pnj(rutina, "muerte")
        sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
        if sel is not None:
            sel.seleccionado = False

class SistemaRenderizado:
    def __init__(self):
        self.fuente = pygame.font.Font(None, 20)

    def _sprite_pnj(self, rutina, seleccionado):
        es_mujer = rutina.genero == "m"
        carpeta = "Npcs/Cochimie mujer" if es_mujer else "Npcs/Cochimie hombre"
        prefijo_min = "cochimie_m" if es_mujer else "cochimie_h"
        prefijo_may = "Cochimie_m" if es_mujer else "Cochimie_h"
        estado = rutina.estado

        if estado == ESTADO_MUERTO:
            sufijo = "muerta" if es_mujer else "muerto"
            return f"{carpeta}/{prefijo_min}_{sufijo}.png"
        if estado == ESTADO_COMIENDO:
            sufijo = "sentada" if es_mujer else "sentando"
            return f"{carpeta}/{prefijo_min}_{sufijo}.png"
        if estado == ESTADO_HAMBRIENTO:
            p = prefijo_min if es_mujer else prefijo_may
            return f"{carpeta}/{p}_saludando.png"
        if estado == ESTADO_INACTIVO and seleccionado:
            # Sube y baja la mano alternando entre saludando y frente
            if int(rutina.tiempo_animacion / 0.35) % 2 == 0:
                p = prefijo_min if es_mujer else prefijo_may
                return f"{carpeta}/{p}_saludando.png"
            frente = "cochimie_M_frente.png" if es_mujer else "cochimie_h_frente.png"
            return f"{carpeta}/{frente}"
        if estado in (ESTADO_RECOLECTANDO, ESTADO_DEPOSITANDO):
            lado = "lado_izquierdo" if rutina.mirando_izquierda else "lado_derecho"
            return f"{carpeta}/{prefijo_min}_{lado}.png"
        if estado in (
            ESTADO_MOVIENDOSE,
            ESTADO_YENDO_AL_RECURSO,
            ESTADO_YENDO_A_CASA,
            ESTADO_YENDO_A_COMER,
        ):
            sufijo_dir = "_izquierda" if rutina.mirando_izquierda else ""
            if es_mujer:
                lado = "lado_izquierdo" if rutina.mirando_izquierda else "lado_derecho"
                secuencia = (
                    f"{carpeta}/cochimie_m_{lado}.png",
                    f"{carpeta}/Cochimie_m_caminando2{sufijo_dir}.png",
                    f"{carpeta}/Cochimie_m_caminando1{sufijo_dir}.png",
                )
                return secuencia[int(rutina.tiempo_animacion / 0.15) % 3]
            cuadro = 1 + (int(rutina.tiempo_animacion / 0.2) % 2)
            return f"{carpeta}/{prefijo_may}_caminando{cuadro}{sufijo_dir}.png"

        # Inactivo: si lleva 8 s sin hacer nada y no está seleccionado, se sienta
        if (
            estado == ESTADO_INACTIVO
            and not seleccionado
            and rutina.segundos_inactivo >= cfg.SEGUNDOS_INACTIVO_PARA_SENTARSE
        ):
            sufijo = "sentada" if es_mujer else "sentando"
            return f"{carpeta}/{prefijo_min}_{sufijo}.png"

        # Inactivo (mirando de frente)
        frente = "cochimie_M_frente.png" if es_mujer else "cochimie_h_frente.png"
        return f"{carpeta}/{frente}"

    def _sprite_cardon(self, cantidad):
        carpeta = "Vegetacion/Planta de recolecion"
        if cantidad >= cfg.CARDON_UMBRAL_LLENO:
            return f"{carpeta}/Arbol_de_pitaya_lleno_de_7_a_10.png"
        if cantidad >= cfg.CARDON_UMBRAL_MEDIO:
            return f"{carpeta}/Arbol_de_pitaya_medio_de_4_a_7.png"
        if cantidad >= cfg.CARDON_UMBRAL_BAJO:
            return f"{carpeta}/Arbol_de_pitaya_bajo_de_1_a_4.png"
        if cantidad >= cfg.CARDON_UMBRAL_MUY_BAJO:
            return f"{carpeta}/Arbol_de_pitaya_muy_bajo_de_1_a_0.png"
        return f"{carpeta}/Arbol_de_pitaya_nada_de_0.png"

    def dibujar(self, mundo, pantalla):
        # Se dibuja en orden de creación: la Casa queda debajo de los PNJ
        for id_entidad, (pos, imagen) in mundo.entidades_con(
            ComponenteTransformacion, ComponenteRenderizado
        ):
            rect = pygame.Rect(pos.x, pos.y, imagen.ancho, imagen.alto)
            rutina = mundo.obtener(id_entidad, ComponenteRutinaTrabajador)
            nodo = mundo.obtener(id_entidad, ComponenteNodoRecurso)
            sel = mundo.obtener(id_entidad, ComponenteSeleccionable)
            seleccionado = sel is not None and sel.seleccionado

            if rutina is not None:
                ruta_sprite = self._sprite_pnj(rutina, seleccionado)
                superficie = cargar_imagen(
                    ruta_sprite, (imagen.ancho, imagen.alto), imagen.color
                )
                pantalla.blit(superficie, rect.topleft)
            elif nodo is not None and nodo.tipo == "comida":
                ruta_sprite = self._sprite_cardon(nodo.cantidad)
                superficie = cargar_imagen(
                    ruta_sprite, (imagen.ancho, imagen.alto), imagen.color
                )
                pantalla.blit(superficie, rect.topleft)
            elif imagen.sprite is not None:
                superficie = cargar_imagen(
                    imagen.sprite, (imagen.ancho, imagen.alto), imagen.color
                )
                pantalla.blit(superficie, rect.topleft)
            else:
                pygame.draw.rect(pantalla, imagen.color, rect)

            if seleccionado:
                pygame.draw.rect(pantalla, (255, 255, 255), rect, 2)

            # Textos de depuración: cantidad del recurso y carga del PNJ
            if nodo is not None:
                self._texto(pantalla, str(nodo.cantidad), (rect.centerx, rect.bottom - 10))

            if rutina is not None:
                if rutina.carga > 0:
                    self._texto(pantalla, str(rutina.carga), (rect.right + 10, rect.top + 8))
                if rutina.estado == ESTADO_HAMBRIENTO:
                    icono = rect_icono_hambre(pos, imagen)
                    pygame.draw.rect(pantalla, (255, 255, 255), icono)
                    margen = 2
                    tam_img = (icono.width - margen * 2, icono.height - margen * 2)
                    img_hambre = cargar_imagen("Icono_de_hambre.png", tam_img)
                    pantalla.blit(img_hambre, (icono.x + margen, icono.y + margen))
                    pygame.draw.rect(pantalla, (200, 40, 40), icono, 1)

    def _texto(self, pantalla, texto, centro):
        imagen = self.fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(imagen, imagen.get_rect(center=centro))


class SistemaInterfaz:
    """Panel derecho (reservas, reloj, velocidades, crear PNJ) y menús de pausa/audio."""

    def __init__(self):
        self.fuente = pygame.font.Font(None, 26)
        self.fuente_titulo = pygame.font.SysFont("arial", 46, bold=True, italic=True)
        self.fuente_boton = pygame.font.SysFont("arial", 22)
        self.fuente_audio = pygame.font.SysFont("arial", 19)

        self.pausado = False
        self.en_menu_audio = False
        self.slider_arrastrando = None

        ancho, alto, sep = 52, 32, 10
        x0 = cfg.ANCHO_MAPA + 8
        self.botones_velocidad = {
            vel: pygame.Rect(x0 + i * (ancho + sep), 144, ancho, alto)
            for i, vel in enumerate(cfg.VELOCIDADES)
        }
        self.boton_pnj = pygame.Rect(cfg.ANCHO_MAPA + 16, 192, 160, 36)
        self.boton_pausa = pygame.Rect(cfg.ANCHO_MAPA + 16, 516, 160, 38)

        cx, cy = cfg.ANCHO_MAPA // 2, cfg.ALTO_MAPA // 2
        self.rect_caja_pausa = pygame.Rect(cx - 190, cy - 210, 380, 420)
        ancho_btn, alto_btn = 280, 48
        bx = cx - ancho_btn // 2
        self.btn_continuar = pygame.Rect(bx, cy - 80, ancho_btn, alto_btn)
        self.btn_config_audio = pygame.Rect(bx, cy - 10, ancho_btn, alto_btn)
        self.btn_salir = pygame.Rect(bx, cy + 60, ancho_btn, alto_btn)

        self.rect_caja_audio = pygame.Rect(cx - 330, cy - 215, 660, 430)
        self.categorias_audio = [
            ("general", "Sonido general"),
            ("efectos", "Sonido de efectos"),
            ("voces", "Voces de NPCs"),
            ("ambiente", "Sonido de ambiente"),
            ("musica", "Música (OST)"),
        ]
        self.rects_sliders = {
            clave: pygame.Rect(
                self.rect_caja_audio.x + 420,
                self.rect_caja_audio.y + 58 + i * 58 + 16,
                190,
                16,
            )
            for i, (clave, _) in enumerate(self.categorias_audio)
        }
        self.btn_volver_audio = pygame.Rect(
            cx - 100, self.rect_caja_audio.bottom - 56, 200, 40
        )

    def manejar_evento(self, escena, evento):
        """Devuelve True si el evento fue consumido por la interfaz o la pausa."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            if self.en_menu_audio:
                self.en_menu_audio = False
                self.slider_arrastrando = None
            else:
                self.pausado = not self.pausado
            return True

        if self.pausado:
            self._manejar_evento_pausa(evento)
            return True

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.boton_pausa.collidepoint(evento.pos):
                self.pausado = True
                self.en_menu_audio = False
                return True
            if self.boton_pnj.collidepoint(evento.pos):
                escena.crear_pnj_nuevo()
                return True
            for velocidad, rect in self.botones_velocidad.items():
                if rect.collidepoint(evento.pos):
                    if not escena.hay_hambre():
                        escena.reloj.velocidad = velocidad
                    return True
        return False

    def _manejar_evento_pausa(self, evento):
        if not self.en_menu_audio:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self.btn_continuar.collidepoint(evento.pos):
                    self.pausado = False
                elif self.btn_config_audio.collidepoint(evento.pos):
                    self.en_menu_audio = True
                elif self.btn_salir.collidepoint(evento.pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_volver_audio.collidepoint(evento.pos):
                self.en_menu_audio = False
                self.slider_arrastrando = None
                return
            for clave, rect_slider in self.rects_sliders.items():
                if rect_slider.inflate(12, 16).collidepoint(evento.pos):
                    self.slider_arrastrando = clave
                    self._actualizar_slider(clave, evento.pos[0])
                    return
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.slider_arrastrando = None
        elif evento.type == pygame.MOUSEMOTION and self.slider_arrastrando is not None:
            self._actualizar_slider(self.slider_arrastrando, evento.pos[0])

    def _actualizar_slider(self, clave, mouse_x):
        rect = self.rects_sliders[clave]
        proporcion = (mouse_x - rect.x) / float(rect.width)
        VOLUMENES[clave] = int(round(max(0.0, min(1.0, proporcion)) * 100))
        actualizar_volumenes()

    def dibujar(self, escena, pantalla):
        x = cfg.ANCHO_MAPA + 16
        almacen = escena.mundo.obtener(escena.id_campamento, ComponenteAlmacen)
        pantalla.blit(self.fuente.render(f"Agua: {almacen.agua}", True, (255, 255, 255)), (x, 24))
        pantalla.blit(self.fuente.render(f"Comida: {almacen.comida}", True, (255, 255, 255)), (x, 56))
        pantalla.blit(
            self.fuente.render(f"Día: {escena.reloj.dia} / {cfg.DIAS_TOTALES}", True, (255, 255, 255)),
            (x, 88),
        )

        minutos = int(escena.reloj.segundos_dia / cfg.SEGUNDOS_POR_DIA * cfg.HORAS_POR_DIA * 60)
        pantalla.blit(
            self.fuente.render(f"Hora: {minutos // 60:02d}:{minutos % 60:02d}", True, (255, 255, 255)),
            (x, 112),
        )

        bloqueado = escena.hay_hambre()
        for velocidad, rect in self.botones_velocidad.items():
            activo = velocidad == escena.reloj.velocidad
            fondo = (50, 46, 42) if bloqueado else ((90, 130, 90) if activo else (70, 64, 58))
            pygame.draw.rect(pantalla, fondo, rect)
            pygame.draw.rect(pantalla, (255, 255, 255), rect, 2 if activo else 1)
            txt = self.fuente.render(f"x{velocidad}", True, (255, 255, 255))
            pantalla.blit(txt, txt.get_rect(center=rect.center))

        vivos = escena.pnj_vivos()
        fondo_pnj = (90, 130, 90) if escena.puede_crear_pnj() else (50, 46, 42)
        pygame.draw.rect(pantalla, fondo_pnj, self.boton_pnj)
        pygame.draw.rect(pantalla, (255, 255, 255), self.boton_pnj, 1)
        txt_pnj = self.fuente.render("Nuevo Cochimie", True, (255, 255, 255))
        pantalla.blit(txt_pnj, txt_pnj.get_rect(center=self.boton_pnj.center))

        detalle = "Máximo alcanzado" if vivos >= cfg.PNJ_MAXIMOS else f"Cuesta {escena.costo_pnj()} comida"
        pantalla.blit(self.fuente.render(detalle, True, (255, 255, 255)), (x, 236))
        pantalla.blit(self.fuente.render(f"PNJ: {vivos}/{cfg.PNJ_MAXIMOS}", True, (255, 255, 255)), (x, 262))

        pygame.draw.rect(pantalla, (138, 71, 14), self.boton_pausa)
        pygame.draw.rect(pantalla, (235, 221, 190), self.boton_pausa, 2)
        txt_pausa = self.fuente.render("Pausa", True, (255, 255, 255))
        pantalla.blit(txt_pausa, txt_pausa.get_rect(center=self.boton_pausa.center))

        if self.pausado:
            if self.en_menu_audio:
                self._dibujar_menu_audio(pantalla)
            else:
                self._dibujar_menu_pausa(pantalla)

    def _dibujar_menu_pausa(self, pantalla):
        pygame.draw.rect(pantalla, (235, 221, 190), self.rect_caja_pausa)
        pygame.draw.rect(pantalla, (130, 65, 10), self.rect_caja_pausa, 3)

        titulo = self.fuente_titulo.render("Pausa", True, (0, 0, 0))
        pantalla.blit(
            titulo,
            titulo.get_rect(center=(self.rect_caja_pausa.centerx, self.rect_caja_pausa.y + 65)),
        )

        for rect_btn, etiqueta in (
            (self.btn_continuar, "Continuar"),
            (self.btn_config_audio, "Configuracion de audio"),
            (self.btn_salir, "Salir"),
        ):
            pygame.draw.rect(pantalla, (138, 71, 14), rect_btn)
            txt = self.fuente_boton.render(etiqueta, True, (255, 255, 255))
            pantalla.blit(txt, txt.get_rect(center=rect_btn.center))

    def _dibujar_menu_audio(self, pantalla):
        pygame.draw.rect(pantalla, (34, 28, 26), self.rect_caja_audio)
        pygame.draw.rect(pantalla, (120, 95, 80), self.rect_caja_audio, 2)

        encabezado = self.fuente_audio.render("Volúmenes", True, (210, 200, 195))
        pantalla.blit(encabezado, (self.rect_caja_audio.x + 20, self.rect_caja_audio.y + 18))

        y0 = self.rect_caja_audio.y + 58
        for i, (clave, nombre) in enumerate(self.categorias_audio):
            fila_y = y0 + i * 58
            rect_fila = pygame.Rect(
                self.rect_caja_audio.x + 18, fila_y, self.rect_caja_audio.width - 36, 48
            )
            pygame.draw.rect(pantalla, (56, 46, 43), rect_fila)
            pygame.draw.rect(pantalla, (82, 70, 66), rect_fila, 1)

            lbl = self.fuente_audio.render(nombre, True, (215, 208, 204))
            pantalla.blit(lbl, (rect_fila.x + 16, rect_fila.centery - lbl.get_height() // 2))

            valor = VOLUMENES[clave]
            x_val = self.rect_caja_audio.x + 315
            pygame.draw.line(
                pantalla, (90, 78, 74), (x_val - 12, rect_fila.y + 8), (x_val - 12, rect_fila.bottom - 8)
            )
            txt_val = self.fuente_audio.render(f"{valor}", True, (235, 230, 225))
            pantalla.blit(txt_val, (x_val, rect_fila.centery - txt_val.get_height() // 2 - 3))

            ancho_sub = 76
            pygame.draw.rect(pantalla, (85, 75, 72), (x_val - 4, rect_fila.bottom - 7, ancho_sub, 3))
            pygame.draw.rect(
                pantalla,
                (235, 235, 235),
                (x_val - 4, rect_fila.bottom - 7, int(ancho_sub * (valor / 100.0)), 3),
            )

            rect_slider = self.rects_sliders[clave]
            y_linea = rect_slider.centery
            pygame.draw.line(
                pantalla, (95, 85, 82), (rect_slider.left, y_linea), (rect_slider.right, y_linea), 3
            )
            x_activo = rect_slider.left + int(rect_slider.width * (valor / 100.0))
            if valor > 0:
                pygame.draw.line(
                    pantalla, (235, 235, 235), (rect_slider.left, y_linea), (x_activo, y_linea), 3
                )
            pygame.draw.circle(pantalla, (255, 255, 255), (x_activo, y_linea), 6)

        pygame.draw.rect(pantalla, (138, 71, 14), self.btn_volver_audio)
        pygame.draw.rect(pantalla, (235, 221, 190), self.btn_volver_audio, 1)
        txt_volver = self.fuente_boton.render("Volver", True, (255, 255, 255))
        pantalla.blit(txt_volver, txt_volver.get_rect(center=self.btn_volver_audio.center))
