"""Menú principal del juego: Inicio, consejos, configuración de audio y salida."""
import pygame

from codigo import configuracion as cfg
from codigo.gestor_recursos import (
    VOLUMENES,
    actualizar_volumenes,
    alternar_pantalla_completa,
    cargar_fuente,
    cargar_imagen,
    dibujar_texto_retro,
    es_pantalla_completa,
    iniciar_ambiente,
    reproducir_sonido,
)

COLOR_FONDO = cfg.COLOR_PANEL
COLOR_CREMA = (235, 221, 190)
COLOR_CAFE = (138, 71, 14)
COLOR_CAFE_CLARO = (175, 95, 25)
COLOR_CAFE_OSCURO = (130, 65, 10)


class EscenaMenu:
    """Pantalla inicial del juego con navegación y ajustes."""

    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.siguiente = None

        self.fuente_titulo = cargar_fuente(20, retro=True)
        self.fuente_subtitulo = cargar_fuente(9, retro=True)
        self.fuente_boton = cargar_fuente(12, retro=True)
        self.fuente_audio = pygame.font.SysFont("arial", 19)

        cx = cfg.ANCHO_VENTANA // 2
        ancho_btn, alto_btn = 320, 44

        self.btn_jugar = pygame.Rect(cx - ancho_btn // 2, 244, ancho_btn, alto_btn)
        self.btn_consejos = pygame.Rect(cx - ancho_btn // 2, 298, ancho_btn, alto_btn)
        self.btn_audio = pygame.Rect(cx - ancho_btn // 2, 352, ancho_btn, alto_btn)
        self.btn_pantalla = pygame.Rect(cx - ancho_btn // 2, 406, ancho_btn, alto_btn)
        self.btn_salir = pygame.Rect(cx - ancho_btn // 2, 460, ancho_btn, alto_btn)

        # Modal de configuración de audio
        self.en_menu_audio = False
        self.slider_arrastrando = None
        self.rect_caja_audio = pygame.Rect(cx - 330, cfg.ALTO_VENTANA // 2 - 215, 660, 430)
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

        # Logo si existe
        self.logo = cargar_imagen("Logo.png", carpeta="imagenes", tamano=None)
        if self.logo:
            # Escalar proporcionalmente si es muy grande
            ancho_orig, alto_orig = self.logo.get_size()
            if alto_orig > 150:
                escala = 200 / float(alto_orig)
                self.logo = pygame.transform.smoothscale(
                    self.logo, (int(ancho_orig * escala), 200)
                )

        iniciar_ambiente()

    def manejar_evento(self, evento):
        if self.en_menu_audio:
            self._manejar_evento_audio(evento)
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_jugar.collidepoint(evento.pos):
                reproducir_sonido("sonidos ambientales/recojer_agua.wav")
                self.siguiente = "juego"
            elif self.btn_consejos.collidepoint(evento.pos):
                self.siguiente = "carga"
            elif self.btn_audio.collidepoint(evento.pos):
                self.en_menu_audio = True
            elif self.btn_pantalla.collidepoint(evento.pos):
                alternar_pantalla_completa()
            elif self.btn_salir.collidepoint(evento.pos):
                self.siguiente = "salir"

        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.siguiente = "juego"
            elif evento.key == pygame.K_ESCAPE:
                self.siguiente = "salir"

    def _manejar_evento_audio(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.en_menu_audio = False
            self.slider_arrastrando = None
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

    def actualizar(self, dt):
        pass

    def dibujar(self):
        p = self.pantalla
        p.fill(COLOR_FONDO)
        cx = cfg.ANCHO_VENTANA // 2

        # Fondo con suelo desértico decorativo
        pygame.draw.rect(p, cfg.COLOR_SUELO, pygame.Rect(0, 500, cfg.ANCHO_VENTANA, 76))
        pygame.draw.line(p, cfg.COLOR_LINEA, (0, 500), (cfg.ANCHO_VENTANA, 500), 2)

        # Decoraciones a los lados
        palma = cargar_imagen("Vegetacion/Decoracion/Palma.png", tamano=(40, 80))
        cactus = cargar_imagen("Vegetacion/Decoracion/cactus.png", tamano=(36, 72))
        cochimi_h = cargar_imagen("Npcs/Cochimie hombre/Cochimie_h_saludando.png", tamano=(36, 36))
        cochimi_m = cargar_imagen("Npcs/Cochimie mujer/cochimie_m_sentada.png", tamano=(36, 36))

        p.blit(palma, (40, 420))
        p.blit(cactus, (100, 430))
        p.blit(cochimi_h, (150, 465))

        p.blit(cactus, (cfg.ANCHO_VENTANA - 150, 430))
        p.blit(palma, (cfg.ANCHO_VENTANA - 90, 420))
        p.blit(cochimi_m, (cfg.ANCHO_VENTANA - 200, 465))

        # Logo o Título
        if self.logo:
            rect_logo = self.logo.get_rect(center=(cx, 115))
            p.blit(self.logo, rect_logo)
            dibujar_texto_retro(
                p,
                "PROTECCIÓN DEL ECOSISTEMA Y DISTRIBUCIÓN DEL AGUA",
                self.fuente_subtitulo,
                COLOR_CREMA,
                centro=(cx, 220),
                offset_sombra=(1, 1),
                con_borde=True,
            )
        else:
            dibujar_texto_retro(
                p,
                "EL ÚLTIMO AGUAJE: LEGADO COCHIMÍ",
                self.fuente_titulo,
                (255, 220, 110),
                centro=(cx, 90),
                offset_sombra=(3, 3),
                con_borde=True,
            )
            dibujar_texto_retro(
                p,
                "PROTECCIÓN DEL ECOSISTEMA Y DISTRIBUCIÓN DEL AGUA",
                self.fuente_subtitulo,
                (220, 200, 170),
                centro=(cx, 145),
                offset_sombra=(1, 1),
                con_borde=True,
            )

        # Botones del menú
        etiqueta_pantalla = (
            "MODO VENTANA" if es_pantalla_completa() else "PANTALLA COMPLETA"
        )
        botones = [
            (self.btn_jugar, "JUGAR"),
            (self.btn_consejos, "GUÍA Y CONSEJOS"),
            (self.btn_audio, "CONFIGURACIÓN DE AUDIO"),
            (self.btn_pantalla, etiqueta_pantalla),
            (self.btn_salir, "SALIR"),
        ]

        pos_mouse = pygame.mouse.get_pos()
        for rect, etiqueta in botones:
            hover = rect.collidepoint(pos_mouse)
            color_fondo = COLOR_CAFE_CLARO if hover else COLOR_CAFE
            pygame.draw.rect(p, color_fondo, rect, border_radius=6)
            pygame.draw.rect(p, COLOR_CREMA, rect, width=2, border_radius=6)
            dibujar_texto_retro(
                p,
                etiqueta,
                self.fuente_boton,
                (255, 255, 255),
                centro=rect.center,
                offset_sombra=(2, 2),
                con_borde=True,
            )

        # Modal de configuración de audio si está activo
        if self.en_menu_audio:
            self._dibujar_menu_audio(p)

    def _dibujar_menu_audio(self, pantalla):
        pygame.draw.rect(pantalla, (34, 28, 26), self.rect_caja_audio, border_radius=8)
        pygame.draw.rect(pantalla, (120, 95, 80), self.rect_caja_audio, 2, border_radius=8)

        encabezado = self.fuente_audio.render("Volúmenes de Audio", True, (210, 200, 195))
        pantalla.blit(encabezado, (self.rect_caja_audio.x + 20, self.rect_caja_audio.y + 18))

        y0 = self.rect_caja_audio.y + 58
        for i, (clave, nombre) in enumerate(self.categorias_audio):
            fila_y = y0 + i * 58
            rect_fila = pygame.Rect(
                self.rect_caja_audio.x + 18, fila_y, self.rect_caja_audio.width - 36, 48
            )
            pygame.draw.rect(pantalla, (56, 46, 43), rect_fila, border_radius=4)
            pygame.draw.rect(pantalla, (82, 70, 66), rect_fila, 1, border_radius=4)

            lbl = self.fuente_audio.render(nombre, True, (215, 208, 204))
            pantalla.blit(lbl, (rect_fila.x + 16, rect_fila.centery - lbl.get_height() // 2))

            valor = VOLUMENES[clave]
            x_val = self.rect_caja_audio.x + 315
            txt_val = self.fuente_audio.render(f"{valor}", True, (235, 230, 225))
            pantalla.blit(txt_val, (x_val, rect_fila.centery - txt_val.get_height() // 2 - 3))

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

        pygame.draw.rect(pantalla, COLOR_CAFE, self.btn_volver_audio, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_CREMA, self.btn_volver_audio, 1, border_radius=6)
        txt_volver = self.fuente_boton.render("Volver", True, (255, 255, 255))
        pantalla.blit(txt_volver, txt_volver.get_rect(center=self.btn_volver_audio.center))
