"""Punto de entrada de El Último Aguaje: Legado Cochimí."""
import ctypes
import sys

import pygame

from codigo import configuracion as cfg
from codigo.escenas.escena_carga import EscenaCarga
from codigo.escenas.escena_final import EscenaFinal
from codigo.escenas.escena_juego import EscenaJuego
from codigo.escenas.escena_menu import EscenaMenu
from codigo.gestor_recursos import cargar_imagen, detener_todo_audio

# Contrato de una escena: métodos manejar_evento(evento), actualizar(dt) y
# dibujar(), más un atributo `siguiente`: None mientras sigue activa, o el nombre
# de la escena a la que hay que pasar. Para sumar una escena solo se agrega aquí.
ESCENA_INICIAL = "carga"
ESCENAS = {
    "carga": EscenaCarga,
    "menu": EscenaMenu,
    "juego": EscenaJuego,
    "final": EscenaFinal,
}


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
    logo = cargar_imagen("Logo.png", carpeta="imagenes")
    escala_icono = min(64 / logo.get_width(), 64 / logo.get_height())
    tamano_icono = (
        max(1, int(logo.get_width() * escala_icono)),
        max(1, int(logo.get_height() * escala_icono)),
    )
    imagen_icono = pygame.transform.smoothscale(logo, tamano_icono)
    icono = pygame.Surface((64, 64), pygame.SRCALPHA)
    icono.blit(
        imagen_icono,
        ((64 - tamano_icono[0]) // 2, (64 - tamano_icono[1]) // 2),
    )
    pygame.display.set_icon(icono)
    pygame.display.set_caption(cfg.TITULO_VENTANA)
    reloj = pygame.time.Clock()

    escena = ESCENAS[ESCENA_INICIAL](pantalla)
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

        nombre = getattr(escena, "siguiente", None)
        if nombre is not None:
            if nombre == "salir":
                ejecutando = False
            elif nombre in ESCENAS:
                detener_todo_audio()  # cada escena arranca su propio sonido
                params = getattr(escena, "params_siguiente", None)
                fabrica = ESCENAS[nombre]
                if params:
                    escena = fabrica(pantalla, **params)
                else:
                    escena = fabrica(pantalla)
            else:
                print(f"[main] Escena desconocida: {nombre}")
                escena.siguiente = None

    detener_todo_audio(cerrar_mixer=True)
    pygame.quit()


if __name__ == "__main__":
    main()