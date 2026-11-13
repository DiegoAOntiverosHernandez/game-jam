# Game Jam BCS 2026 — El Último Aguaje: Legado Cochimí *(Título provisional)*

> **Game Jam:** Diseñando juegos para transformar los retos de BCS (2026)  
> **Temáticas:** Protección del ecosistema, Escasez y distribución del agua  
> **Motor / Tecnología:** Python (`pygame-ce`) · Arquitectura **ECS (Entity-Component-System)**

---

## ¿De qué trata el juego?

El jugador lidera un pequeño asentamiento temporal de indígenas **Cochimíes** cerca de la sierra antes de la temporada de sequía extrema en Baja California Sur. El objetivo principal es gestionar la **recolección sustentable** de recursos naturales sin extinguir el ecosistema local:

- **Agua (Aguajes / Tinajas):** Se regenera lentamente (`+1` cada 15s, máx. 10 botes). Si se sobreexplota hasta vaciarse a `0`, el aguaje se agota y tarda **120s** en recuperarse.
- **Pitahayas (Cardones):** Se regenera `+1` cada 25s (máx. 10 frutos). Si se vacía a `0`, sufre un castigo de **120s** de recuperación.
- **Caza (Fauna local):** Se reproduce cada 30s (máx. 12 animales). Si el jugador caza a todos los ejemplares, la especie **se extingue permanentemente**.

La tribu debe almacenar suficientes reservas en la **Casa de Campaña** durante **50 días de preparación** y luego resistir **20 días adicionales de sequía extrema** encerrados en el refugio, conectando el manejo ancestral de los recursos con la crisis hídrica actual en Baja California Sur.

---

## Mecánicas Principales

- **Perspectiva Cenital (Top-Down):** Mapa fijo de `24 × 18 tiles` estilo *WorldBox / RimWorld*.
- **Rutinas Automáticas:** Selecciona un NPC Cochimí, asigna un recurso y la Casa de Campaña para automatizar su ciclo de recolección (hasta 7 NPCs).
- **Gestión de Necesidades:** Los NPCs consumen agua y comida según su estado (`IDLE` o `Trabajando`) y requieren descanso periódico.
- **Control de Tiempo (`x1`, `x2`, `x5`):** Escala base de `1 día = 60s` con botones de aceleración (Fast-Forward).
- **La Gran Sequía (Días 50–70):** Fase cinemática de suspenso donde se bloquean los controles y el reloj se acelera mientras las reservas del almacén se consumen día a día.

---

## Estructura del Proyecto

```text
proyecto-gamejam-bcs/
├── recursos/
│   ├── musica/          # Ambiente desierto, tensión sequía (.ogg)
│   ├── sonido/          # SFX: agua, recolección, alertas (.wav)
│   ├── sprites/         # Sprites y personajes (.png)
│   └── imagenes/        # Fondos, UI, pantallas finales
├── src/
│   ├── config.py        # Constantes (tiempos, costos, FPS)
│   ├── asset_manager.py # Cargador seguro con fallback visual
│   ├── ecs/
│   │   ├── world.py     # Gestor de entidades y sistemas
│   │   ├── components.py# Clases de datos (Dataclasses)
│   │   └── systems.py   # Lógica principal procesada por frame
│   └── scenes/
│       ├── game_scene.py
│       └── end_scene.py
├── main.py              # Punto de entrada
└── README.md
```
