"""Pantalla de carga simulada: barra de progreso y lista de consejos."""
import pygame

from codigo import configuracion as cfg
from codigo.consejos import CONSEJOS
from codigo.gestor_recursos import cargar_fuente, dibujar_texto_retro

COLOR_FONDO = cfg.COLOR_PANEL
COLOR_CREMA = (235, 221, 190)
COLOR_CAFE = (138, 71, 14)
COLOR_CAFE_OSCURO = (130, 65, 10)
COLOR_CAFE_CLARO = (168, 98, 30)   # al pasar el mouse por un botón
COLOR_TEXTO = (30, 20, 10)


def partir_texto(texto, fuente, ancho_maximo):
    """Divide el texto en líneas que quepan en el ancho dado."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if fuente.size(prueba)[0] <= ancho_maximo:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


class EscenaCarga:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.siguiente = None   # nombre de la escena a la que pasar (None = sigue aquí)
        self.tiempo = 0.0
        self.indice = 0

        self.fuente_titulo = cargar_fuente(20, retro=True)
        self.fuente_subtitulo = pygame.font.SysFont("arial", 28, italic=True)
        self.fuente_consejo = pygame.font.SysFont("arial", 26)
        self.fuente_chica = pygame.font.SysFont("arial", 18)
        self.fuente_boton = pygame.font.SysFont("arial", 22)

        centro = cfg.ANCHO_VENTANA // 2
        self.caja = pygame.Rect(centro - 360, 170, 720, 190)
        self.btn_anterior = pygame.Rect(centro - 170, 376, 150, 40)
        self.btn_siguiente = pygame.Rect(centro + 20, 376, 150, 40)
        self.barra = pygame.Rect(centro - 300, 446, 600, 22)
        self.btn_continuar = pygame.Rect(centro - 100, 486, 200, 48)

    def _progreso(self):
        t = min(1.0, self.tiempo / cfg.SEGUNDOS_CARGA_SIMULADA)
        return t * t * (3 - 2 * t)  # arranca y termina suave

    def _lista(self):
        return self.tiempo >= cfg.SEGUNDOS_CARGA_SIMULADA

    def _cambiar_consejo(self, paso):
        self.indice = (self.indice + paso) % len(CONSEJOS)

    def _continuar(self):
        if self._lista():
            self.siguiente = "menu"

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_anterior.collidepoint(evento.pos):
                self._cambiar_consejo(-1)
            elif self.btn_siguiente.collidepoint(evento.pos):
                self._cambiar_consejo(1)
            elif self.btn_continuar.collidepoint(evento.pos):
                self._continuar()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                self._cambiar_consejo(-1)
            elif evento.key == pygame.K_RIGHT:
                self._cambiar_consejo(1)
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._continuar()

    def actualizar(self, dt):
        self.tiempo += dt

    def _boton(self, etiqueta, rect):
        encima = rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(self.pantalla, COLOR_CAFE_CLARO if encima else COLOR_CAFE, rect)
        pygame.draw.rect(self.pantalla, COLOR_CREMA, rect, 2)
        texto = self.fuente_boton.render(etiqueta, True, (255, 255, 255))
        self.pantalla.blit(texto, texto.get_rect(center=rect.center))

    def dibujar(self):
        p = self.pantalla
        centro = cfg.ANCHO_VENTANA // 2
        p.fill(COLOR_FONDO)

        dibujar_texto_retro(
            p,
            "EL RESPIRO DE LA SIERRA COCHIMÍ",
            self.fuente_titulo,
            COLOR_CREMA,
            centro=(centro, 90),
            offset_sombra=(3, 3),
            con_borde=True,
        )

        # Caja del consejo
        pygame.draw.rect(p, COLOR_CREMA, self.caja)
        pygame.draw.rect(p, COLOR_CAFE_OSCURO, self.caja, 3)
        etiqueta = self.fuente_chica.render(
            f"Consejo {self.indice + 1}/{len(CONSEJOS)}", True, COLOR_CAFE_OSCURO
        )
        p.blit(etiqueta, (self.caja.x + 18, self.caja.y + 12))

        lineas = partir_texto(CONSEJOS[self.indice], self.fuente_consejo, self.caja.width - 60)
        alto_linea = self.fuente_consejo.get_linesize()
        y = self.caja.centery - (len(lineas) * alto_linea) // 2 + 8
        for linea in lineas:
            texto = self.fuente_consejo.render(linea, True, COLOR_TEXTO)
            p.blit(texto, texto.get_rect(center=(self.caja.centerx, y + alto_linea // 2)))
            y += alto_linea

        self._boton("< Anterior", self.btn_anterior)
        self._boton("Siguiente >", self.btn_siguiente)

        # Barra de progreso
        pygame.draw.rect(p, (70, 60, 52), self.barra)
        relleno = self.barra.copy()
        relleno.width = int(self.barra.width * self._progreso())
        pygame.draw.rect(p, COLOR_CAFE, relleno)
        pygame.draw.rect(p, COLOR_CREMA, self.barra, 2)

        if self._lista():
            self._boton("Continuar", self.btn_continuar)
        else:
            porcentaje = int(self._progreso() * 100)
            texto = self.fuente_boton.render(f"Cargando... {porcentaje}%", True, COLOR_CREMA)
            p.blit(texto, texto.get_rect(center=(centro, 500)))