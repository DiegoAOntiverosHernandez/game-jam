"""Constantes de El Último Aguaje: Legado Cochimí.

Regla: ningún número fijo en la lógica del juego; todo vive aquí.
Todos los tiempos están en segundos de juego (escalan con el avance rápido).
Los valores de balance son un punto de partida y se afinan jugando.
"""

# --- Ventana y mapa ---------------------------------------------------------
TITULO_VENTANA = "El Último Aguaje: Legado Cochimí"
FPS = 60

TAMANO_CASILLA = 32            # píxeles por casilla
COLUMNAS_MAPA = 24
FILAS_MAPA = 18
ANCHO_MAPA = COLUMNAS_MAPA * TAMANO_CASILLA   # 768
ALTO_MAPA = FILAS_MAPA * TAMANO_CASILLA       # 576
ANCHO_PANEL = 192                             # panel de interfaz a la derecha
ANCHO_VENTANA = ANCHO_MAPA + ANCHO_PANEL      # 960
ALTO_VENTANA = ALTO_MAPA                      # 576

# --- Tamaño de sprites (píxeles) --------------------------------------------
TAMANO_SPRITE_PNJ = (32, 32)           # también existen sprites de 32x64
TAMANO_CASA_CAMPANA = (96, 96)         # 3x3 casillas

# --- Tiempo -------------------------------------------------------------------
SEGUNDOS_POR_DIA = 60                  # a velocidad x1 equivale a 60 s reales
HORAS_POR_DIA = 24
DIAS_PREPARACION = 50
DIAS_SEQUIA = 20
DIAS_TOTALES = DIAS_PREPARACION + DIAS_SEQUIA   # 70

VELOCIDADES = (1, 2, 5)                # botones de avance rápido
VELOCIDAD_SEQUIA = 1.25                # velocidad automática desde el día 50
VELOCIDAD_MAXIMA_SEQUIA = 5            # el botón x5 sigue disponible

# --- Personajes (PNJ) ---------------------------------------------------------
PNJ_INICIALES = 2
PNJ_MAXIMOS = 7                        # vivos al mismo tiempo
PNJ_VELOCIDAD = 64
COSTO_PNJ_PRIMERO = 20                 # de comida
COSTO_PNJ_INCREMENTO = 10              # por cada PNJ adicional
CARGA_POR_VIAJE = 5
SEGUNDOS_POR_UNIDAD_EXTRAIDA = 0.5     # tiempo para sacar 1 unidad de un recurso
SEGUNDOS_POR_UNIDAD_DEPOSITADA = 0.5
SEGUNDOS_INACTIVO_PARA_SENTARSE = 8    # tiempo sin hacer nada antes de sentarse

# --- Necesidades y consumo ----------------------------------------------------
SEGUNDOS_CICLO_CONSUMO = 30            # cada ciclo llega el hambre
SEGUNDOS_DESCANSO_COMER = 10
SEGUNDOS_LIMITE_HAMBRE = 12            # tiempo para atender el hambre antes de morir
TAMANO_ICONO_HAMBRE = 22               # lado del cuadro blanco del ícono (píxeles)
SEGUNDOS_PAJAROS_FONDO = 45            # cada cuánto suenan los pájaros de fondo
SEGUNDOS_INICIO_OST = 25               # segundo real en el que inicia la música (08 Party.mp3)

CONSUMO_INACTIVO = {"comida": 1, "agua": 2}      # por ciclo
CONSUMO_TRABAJANDO = {"comida": 2, "agua": 3}    # por ciclo
SEGUNDOS_CUERPO_VISIBLE = 3            # cuánto se ve el PNJ muerto antes de desaparecer

# --- Reservas de la Casa de Campaña -------------------------------------------
RESERVA_INICIAL_AGUA = 30
RESERVA_INICIAL_COMIDA = 30
RESERVA_MAXIMA = 300                   # de cada recurso

# El sprite de la Casa de Campaña depende del menor de los dos niveles
NIVEL_RESERVA_ALTO = 200               # más de 200
NIVEL_RESERVA_MEDIO = 100              # de 100 a 200; de 1 a 99 es bajo; 0 es nada

