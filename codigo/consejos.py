"""Consejos de la pantalla de carga, en el orden en que se muestran."""
from codigo import configuracion as cfg

CONSEJOS = [
    "Haz clic en un cochimí, luego en un recurso y luego en la Casa de Campaña "
    "para que repita el trabajo solo. Clic derecho quita la selección.",
    f"Atiende el ícono de hambre antes de {cfg.SEGUNDOS_LIMITE_HAMBRE} segundos "
    "o el cochimí morirá.",
    "El agua que se infiltra en la sierra puede tardar entre 5 y 15 años en llegar "
    "al acuífero, hay que cuidarla.",
    f"Si un aguaje llega a 0, tarda {cfg.AGUAJE_SEGUNDOS_RECUPERACION} segundos en "
    "recuperarse. Cambia de aguaje antes de vaciarlo.",
    "Los antiguos pueblos de la península se asentaban cerca de los aguajes y "
    "crearon rituales para vivir con poca agua y alimento.",
    "Más cochimíes no significan más agua: cada uno consume reservas. Crea solo los "
    "que puedas sostener.",
    "Para los cochimíes, la cosecha de la pitahaya era motivo de fiesta: la "
    "celebración de Meyibó.",
    f"Si quedan menos de {cfg.VENADOS_MINIMO_PARA_REPRODUCIRSE} venados, la especie "
    "ya no se recupera. Caza con cuidado.",
    "Un cochimí sentado es un cochimí sin trabajo.",
    "Cuida lo que tienes: un recurso que se agota por completo tarda mucho más en "
    "volver.",
    f"Pierdes si no queda ningún cochimí y no tienes {cfg.COSTO_PNJ_PRIMERO} de "
    "comida para crear otro. En la sequía, pierdes si el agua o la comida llegan a 0.",
    f"El día {cfg.DIAS_PREPARACION} pierdes el control. Llega con las reservas "
    "llenas para sobrevivir a la sequía.",
]