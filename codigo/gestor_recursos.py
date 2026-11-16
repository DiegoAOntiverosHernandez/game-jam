"""Gestor de recursos: carga imágenes de forma segura.

- Si falta un archivo, devuelve un cuadro de color y el juego sigue funcionando.
- Guarda en memoria lo ya cargado para no leer el disco en cada fotograma.
- Funciona igual en desarrollo y dentro del ejecutable de PyInstaller.
"""
import os
import sys
import threading

import pygame

_cache = {}
_cache_sonidos = {}
_faltantes = set()  # para avisar una sola vez por archivo

# Niveles de volumen del usuario (0 a 100)
VOLUMENES = {
    "general": 100,
    "efectos": 100,
    "voces": 100,
    "ambiente": 80,
    "musica": 85,
}

# Factores de mezcla base para que la música y el ambiente nunca opaquen las voces ni efectos
_FACTOR_BASE = {
    "efectos": 1.0,
    "voces": 1.0,
    "ambiente": 0.55,
    "musica": 0.60,
}


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


def _asegurar_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        pygame.mixer.set_reserved(2)  # Canal 0: voces, Canal 1: OST (08 Party.mp3)


def volumen_efectivo(categoria):
    general = VOLUMENES.get("general", 100) / 100.0
    cat = VOLUMENES.get(categoria, 100) / 100.0
    base = _FACTOR_BASE.get(categoria, 1.0)
    return max(0.0, min(1.0, general * cat * base))


def actualizar_volumenes():
    """Actualiza en tiempo real el volumen de los canales activos y del ambiente."""
    if not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.music.set_volume(volumen_efectivo("ambiente"))
        pygame.mixer.Channel(0).set_volume(volumen_efectivo("voces"))
        pygame.mixer.Channel(1).set_volume(volumen_efectivo("musica"))
    except pygame.error:
        pass


def cargar_sonido(nombre, carpeta="sonidos"):
    """Carga un archivo de audio (.mp3, .wav, .ogg) de forma segura."""
    clave = (carpeta, nombre)
    if clave in _cache_sonidos:
        return _cache_sonidos[clave]

    ruta = ruta_recurso(carpeta, nombre)
    sonido = None
    try:
        _asegurar_mixer()
        sonido = pygame.mixer.Sound(ruta)
    except (pygame.error, FileNotFoundError):
        if ruta not in _faltantes:
            _faltantes.add(ruta)
            print(f"[gestor_recursos] No se pudo cargar sonido: {ruta}")

    _cache_sonidos[clave] = sonido
    return sonido


def reproducir_sonido(nombre, carpeta="sonidos", canal_voz=False, categoria=None):
    """Reproduce un sonido aplicando el volumen de su categoría."""
    sonido = cargar_sonido(nombre, carpeta)
    if sonido is None:
        return
    if categoria is None:
        categoria = "voces" if canal_voz else "efectos"
    vol = volumen_efectivo(categoria)
    try:
        if canal_voz:
            canal = pygame.mixer.Channel(0)
            sonido.set_volume(1.0)
            canal.set_volume(vol)
            canal.play(sonido)
        else:
            sonido.set_volume(vol)
            sonido.play()
    except pygame.error:
        pass


def iniciar_ambiente():
    """Inicia ambiental.mp3 en bucle continuo y precarga el OST en segundo plano."""
    try:
        _asegurar_mixer()
        ruta_amb = ruta_recurso("sonidos", "sonidos ambientales/ambiental.mp3")
        pygame.mixer.music.load(ruta_amb)
        pygame.mixer.music.set_volume(volumen_efectivo("ambiente"))
        pygame.mixer.music.play(loops=-1)
        threading.Thread(
            target=lambda: cargar_sonido("08 Party.mp3", carpeta="musica"),
            daemon=True,
        ).start()
    except pygame.error as e:
        print(f"[gestor_recursos] No se pudo iniciar audio ambiental: {e}")


def iniciar_ost():
    """Inicia 08 Party.mp3 en el canal reservado 1 sin detener el sonido ambiental."""
    sonido = cargar_sonido("08 Party.mp3", carpeta="musica")
    if sonido is None:
        return
    try:
        _asegurar_mixer()
        canal = pygame.mixer.Channel(1)
        if not canal.get_busy():
            sonido.set_volume(1.0)
            canal.set_volume(volumen_efectivo("musica"))
            canal.play(sonido, loops=-1)
    except pygame.error:
        pass


def reproducir_fin_del_juego():
    """Detiene todo sonido ambiental y música, y reproduce fin_del_juego.mp3."""
    try:
        _asegurar_mixer()
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        reproducir_sonido("fin_del_juego.mp3", carpeta="sonidos", categoria="musica")
    except pygame.error:
        pass


def detener_todo_audio(cerrar_mixer=False):
    """Detiene todos los canales y la música; cierra el mixer al salir del programa."""
    try:
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            if cerrar_mixer:
                _cache_sonidos.clear()
                pygame.mixer.quit()
    except pygame.error:
        pass
