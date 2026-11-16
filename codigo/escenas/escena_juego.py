"""Escena principal del juego."""
import random

import pygame

from codigo import configuracion as cfg
from codigo.ecs.componentes import (
    ESTADO_HAMBRIENTO,
    ESTADO_MUERTO,
    ComponenteAlmacen,
    ComponenteAnimal,
    ComponenteNecesidades,
    ComponenteNodoRecurso,
    ComponenteObstaculo,
    ComponenteReloj,
    ComponenteRenderizado,
    ComponenteRutinaTrabajador,
    ComponenteSeleccionable,
    ComponenteTransformacion,
)
from codigo.ecs.mundo import Mundo
from codigo.ecs.sistemas import (
    SistemaCicloDia,
    SistemaEntradaYSeleccion,
    SistemaInterfaz,
    SistemaNecesidades,
    SistemaRenderizado,
    SistemaRutinaTrabajador,
    SistemaRegeneracionRecursos,
    SistemaAnimales,
    crear_venado,
)
from codigo.gestor_recursos import (
    iniciar_ambiente,
    iniciar_ost,
    reproducir_fin_del_juego,
    reproducir_sonido,
)

# Matriz de 18 filas x 24 columnas (cada posición es una casilla de 32x32 px)
# Códigos en configuracion.py:
#   1=Base, 4=PNJ inicial, 5=Hierba, 6=Alicoche, 7=Cactus, 8=Palma, 9=Palo blanco, 11=Piedra
# Los aguajes (2), cardones (3) y venados (10) ya NO se leen de aquí:
# se colocan al azar en cada partida (ver _cargar_mapa_desde_matriz).
MAPA_INICIAL = [
    # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 0
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 9, 0],  # fila 1
    [ 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 2
    [ 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 3
    [ 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 4
    [ 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 5
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 6
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 7
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 8 (Base en col 11)
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 9
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0],  # fila 10
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 11
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 12 (PNJ en col 11 y 13)
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0,11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 13
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 14
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 15
    [ 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 16
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fila 17
]

class EscenaJuego:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.siguiente = None
        self.mundo = Mundo()
        self.sistema_entrada = SistemaEntradaYSeleccion()
        self.sistema_renderizado = SistemaRenderizado()
        self.sistema_interfaz = SistemaInterfaz()

        self.mundo.agregar_sistema(SistemaRutinaTrabajador())
        self.mundo.agregar_sistema(SistemaNecesidades())
        self.mundo.agregar_sistema(SistemaCicloDia())
        self.mundo.agregar_sistema(SistemaRegeneracionRecursos())
        self.mundo.agregar_sistema(SistemaAnimales())

        self.reloj = ComponenteReloj(
            segundos_dia=cfg.HORA_INICIAL / cfg.HORAS_POR_DIA * cfg.SEGUNDOS_POR_DIA
        )
        self.mundo.crear_entidad(self.reloj)

        self.filtro_noche = pygame.Surface((cfg.ANCHO_MAPA, cfg.ALTO_MAPA))
        self.filtro_noche.fill(cfg.COLOR_NOCHE)

        self.temporizador_pajaros = 0.0
        self.tiempo_juego_real = 0.0
        self.ost_iniciado = False
        self.fin_del_juego = False
        self.mensaje_fin_juego = ""

        self.id_campamento = None
        self._cargar_mapa_desde_matriz()
        iniciar_ambiente()

    def _cargar_mapa_desde_matriz(self):
        t = cfg.TAMANO_CASILLA
        posiciones_pnj = []
        ocupados = []  # rectángulos ya usados, para que nada se sobreponga
        cantidad = {"aguaje": 0, "cardon": 0, "venado": 0}

        # 1) Elementos fijos (Casa, decoración, PNJ). Aguajes, cardones y
        #    venados solo se cuentan: su lugar se sortea en el paso 2.
        for fila, valores_fila in enumerate(MAPA_INICIAL):
            for columna, celda in enumerate(valores_fila):
                x, y = columna * t, fila * t
                if celda == cfg.CASILLA_BASE:
                    self.id_campamento = self.mundo.crear_entidad(
                        ComponenteTransformacion(x, y),
                        ComponenteRenderizado(
                            *cfg.TAMANO_CASA_CAMPANA,
                            cfg.COLOR_CAMPAMENTO,
                            sprite="base/Base_nivel_nada.png",
                        ),
                        ComponenteAlmacen(
                            cfg.RESERVA_INICIAL_AGUA, cfg.RESERVA_INICIAL_COMIDA
                        ),
                    )
                    ocupados.append(pygame.Rect(x, y, *cfg.TAMANO_CASA_CAMPANA))
                elif celda == cfg.CASILLA_AGUAJE:
                    cantidad["aguaje"] += 1
                elif celda == cfg.CASILLA_CARDON:
                    cantidad["cardon"] += 1
                elif celda == cfg.CASILLA_VENADO:
                    cantidad["venado"] += 1
                elif celda in cfg.SPRITES_DECORACION:
                    ruta_sprite, (ancho, alto) = cfg.SPRITES_DECORACION[celda]
                    componentes_deco = [
                        ComponenteTransformacion(x, (fila + 1) * t - alto),
                        ComponenteRenderizado(
                            ancho, alto, cfg.COLOR_DECORACION, sprite=ruta_sprite
                        ),
                    ]
                    if celda == cfg.CASILLA_PIEDRA:
                        componentes_deco.append(ComponenteObstaculo())
                    self.mundo.crear_entidad(*componentes_deco)
                    ocupados.append(pygame.Rect(x, (fila + 1) * t - alto, ancho, alto))
                elif celda == cfg.CASILLA_PNJ:
                    posiciones_pnj.append((x, y))
                    ocupados.append(pygame.Rect(x, y, *cfg.TAMANO_SPRITE_PNJ))

        # 2) Aguajes, cardones y venados en lugares al azar, sin sobreponerse
        for _ in range(random.randint(cfg.AGUAJES_MINIMO, cfg.AGUAJES_MAXIMO)):
            lugar = self._lugar_libre(t, t, ocupados)
            if lugar is not None:
                self.mundo.crear_entidad(
                    ComponenteTransformacion(*lugar),
                    ComponenteRenderizado(t, t, cfg.COLOR_AGUAJE),
                    ComponenteNodoRecurso("agua", cfg.AGUAJE_MAXIMO, cfg.AGUAJE_MAXIMO),
                )

        ancho_cardon, alto_cardon = cfg.TAMANO_CARDON
        for _ in range(random.randint(cfg.CARDONES_MINIMO, cfg.CARDONES_MAXIMO)):
            lugar = self._lugar_libre(ancho_cardon, alto_cardon, ocupados)
            if lugar is not None:
                self.mundo.crear_entidad(
                    ComponenteTransformacion(*lugar),
                    ComponenteRenderizado(
                        ancho_cardon,
                        alto_cardon,
                        cfg.COLOR_CARDON,
                        sprite="Vegetacion/Planta de recolecion/Arbol_de_pitaya_lleno_de_7_a_10.png",
                    ),
                    ComponenteNodoRecurso("comida", cfg.CARDON_MAXIMO, cfg.CARDON_MAXIMO),
                )

        for _ in range(cfg.VENADOS_INICIALES):
            lugar = self._lugar_libre(t, t, ocupados)
            if lugar is not None:
                crear_venado(self.mundo, *lugar)

        # 3) Los PNJ iniciales se crean al final para dibujarse encima
        for x, y in posiciones_pnj:
            self._crear_cochimi(x, y)

    def _lugar_libre(self, ancho, alto, ocupados, intentos=300):
        """Busca un rectángulo libre dentro del mapa. Devuelve (x, y) o None."""
        t = cfg.TAMANO_CASILLA
        margen = t // 2  # separación mínima entre objetos
        limite = pygame.Rect(0, 0, cfg.ANCHO_MAPA, cfg.ALTO_MAPA)
        for _ in range(intentos):
            columna = random.randint(0, cfg.COLUMNAS_MAPA - 1)
            fila = random.randint(0, cfg.FILAS_MAPA - 1)
            # Los objetos altos se anclan por la base, igual que en la matriz
            rect = pygame.Rect(columna * t, (fila + 1) * t - alto, ancho, alto)
            if not limite.contains(rect):
                continue
            if rect.inflate(margen * 2, margen * 2).collidelist(ocupados) != -1:
                continue
            ocupados.append(rect)
            return rect.x, rect.y
        print("[mapa] No se encontró lugar libre para un objeto")
        return None

    def _crear_cochimi(self, x, y):
        genero = random.choice(("h", "m"))
        self.mundo.crear_entidad(
            ComponenteTransformacion(x, y, cfg.PNJ_VELOCIDAD),
            ComponenteRenderizado(*cfg.TAMANO_SPRITE_PNJ, cfg.COLOR_COCHIMI),
            ComponenteSeleccionable(),
            ComponenteRutinaTrabajador(genero=genero),
            ComponenteNecesidades(
                casa=self.id_campamento,
                segundos_ciclo=random.uniform(0, cfg.SEGUNDOS_CICLO_CONSUMO),
            ),
        )

    def hay_hambre(self):
        return any(
            rutina.estado == ESTADO_HAMBRIENTO
            for _, (rutina,) in self.mundo.entidades_con(ComponenteRutinaTrabajador)
        )

    def pnj_vivos(self):
        return sum(
            1
            for _, (rutina,) in self.mundo.entidades_con(ComponenteRutinaTrabajador)
            if rutina.estado != ESTADO_MUERTO
        )

    def costo_pnj_comida(self):
        adicionales = max(0, self.pnj_vivos() - cfg.PNJ_INICIALES)
        return cfg.COSTO_PNJ_PRIMERO + cfg.COSTO_PNJ_INCREMENTO * adicionales

    def costo_pnj_agua(self):
        adicionales = max(0, self.pnj_vivos() - cfg.PNJ_INICIALES)
        return cfg.COSTO_PNJ_AGUA_PRIMERO + cfg.COSTO_PNJ_INCREMENTO * adicionales

    def puede_crear_pnj(self):
        almacen = self.mundo.obtener(self.id_campamento, ComponenteAlmacen)
        return (
            self.pnj_vivos() < cfg.PNJ_MAXIMOS
            and almacen.comida >= self.costo_pnj_comida()
            and almacen.agua >= self.costo_pnj_agua()
        )

    def crear_pnj_nuevo(self):
        if not self.puede_crear_pnj():
            return
        almacen = self.mundo.obtener(self.id_campamento, ComponenteAlmacen)
        almacen.comida -= self.costo_pnj_comida()
        almacen.agua -= self.costo_pnj_agua()
        casa = self.mundo.obtener(self.id_campamento, ComponenteTransformacion)
        ancho_casa, alto_casa = cfg.TAMANO_CASA_CAMPANA
        x = casa.x + (ancho_casa - cfg.TAMANO_SPRITE_PNJ[0]) / 2 + random.uniform(-20, 20)
        y = casa.y + alto_casa + 4
        self._crear_cochimi(x, y)
        reproducir_sonido("sonidos ambientales/sonido_de_apericion_de_nuevo_aldeano.mp3")

    def _activar_fin_del_juego(self, mensaje):
        if self.fin_del_juego:
            return
        self.fin_del_juego = True
        self.mensaje_fin_juego = mensaje
        reproducir_fin_del_juego()

    def manejar_evento(self, evento):
        if self.sistema_interfaz.manejar_evento(self, evento):
            return
        self.sistema_entrada.manejar_evento(self.mundo, evento)

    def actualizar(self, dt):
        if self.fin_del_juego or self.sistema_interfaz.pausado:
            return

        if self.hay_hambre():
            self.reloj.velocidad = 1

        dt_juego = dt * self.reloj.velocidad
        self.tiempo_juego_real += dt_juego
        if not self.ost_iniciado and self.tiempo_juego_real >= cfg.SEGUNDOS_INICIO_OST:
            self.ost_iniciado = True
            iniciar_ost()

        self.temporizador_pajaros += dt
        if self.temporizador_pajaros >= cfg.SEGUNDOS_PAJAROS_FONDO:
            self.temporizador_pajaros -= cfg.SEGUNDOS_PAJAROS_FONDO
            reproducir_sonido("sonidos ambientales/pajaros_fondo.WAV", categoria="ambiente")

        self.mundo.actualizar(dt_juego)

        # Actualizar contadores de escasez en el almacén y verificar condiciones de derrota
        almacen = self.mundo.obtener(self.id_campamento, ComponenteAlmacen)
        if almacen is not None:
            if almacen.agua <= 0:
                almacen.segundos_sin_agua += dt_juego
            else:
                almacen.segundos_sin_agua = 0.0

            if almacen.agua <= 0 and almacen.comida <= 0:
                almacen.segundos_sin_recursos += dt_juego
            else:
                almacen.segundos_sin_recursos = 0.0

            if (
                almacen.segundos_sin_recursos
                >= cfg.DIAS_TOLERANCIA_SIN_RECURSOS * cfg.SEGUNDOS_POR_DIA
            ):
                self._activar_fin_del_juego(
                    "No lograste recolectar alimentos y no sobreviviste"
                )
                return

        if self.pnj_vivos() <= 0:
            self._activar_fin_del_juego("No sobreviviste, has fallado como líder")

    def dibujar(self):
        self.pantalla.fill(cfg.COLOR_PANEL)

        mapa = pygame.Rect(0, 0, cfg.ANCHO_MAPA, cfg.ALTO_MAPA)
        pygame.draw.rect(self.pantalla, cfg.COLOR_SUELO, mapa)
        for columna in range(cfg.COLUMNAS_MAPA + 1):
            x = columna * cfg.TAMANO_CASILLA
            pygame.draw.line(self.pantalla, cfg.COLOR_LINEA, (x, 0), (x, cfg.ALTO_MAPA))
        for fila in range(cfg.FILAS_MAPA + 1):
            y = fila * cfg.TAMANO_CASILLA
            pygame.draw.line(self.pantalla, cfg.COLOR_LINEA, (0, y), (cfg.ANCHO_MAPA, y))

        self.sistema_renderizado.dibujar(self.mundo, self.pantalla)

        alpha = int(self._oscuridad() * cfg.NOCHE_ALPHA_MAXIMA)
        if alpha > 0:
            self.filtro_noche.set_alpha(alpha)
            self.pantalla.blit(self.filtro_noche, (0, 0))

        self.sistema_interfaz.dibujar(self, self.pantalla)

    def _oscuridad(self):
        hora = self.reloj.segundos_dia / cfg.SEGUNDOS_POR_DIA * cfg.HORAS_POR_DIA

        def suavizar(t):
            t = max(0.0, min(1.0, t))
            return t * t * (3 - 2 * t)

        if hora < cfg.HORA_AMANECER_INICIO:
            return 1.0
        if hora < cfg.HORA_DIA_PLENO:
            duracion = cfg.HORA_DIA_PLENO - cfg.HORA_AMANECER_INICIO
            return 1.0 - suavizar((hora - cfg.HORA_AMANECER_INICIO) / duracion)
        if hora < cfg.HORA_ATARDECER_INICIO:
            return 0.0
        if hora < cfg.HORA_NOCHE_PLENA:
            duracion = cfg.HORA_NOCHE_PLENA - cfg.HORA_ATARDECER_INICIO
            return suavizar((hora - cfg.HORA_ATARDECER_INICIO) / duracion)
        return 1.0
