# Configuración de la simulación

# Pantalla
WIDTH = 1200
HEIGHT = 700
FPS = 60

# Boids / Zombies
INITIAL_BOIDS = 18
MAX_BOIDS     = 60
BOID_SIZE = 6
MAX_SPEED = 3.2
MAX_FORCE = 0.08

# Percepción (pixeles)
NEIGHBOR_RADIUS = 55.0
SEPARATION_RADIUS = 22.0

# Pesos de comportamiento (patrulla)
WEIGHT_SEPARATION = 1.6
WEIGHT_ALIGNMENT  = 1.0
WEIGHT_COHESION   = 0.9

# Caza / Detección
DETECTION_RADIUS = 160.0    # radio base
WEIGHT_SEEK      = 1.35
CROUCH_MULT      = 0.55     # al agacharte, reduces tu ruido/visibilidad
SPRINT_MULT      = 1.25     # si corres (Shift), eres más visible

# Jugador
PLAYER_SPEED = 4.2
PLAYER_SPEED_SPRINT = 6.0
PLAYER_SIZE  = 8

# Apariencia
BACKGROUND_COLOR = (18, 18, 22)
BOID_COLOR = (230, 230, 230)
PLAYER_COLOR = (120, 200, 255)
PLAYER_CROUCH_COLOR = (90, 180, 240)

# Colisiones / Game Over
PLAYER_HIT_RADIUS = PLAYER_SIZE + 6
GAME_OVER_PAUSE_MS = 1200

# Spawning (nuevos zombis con el tiempo)
AUTO_SPAWN = True
SPAWN_INTERVAL_MS = 1400
SPAWN_EDGE_ONLY = True

# Obstáculos (se definen en main para poder dibujarlos fácil)
OBSTACLE_COLOR = (60, 60, 80)

# Alerta de horda
ALERT_DURATION_MS = 2500   # cuánto dura la alerta global
ALERT_COOLDOWN_MS = 800    # anti-spam entre gritos
ALERT_COLOR = (255, 120, 120)  # color del HUD cuando hay alerta

# Punto seguro / niveles
SAFEZONE_SIZE = (90, 90)
SAFEZONE_COLOR = (120, 230, 160)
SAFEZONE_EDGE_MARGIN = 30
LEVEL_UP_PAUSE_MS = 1200

