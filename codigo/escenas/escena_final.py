"""Escena cinemática para finales de Victoria (Win) y Game Over.

Presenta una secuencia animada con narrativa de acuerdo a las condiciones
alcanzadas al día 30 (o previas), efectos visuales temáticos (sequía vs oasis)
y opciones posteriores para volver al inicio/menú principal o salir del juego.
"""
import math
import random
import pygame

from codigo import configuracion as cfg
from codigo.gestor_recursos import (
    cargar_fuente,
    cargar_imagen,
    cargar_sonido,
    detener_todo_audio,
    dibujar_texto_retro,
    iniciar_ost,
    reproducir_fin_del_juego,
    reproducir_sonido,
)

# Paletas de color
COLOR_FONDO_GAMEOVER = (22, 16, 14)
COLOR_FONDO_VICTORIA = (18, 28, 32)
COLOR_CREMA = (238, 226, 204)
COLOR_DORADO = (255, 215, 110)
COLOR_ROJO_TITULO = (230, 60, 50)
COLOR_TEXTO_OSCURO = (25, 20, 18)

# Botones
COLOR_BTN_NORMAL = (138, 71, 14)
COLOR_BTN_HOVER = (175, 95, 25)
COLOR_BTN_BORDE = (235, 221, 190)
COLOR_BTN_VICTORIA = (42, 110, 75)
COLOR_BTN_VICTORIA_HOVER = (60, 145, 100)


def partir_texto(texto, fuente, ancho_maximo):
    """Divide un texto en varias líneas sin cortar palabras."""
    parrafos = texto.split("\n\n")
    lineas = []
    for indice, parrafo in enumerate(parrafos):
        actual = ""
        for palabra in parrafo.split():
            prueba = f"{actual} {palabra}".strip()
            if fuente.size(prueba)[0] <= ancho_maximo:
                actual = prueba
            else:
                lineas.append(actual)
                actual = palabra
        if actual:
            lineas.append(actual)
        if indice < len(parrafos) - 1:
            lineas.append("")
    return lineas