# --- Aguajes ------------------------------------------------------------------
CANTIDAD_AGUAJES = 3
AGUAJE_MAXIMO = 10                     # botes
AGUAJE_SEGUNDOS_REGENERACION = 15      # +1 bote cada 15 s
AGUAJE_SEGUNDOS_RECUPERACION = 120     # si se vacía a 0
AGUAJE_BOTES_RECUPERADOS = 5           # al terminar la recuperación

# --- Cardones -----------------------------------------------------------------
CANTIDAD_CARDONES = 6
CARDON_MAXIMO = 10                     # pitahayas
CARDON_SEGUNDOS_REGENERACION = 25      # +1 pitahaya cada 25 s
CARDON_SEGUNDOS_RECUPERACION = 120     # si se vacía a 0
CARDON_PITAHAYAS_RECUPERADAS = 3       # al terminar la recuperación

# Sprite del cardón según pitahayas restantes (mínimo para cada nivel)
CARDON_UMBRAL_LLENO = 7                # 7 a 10
CARDON_UMBRAL_MEDIO = 4                # 4 a 6
CARDON_UMBRAL_BAJO = 2                 # 2 a 3
CARDON_UMBRAL_MUY_BAJO = 1             # 1; con 0 se muestra agotado

# --- Fauna --------------------------------------------------------------------
FAUNA_INICIAL = 2
FAUNA_MAXIMA = 12
FAUNA_SEGUNDOS_REPRODUCCION = 30

# --- Ciclo de luz (día / noche) ---------------------------------------------
HORA_INICIAL = 8                       # el juego arranca a las 08:00
HORA_AMANECER_INICIO = 5               # empieza a aclarar
HORA_DIA_PLENO = 8                     # ya es de día completo
HORA_ATARDECER_INICIO = 18             # empieza a oscurecer
HORA_NOCHE_PLENA = 21                  # noche cerrada
COLOR_NOCHE = (10, 20, 60)             # azul oscuro
NOCHE_ALPHA_MAXIMA = 150               # opacidad máxima de la noche (0 a 255)

# --- Colores de mapa e interfaz ----------------------------------------------
COLOR_PANEL = (40, 36, 32)
COLOR_SUELO = (194, 170, 120)
COLOR_LINEA = (180, 156, 108)
COLOR_CAMPAMENTO = (120, 80, 50)
COLOR_COCHIMI = (200, 60, 60)
COLOR_AGUAJE = (60, 120, 200)
COLOR_CARDON = (60, 140, 70)
COLOR_DECORACION = (90, 120, 60)

# --- Códigos de la matriz del mapa (18 filas x 24 columnas) ------------------
CASILLA_BASE = 1         # Casa de Campaña (Base_nivel_nada.png)
CASILLA_AGUAJE = 2       # Aguaje (agua)
CASILLA_CARDON = 3       # Cardón / Árbol de pitaya (comida)
CASILLA_PNJ = 4          # Cochimí inicial
CASILLA_HIERBA = 5       # Decoración: hierba.png (32x32)
CASILLA_ALICOCHE = 6     # Decoración: alicoche.png (32x32)
CASILLA_CACTUS = 7       # Decoración: cactus.png (32x64)
CASILLA_PALMA = 8        # Decoración: Palma.png (32x64)
CASILLA_PALO_BLANCO = 9  # Decoración: palo_blanco.png (32x64)
CASILLA_VENADO = 10      # Animal: venado_de_frente.png (32x32)

SPRITES_DECORACION = {
    CASILLA_HIERBA: ("Vegetacion/Decoracion/hierba.png", (32, 32)),
    CASILLA_ALICOCHE: ("Vegetacion/Decoracion/alicoche.png", (32, 32)),
    CASILLA_CACTUS: ("Vegetacion/Decoracion/cactus.png", (32, 64)),
    CASILLA_PALMA: ("Vegetacion/Decoracion/Palma.png", (32, 64)),
    CASILLA_PALO_BLANCO: ("Vegetacion/Decoracion/palo_blanco.png", (32, 64)),
}
