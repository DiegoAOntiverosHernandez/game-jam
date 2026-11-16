"""Punto de entrada de El Último Aguaje: Legado Cochimí."""
import ctypes
import sys

import pygame

from codigo import configuracion as cfg
from codigo.escenas.escena_juego import EscenaJuego
from codigo.gestor_recursos import detener_todo_audio


def activar_consciencia_dpi():
    """Evita que Windows escale la ventana y se vea borrosa."""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    activar_consciencia_dpi()
    pygame.init()
    pantalla = pygame.display.set_mode(
        (cfg.ANCHO_VENTANA, cfg.ALTO_VENTANA), pygame.SCALED
    )
    pygame.display.set_caption(cfg.TITULO_VENTANA)
    reloj = pygame.time.Clock()

    escena = EscenaJuego(pantalla)
    ejecutando = True
    while ejecutando:
        dt = reloj.tick(cfg.FPS) / 1000  # segundos reales del fotograma
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            else:
                escena.manejar_evento(evento)
        escena.actualizar(dt)
        escena.dibujar()
        pygame.display.flip()

    detener_todo_audio()
    pygame.quit()


if __name__ == "__main__":
    main()