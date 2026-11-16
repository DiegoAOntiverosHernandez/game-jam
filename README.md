# Competencia de Videojuegos BCS 2026 — El Respiro de la Sierra cochimie

> **Competencia:** Diseñando juegos para transformar los retos de BCS (2026)  
> **Temáticas:** Protección del ecosistema, escasez y distribución del agua  
> **Motor / Tecnología:** Python (`pygame-ce`) · Arquitectura **ECS (Entidad-Componente-Sistema)**

---

## ¿De qué trata el juego?

El jugador lidera un pequeño asentamiento temporal de indígenas **cochimíes** cerca de la sierra antes de la temporada de sequía extrema en Baja California Sur. El objetivo principal es gestionar la **recolección sustentable** de recursos naturales sin extinguir el ecosistema local:

- **Agua (aguajes):** Se regenera lentamente (`+1` cada 15 s, máx. 10 botes). Si se sobreexplota hasta vaciarse a `0`, el aguaje se agota y tarda **120 s** en recuperar 5 botes.
- **Pitahayas (cardones):** Se regeneran `+1` cada 25 s (máx. 10 pitahayas). Si el cardón se vacía a `0`, sufre un castigo de **120 s** para recuperar 3 pitahayas.
- **Caza (fauna local):** Se reproduce cada 30 s (máx. 12 animales). Si el jugador caza a todos los ejemplares, la especie **se extingue permanentemente**.

La tribu debe almacenar suficientes reservas en la **Casa de Campaña** durante **50 días de preparación** y luego resistir **20 días adicionales de sequía extrema** encerrados en ella, conectando el manejo ancestral de los recursos con la crisis hídrica actual en Baja California Sur.

---

## Mecánicas principales

- **Vista cenital:** Mapa fijo de `24 × 18 casillas` (de 32 px) estilo *WorldBox / RimWorld*, con un panel de interfaz a la derecha (ventana de `960 × 576`).
- **Rutinas automáticas:** Selecciona un PNJ cochimí, asígnale un recurso y luego la Casa de Campaña para automatizar su ciclo de recolección (inicias con 2 PNJ y puedes tener hasta 7 vivos).
- **Gestión de necesidades:** Los PNJ consumen agua y comida según su estado (`Inactivo` o `Trabajando`). Cada 30 s les llega el hambre y el jugador debe atenderla con un clic en menos de 12 s, o el PNJ muere.
- **Control de tiempo (`x1`, `x2`, `x5`):** Escala base de `1 día = 60 s` con botones de avance rápido.
- **La Gran Sequía (días 50–70):** Fase cinemática de suspenso donde se bloquean los controles y las reservas de la Casa de Campaña se consumen día a día. Si el agua o la comida llegan a `0`, la tribu perece; si resisten hasta el día 70, sobreviven.

---

## Estructura del proyecto

```text
game-jam/
├── recursos/
│   ├── musica/             # Ambiente de desierto, tensión de sequía (.ogg)
│   ├── sonido/             # Efectos de sonido: agua, recolección, alertas (.wav)
│   ├── sprites/            # Imágenes de personajes (.png)
│   └── imagenes/           # Fondos, interfaz, pantallas finales
├── codigo/
│   ├── configuracion.py    # Constantes (tiempos, costos, cuadros por segundo)
│   ├── gestor_recursos.py  # Cargador seguro con imagen de respaldo
│   ├── ecs/
│   │   ├── mundo.py        # Gestor de entidades y sistemas
│   │   ├── componentes.py  # Clases de datos (dataclasses)
│   │   └── sistemas.py     # Lógica principal procesada por fotograma
│   └── escenas/
│       ├── escena_menu.py
│       ├── escena_juego.py
│       └── escena_final.py
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias (pygame-ce)
└── README.md
```

---
pip install -r requirements.txt
python main.py
```
