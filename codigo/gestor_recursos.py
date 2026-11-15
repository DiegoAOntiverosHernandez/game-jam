"""Gestor de recursos: carga imágenes de forma segura.

- Si falta un archivo, devuelve un cuadro de color y el juego sigue funcionando.
- Guarda en memoria lo ya cargado para no leer el disco en cada fotograma.
- Funciona igual en desarrollo y dentro del ejecutable de PyInstaller.
"""
import os
import sys

import pygame

_cache = {}
_faltantes = set()  # para avisar una sola vez por archivo


def ruta_base():
    """Carpeta raíz del proyecto (o la carpeta temporal del .exe)."""
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ruta_recurso(*partes):
    """Ruta completa dentro de recursos/. Ej: ruta_recurso("sprites", "cactus.png")."""
    return os.path.join(ruta_base(), "recursos", *partes)


def cargar_imagen(nombre, tamano=None, color_respaldo=(255, 0, 255),
                  carpeta="sprites", espejar=False):
    """Carga una imagen PNG.

    nombre: archivo tal como se llama en la carpeta (respeta mayúsculas).
    tamano: (ancho, alto) para escalar; None conserva el tamaño original.
    color_respaldo: color del cuadro que se usa si el archivo no existe.
    carpeta: subcarpeta de recursos/ ("sprites" o "imagenes").
    espejar: voltea la imagen horizontalmente (caminar a la izquierda).
    """
    clave = (carpeta, nombre, tamano, espejar)
    if clave in _cache:
        return _cache[clave]

    ruta = ruta_recurso(carpeta, nombre)
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        if tamano is not None:
            imagen = pygame.transform.scale(imagen, tamano)
    except (pygame.error, FileNotFoundError):
        if ruta not in _faltantes:
            _faltantes.add(ruta)
            print(f"[gestor_recursos] No se pudo cargar: {ruta}")
        imagen = pygame.Surface(tamano or (32, 32))
        imagen.fill(color_respaldo)

    if espejar:
        imagen = pygame.transform.flip(imagen, True, False)

    _cache[clave] = imagen
    return imagen