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
TAMANO_CASA_CAMPANA = (64, 64)         # 2x2 casillas

# --- Tiempo -------------------------------------------------------------------
SEGUNDOS_POR_DIA = 60                  # a velocidad x1 equivale a 60 s reales
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

# --- Necesidades y consumo ----------------------------------------------------
SEGUNDOS_CICLO_CONSUMO = 30            # cada ciclo llega el hambre
SEGUNDOS_DESCANSO_COMER = 10
SEGUNDOS_LIMITE_HAMBRE = 12            # tiempo para atender el hambre antes de morir

CONSUMO_INACTIVO = {"comida": 1, "agua": 2}      # por ciclo
CONSUMO_TRABAJANDO = {"comida": 2, "agua": 3}    # por ciclo

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