class ParticulaCinematica:
    """Partículas de polvo/viento para Game Over o destellos/gotas para Victoria."""

    def __init__(self, tipo):
        self.tipo = tipo
        self.reiniciar(inicial=True)

    def reiniciar(self, inicial=False):
        if self.tipo == "game_over":
            self.x = random.uniform(0, cfg.ANCHO_VENTANA) if inicial else -10
            self.y = random.uniform(80, cfg.ALTO_VENTANA - 60)
            self.vx = random.uniform(120, 260)
            self.vy = random.uniform(-20, 40)
            self.tam = random.randint(2, 4)
            self.color = random.choice([
                (190, 150, 100),
                (160, 120, 70),
                (210, 180, 130),
            ])
            self.alpha = random.randint(80, 190)
        else:
            self.x = random.uniform(40, cfg.ANCHO_VENTANA - 40)
            self.y = random.uniform(cfg.ALTO_VENTANA - 100, cfg.ALTO_VENTANA - 20) if not inicial else random.uniform(100, cfg.ALTO_VENTANA - 60)
            self.vx = random.uniform(-15, 15)
            self.vy = random.uniform(-40, -90)
            self.tam = random.randint(2, 5)
            self.color = random.choice([
                (255, 235, 150),
                (140, 220, 255),
                (255, 255, 255),
                (100, 200, 230),
            ])
            self.alpha = random.randint(100, 220)

    def actualizar(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.tipo == "game_over":
            if self.x > cfg.ANCHO_VENTANA + 20:
                self.reiniciar()
        else:
            if self.y < 60:
                self.reiniciar()


class EscenaFinal:
    """Cinemática de Game Over o Victoria con opciones posteriores."""

    def __init__(
        self,
        pantalla,
        tipo="game_over",
        motivo="recursos_agotados_30",
        mensaje="",
        agua=0,
        comida=0,
        pnj_vivos=0,
        dia=30,
    ):
        self.pantalla = pantalla
        self.tipo = tipo  # "victoria" o "game_over"
        self.motivo = motivo
        self.mensaje = mensaje
        self.agua = agua
        self.comida = comida
        self.pnj_vivos = pnj_vivos
        self.dia = dia

        self.siguiente = None
        self.tiempo = 0.0
        self.duracion_cinematica = 4.2  # tiempo tras el cual se habilitan botones
        self.cinematica_completa = False

        # Fuentes (Títulos, subtítulos, estadísticas y botones en estilo retro pixel art)
        self.fuente_titulo = cargar_fuente(34, retro=True)
        self.fuente_subtitulo = cargar_fuente(13, retro=True)
        self.fuente_narrativa = pygame.font.SysFont(
            "arial", 14 if self.tipo == "victoria" else 20
        )
        self.fuente_stats = cargar_fuente(11, retro=True)
        self.fuente_boton = cargar_fuente(12, retro=True)
        self.fuente_skip = cargar_fuente(10, retro=True)

        # Configuración de narrativa y títulos según motivo
        self._configurar_narrativa()

        # Partículas temáticas
        self.particulas = [ParticulaCinematica(self.tipo) for _ in range(35)]

        # Posicionamiento de botones (lado a lado, centrados abajo)
        cx = cfg.ANCHO_VENTANA // 2
        ancho_btn, alto_btn = 260, 48
        espacio = 30
        y_btn = cfg.ALTO_VENTANA - 84
        self.btn_1 = pygame.Rect(cx - ancho_btn - espacio // 2, y_btn, ancho_btn, alto_btn)
        self.btn_2 = pygame.Rect(cx + espacio // 2, y_btn, ancho_btn, alto_btn)

        # Superficies para efectos de fundido y viñeta
        self.fade_surf = pygame.Surface((cfg.ANCHO_VENTANA, cfg.ALTO_VENTANA))
        self.fade_surf.fill((0, 0, 0))

        # Iniciar audio correspondiente
        self._iniciar_audio()

    def _configurar_narrativa(self):
        if self.tipo == "victoria":
            self.titulo_principal = "¡VICTORIA!"
            self.mensaje = (
                "Lo lograste porque cuidaste lo que tenías: repartiste el trabajo, "
                "dejaste que aguajes, plantas y venados se recuperaran y guardaste para "
                "los días difíciles. Así vivieron durante siglos los pueblos de la "
                "península: tomando solo lo que el desierto podía devolver.\n\n"
                "Hoy, en Baja California Sur, el agua de las ciudades sale de acuíferos "
                "que se sobreexplotan: se extrae más de lo que la lluvia repone. "
                "A diferencia del juego, ahí no se regenera cada 8 segundos."
            )
            if self.motivo == "recursos_full_30":
                self.subtitulo = "RECURSOS LLENOS A LOS 30 DÍAS"
            elif self.motivo == "agua_sin_comida_30":
                self.subtitulo = "EL MILAGRO DEL AGUAJE (DÍA 30)"
            else:
                self.subtitulo = "SUPERVIVENCIA COCHIMÍ (DÍA 30)"
            self.etiqueta_btn_1 = "Volver al inicio"
            self.etiqueta_btn_2 = "Salir del juego"
        else:
            self.titulo_principal = "GAME OVER"
            self.mensaje = (
                "Tu tribu no alcanzó a reunir lo suficiente. Piensa qué pasó: "
                "¿se agotó un aguaje? ¿Había demasiados cochimíes para tan poca agua? "
                "¿Se cazaron todos los venados?\n\n"
                "En el juego puedes volver a intentarlo. En la vida real, un acuífero "
                "que se agota no se reinicia."
            )
            if self.motivo == "sin_agua_con_comida_30":
                self.subtitulo = "SIN AGUA GUARDADA A LOS 30 DÍAS"
            elif self.motivo == "recursos_agotados_30":
                self.subtitulo = "RECURSOS AGOTADOS A LOS 30 DÍAS"
            elif self.motivo == "pnj_muertos":
                self.subtitulo = "TODOS LOS POBLADORES HAN CAÍDO"
            else:
                self.subtitulo = "FIN DEL JUEGO"
            self.etiqueta_btn_1 = "Volver al menú principal"
            self.etiqueta_btn_2 = "Salir del juego"

    def _iniciar_audio(self):
        """Detiene audio anterior e inicia sonido acorde al final."""
        detener_todo_audio()
        if self.tipo == "victoria":
            # Tocar efecto de tributo y luego música festiva
            reproducir_sonido("sonidos ambientales/tributo.wav")
            reproducir_sonido("sonidos ambientales/recojer_agua.wav")
            iniciar_ost()
        else:
            # Game Over: reproduce fin_del_juego.mp3 o viento
            reproducir_fin_del_juego()
            reproducir_sonido(
                "sonidos ambientales/Efecto_de sonido_de Viento_Clima.mp3",
                categoria="ambiente",
            )

    def saltar_cinematica(self):
        """Permite al jugador acelerar la animación y mostrar los botones de inmediato."""
        self.tiempo = max(self.tiempo, self.duracion_cinematica + 0.1)
        self.cinematica_completa = True

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                if not self.cinematica_completa:
                    self.saltar_cinematica()
                    return

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not self.cinematica_completa:
                self.saltar_cinematica()
                return

            if self.btn_1.collidepoint(evento.pos):
                # Volver al inicio / menú principal
                self.siguiente = "menu"
            elif self.btn_2.collidepoint(evento.pos):
                # Salir del juego
                self.siguiente = "salir"

    def actualizar(self, dt):
        self.tiempo += dt
        if self.tiempo >= self.duracion_cinematica:
            self.cinematica_completa = True

        for p in self.particulas:
            p.actualizar(dt)

    def dibujar(self):
        p = self.pantalla
        p.fill(COLOR_FONDO_VICTORIA if self.tipo == "victoria" else COLOR_FONDO_GAMEOVER)

        # 1. Fondo estilizado: cielo con degradado y suelo
        self._dibujar_fondo_paisaje(p)

        # 2. Viñeta escénica con sprites temáticos
        self._dibujar_vigneta_sprites(p)

        # 3. Partículas ambientales
        for particula in self.particulas:
            surf_p = pygame.Surface((particula.tam * 2, particula.tam * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf_p,
                (*particula.color, particula.alpha),
                (particula.tam, particula.tam),
                particula.tam,
            )
            p.blit(surf_p, (particula.x, particula.y))

        # 4. Barras de cine (widescreen letterboxing)
        alto_barra = 42
        pygame.draw.rect(p, (10, 8, 8), pygame.Rect(0, 0, cfg.ANCHO_VENTANA, alto_barra))
        pygame.draw.rect(
            p,
            (10, 8, 8),
            pygame.Rect(0, cfg.ALTO_VENTANA - alto_barra, cfg.ANCHO_VENTANA, alto_barra),
        )

        # 5. Contenido narrativo y títulos
        self._dibujar_texto_cinematica(p)

        # 6. Botones interactivos (aparecen cuando la cinemática concluye o se salta)
        if self.cinematica_completa:
            self._dibujar_botones(p)
        else:
            # Mensaje para saltar
            dibujar_texto_retro(
                p,
                "[ESPACIO / CLIC PARA SALTAR CINEMÁTICA]",
                self.fuente_skip,
                (200, 190, 175),
                centro=(cfg.ANCHO_VENTANA // 2, cfg.ALTO_VENTANA - 22),
                offset_sombra=(1, 1),
                con_borde=False,
            )

        # 7. Fundido de entrada inicial (fade in)
        if self.tiempo < 1.2:
            alpha = int(max(0, min(255, (1.0 - (self.tiempo / 1.2)) * 255)))
            if alpha > 0:
                self.fade_surf.set_alpha(alpha)
                p.blit(self.fade_surf, (0, 0))

    def _dibujar_fondo_paisaje(self, p):
        """Dibuja un fondo ambiental con gradientes y dunas según el final."""
        h = cfg.ALTO_VENTANA
        w = cfg.ANCHO_VENTANA

        if self.tipo == "victoria":
            # Cielo cálido de amanecer triunfal
            cielo_top = (25, 45, 60)
            cielo_bottom = (195, 140, 75)
            suelo_color = (194, 168, 115)
        else:
            # Cielo de tormenta de arena y sequía
            cielo_top = (45, 20, 18)
            cielo_bottom = (135, 65, 40)
            suelo_color = (105, 68, 48)

        # Franjas simulando gradiente
        lineas = 24
        alto_franja = 260 // lineas
        for i in range(lineas):
            t = i / float(lineas - 1)
            r = int(cielo_top[0] + (cielo_bottom[0] - cielo_top[0]) * t)
            g = int(cielo_top[1] + (cielo_bottom[1] - cielo_top[1]) * t)
            b = int(cielo_top[2] + (cielo_bottom[2] - cielo_top[2]) * t)
            pygame.draw.rect(p, (r, g, b), pygame.Rect(0, 42 + i * alto_franja, w, alto_franja + 1))

        # Suelo
        pygame.draw.rect(p, suelo_color, pygame.Rect(0, 300, w, h - 300))

        # Dunas sutiles
        duna_color = (
            min(255, suelo_color[0] + 15),
            min(255, suelo_color[1] + 12),
            min(255, suelo_color[2] + 8),
        )
        pygame.draw.polygon(
            p,
            duna_color,
            [(0, 310), (w * 0.35, 290), (w * 0.7, 315), (w, 295), (w, 335), (0, 335)],
        )

    def _dibujar_vigneta_sprites(self, p):
        """Ilustración temática usando los recursos gráficos del proyecto."""
        y_suelo = 370

        if self.tipo == "victoria":
            # 1. Base con abundancia (alto)
            base_img = cargar_imagen("base/Base_nivel_alto.png", tamano=(112, 112))
            p.blit(base_img, (80, y_suelo - 100))

            # 2. Palma y cardón con frutos
            palma_img = cargar_imagen("Vegetacion/Decoracion/Palma.png", tamano=(48, 96))
            p.blit(palma_img, (20, y_suelo - 90))

            cardon_img = cargar_imagen(
                "Vegetacion/Planta de recolecion/Arbol_de_pitaya_lleno_de_7_a_10.png",
                tamano=(48, 96),
            )
            p.blit(cardon_img, (200, y_suelo - 90))

            # 3. Aldeanos celebrando con animación sutil
            bob = int(math.sin(self.tiempo * 5.0) * 3)
            hombre_img = cargar_imagen("Npcs/Cochimie hombre/Cochimie_h_saludando.png", tamano=(42, 42))
            mujer_img = cargar_imagen("Npcs/Cochimie mujer/cochimie_m_saludando.png", tamano=(42, 42))
            p.blit(hombre_img, (730, y_suelo - 38 + bob))
            p.blit(mujer_img, (780, y_suelo - 38 - bob))

            # 4. Venado en el horizonte
            venado_img = cargar_imagen("animales/venado_de_frente.png", tamano=(44, 44))
            p.blit(venado_img, (850, y_suelo - 36))

        else:
            # 1. Base vacía / destruida por la sequía
            base_img = cargar_imagen("base/Base_nivel_nada.png", tamano=(112, 112))
            p.blit(base_img, (80, y_suelo - 100))

            # 2. Cardón marchito / sin frutos
            cardon_img = cargar_imagen(
                "Vegetacion/Planta de recolecion/Arbol_de_pitaya_nada_de_0.png",
                tamano=(48, 96),
            )
            p.blit(cardon_img, (205, y_suelo - 90))

            # 3. Piedras en el camino
            piedra_img = cargar_imagen("Vegetacion/Decoracion/piedra.png", tamano=(36, 36))
            p.blit(piedra_img, (28, y_suelo - 32))

            # 4. Cochimíes caídos o derrotados
            hombre_m = cargar_imagen("Npcs/Cochimie hombre/cochimie_h_muerto.png", tamano=(42, 42))
            mujer_m = cargar_imagen("Npcs/Cochimie mujer/cochimie_m_muerta.png", tamano=(42, 42))
            p.blit(hombre_m, (740, y_suelo - 28))
            p.blit(mujer_m, (810, y_suelo - 28))

    def _dibujar_texto_cinematica(self, p):
        """Caja central de diálogo cinemático, estadísticas y titulares."""
        cx = cfg.ANCHO_VENTANA // 2

        # Título principal con estilo retro (arcade shadow + outline)
        color_titulo = COLOR_DORADO if self.tipo == "victoria" else COLOR_ROJO_TITULO
        sombra_titulo = (70, 40, 10) if self.tipo == "victoria" else (50, 10, 10)
        dibujar_texto_retro(
            p,
            self.titulo_principal,
            self.fuente_titulo,
            color_titulo,
            centro=(cx, 75),
            offset_sombra=(4, 4),
            color_sombra=sombra_titulo,
            con_borde=True,
            color_borde=(10, 8, 8),
        )

        # Subtítulo retro (condición lograda o motivo)
        color_sub = (255, 235, 180) if self.tipo == "victoria" else (245, 175, 155)
        dibujar_texto_retro(
            p,
            self.subtitulo,
            self.fuente_subtitulo,
            color_sub,
            centro=(cx, 122),
            offset_sombra=(2, 2),
            con_borde=True,
            color_borde=(15, 10, 8),
        )

        # Caja de narrativa pergamino/piedra
        ancho_caja = 720
        alto_caja = 230
        caja_rect = pygame.Rect(cx - ancho_caja // 2, 150, ancho_caja, alto_caja)

        color_caja = (242, 232, 210) if self.tipo == "victoria" else (48, 36, 32)
        borde_caja = (180, 130, 60) if self.tipo == "victoria" else (160, 65, 45)
        color_texto = (35, 25, 20) if self.tipo == "victoria" else (235, 220, 210)

        pygame.draw.rect(p, color_caja, caja_rect, border_radius=8)
        pygame.draw.rect(p, borde_caja, caja_rect, width=3, border_radius=8)

        # Líneas de texto narrativo
        lineas = partir_texto(self.mensaje, self.fuente_narrativa, ancho_caja - 60)
        y_txt = caja_rect.y + 24
        alto_linea = self.fuente_narrativa.get_linesize() + 4
        for linea in lineas:
            if linea:
                txt_render = self.fuente_narrativa.render(linea, True, color_texto)
                p.blit(txt_render, txt_render.get_rect(center=(cx, y_txt + alto_linea // 2)))
            y_txt += alto_linea

        # Separador para las estadísticas
        y_sep = caja_rect.bottom - 58
        pygame.draw.line(p, borde_caja, (caja_rect.x + 30, y_sep), (caja_rect.right - 30, y_sep), 1)

        # Estadísticas finales en tipografía retro
        stats_texto = (
            f"DÍA: {self.dia}/30  |  AGUA: {self.agua}  |  "
            f"COMIDA: {self.comida}  |  POBLACIÓN: {self.pnj_vivos}"
        )
        color_stats = (110, 60, 15) if self.tipo == "victoria" else (225, 150, 130)
        dibujar_texto_retro(
            p,
            stats_texto,
            self.fuente_stats,
            color_stats,
            centro=(cx, y_sep + 30),
            offset_sombra=None,
            con_borde=False,
        )

    def _dibujar_botones(self, p):
        """Renderiza los dos botones interactivos posteriores a la cinemática."""
        pos_mouse = pygame.mouse.get_pos()

        # Configurar colores según victoria o derrota
        if self.tipo == "victoria":
            color_btn = COLOR_BTN_VICTORIA
            color_hover = COLOR_BTN_VICTORIA_HOVER
        else:
            color_btn = COLOR_BTN_NORMAL
            color_hover = COLOR_BTN_HOVER

        # Botón 1
        hover1 = self.btn_1.collidepoint(pos_mouse)
        pygame.draw.rect(p, color_hover if hover1 else color_btn, self.btn_1, border_radius=6)
        pygame.draw.rect(p, COLOR_BTN_BORDE, self.btn_1, width=2, border_radius=6)
        dibujar_texto_retro(
            p,
            self.etiqueta_btn_1.upper(),
            self.fuente_boton,
            (255, 255, 255),
            centro=self.btn_1.center,
            offset_sombra=(2, 2),
            con_borde=True,
        )

        # Botón 2
        hover2 = self.btn_2.collidepoint(pos_mouse)
        pygame.draw.rect(p, color_hover if hover2 else color_btn, self.btn_2, border_radius=6)
        pygame.draw.rect(p, COLOR_BTN_BORDE, self.btn_2, width=2, border_radius=6)
        dibujar_texto_retro(
            p,
            self.etiqueta_btn_2.upper(),
            self.fuente_boton,
            (255, 255, 255),
            centro=self.btn_2.center,
            offset_sombra=(2, 2),
            con_borde=True,
        )
