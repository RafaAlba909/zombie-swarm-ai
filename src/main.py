import pygame as pg
import numpy as np
from .boids import Boid
from . import config as C
import math
import random

# ---------- Colores ----------
PATROL_COLOR = (230, 230, 230)   # boids patrullando
CHASE_COLOR  = (255, 120, 120)   # boids cazando / alerta

# ---------- Dibujo básico ----------
def draw_boid(surface, position, velocity, color, offset=(0,0)):
    ox, oy = offset
    x, y = position[0] + ox, position[1] + oy
    angle = math.atan2(velocity[1], velocity[0] + 1e-6)
    size = C.BOID_SIZE
    p1 = (x + math.cos(angle) * (size * 2), y + math.sin(angle) * (size * 2))
    p2 = (x + math.cos(angle + 2.5) * size, y + math.sin(angle + 2.5) * size)
    p3 = (x + math.cos(angle - 2.5) * size, y + math.sin(angle - 2.5) * size)
    pg.draw.polygon(surface, color, [p1, p2, p3])

def draw_player(surface, position, alive=True, offset=(0,0)):
    ox, oy = offset
    x, y = int(position[0] + ox), int(position[1] + oy)
    color = (200, 60, 60) if not alive else C.PLAYER_COLOR
    pg.draw.circle(surface, color, (x, y), C.PLAYER_SIZE)

def draw_obstacles(surface, obstacles, offset=(0,0)):
    ox, oy = offset
    for r in obstacles:
        rect = pg.Rect(r.x + ox, r.y + oy, r.width, r.height)
        pg.draw.rect(surface, C.OBSTACLE_COLOR, rect, border_radius=6)

# ---------- Fondo tipo campo ----------
def generate_grass_surface(w, h, seed=None):
    if seed is not None:
        random.seed(seed)
    surf = pg.Surface((w, h))
    base = (22, 56, 28)
    surf.fill(base)
    shades = [(26, 64, 34), (30, 72, 38), (24, 60, 30)]
    for _ in range(2200):
        col = random.choice(shades)
        x = random.randrange(0, w)
        y = random.randrange(0, h)
        rw = random.randint(2, 6)
        rh = random.randint(2, 6)
        surf.fill(col, (x, y, rw, rh))
    path_color = (60, 50, 38)
    for _ in range(3):
        px = random.randint(0, w)
        py = random.randint(0, h)
        for i in range(260):
            dx = int(12 * math.sin(i * 0.09 + random.random()))
            dy = int(12 * math.cos(i * 0.09 + random.random()))
            rect = pg.Rect((px + dx) % w, (py + dy) % h, 14, 6)
            surf.fill(path_color, rect)
            px = (px + random.randint(-6, 8)) % w
            py = (py + random.randint(-3, 3)) % h
    return surf

# ---------- Spawning ----------
def rand_edge_pos():
    side = random.choice(['top','bottom','left','right'])
    if side == 'top':
        return np.array([random.uniform(0, C.WIDTH), 0.0], dtype=float)
    if side == 'bottom':
        return np.array([random.uniform(0, C.WIDTH), float(C.HEIGHT)], dtype=float)
    if side == 'left':
        return np.array([0.0, random.uniform(0, C.HEIGHT)], dtype=float)
    return np.array([float(C.WIDTH), random.uniform(0, C.HEIGHT)], dtype=float)

def spawn_boid(near_edges=True):
    if near_edges:
        pos = rand_edge_pos()
    else:
        pos = np.array([random.uniform(0, C.WIDTH), random.uniform(0, C.HEIGHT)], dtype=float)
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(1.0, C.MAX_SPEED)
    vel = np.array([math.cos(angle), math.sin(angle)], dtype=float) * speed
    return Boid(pos, vel)

def init_boids(n):
    return [spawn_boid(near_edges=False) for _ in range(n)]

# ---------- Geometría (LOS contra rectángulos) ----------
def segments_intersect(p, p2, q, q2):
    def ccw(a,b,c):
        return (c[1]-a[1])*(b[0]-a[0]) > (b[1]-a[1])*(c[0]-a[0])
    return (ccw(p,q,q2) != ccw(p2,q,q2)) and (ccw(p,p2,q) != ccw(p,p2,q2))

def segment_intersects_rect(p, q, rect):
    r = rect
    corners = [
        (r.left, r.top), (r.right, r.top),
        (r.right, r.bottom), (r.left, r.bottom)
    ]
    edges = [(corners[i], corners[(i+1) % 4]) for i in range(4)]
    for a, b in edges:
        if segments_intersect(p, q, a, b):
            return True
    if r.collidepoint(p) and r.collidepoint(q):
        return True
    return False

def has_line_of_sight(a_pos, b_pos, obstacles):
    p = (float(a_pos[0]), float(a_pos[1]))
    q = (float(b_pos[0]), float(b_pos[1]))
    for r in obstacles:
        if segment_intersects_rect(p, q, r):
            return False
    return True

# ---------- Utilidades jugador ----------
def clamp_player(pos):
    pos[0] = min(max(0, pos[0]), C.WIDTH)
    pos[1] = min(max(0, pos[1]), C.HEIGHT)
    return pos

# ---------- Obstáculos estilo campo ----------
def build_field_obstacles():
    obstacles = []
    obstacles.append(pg.Rect(140, 220, 360, 18))
    obstacles.append(pg.Rect(780, 200, 280, 18))
    obstacles.append(pg.Rect(220, 500, 320, 18))
    obstacles.append(pg.Rect(760, 500, 240, 18))
    obstacles.append(pg.Rect(520, 320, 80, 48))
    obstacles.append(pg.Rect(320, 340, 60, 60))
    obstacles.append(pg.Rect(900, 340, 70, 54))
    for _ in range(8):
        x = random.randint(60, C.WIDTH - 120)
        y = random.randint(80, C.HEIGHT - 100)
        w = random.randint(40, 100)
        h = random.randint(18, 34)
        obstacles.append(pg.Rect(x, y, w, h))
    return obstacles

# ---------- Safezone ----------
def spawn_safezone(obstacles):
    sw, sh = C.SAFEZONE_SIZE
    m = C.SAFEZONE_EDGE_MARGIN
    for _ in range(100):
        side = random.choice(['top','bottom','left','right'])
        if side == 'top':
            x, y = random.randint(m, C.WIDTH - sw - m), m
        elif side == 'bottom':
            x, y = random.randint(m, C.WIDTH - sw - m), C.HEIGHT - sh - m
        elif side == 'left':
            x, y = m, random.randint(m, C.HEIGHT - sh - m)
        else:
            x, y = C.WIDTH - sw - m, random.randint(m, C.HEIGHT - sh - m)
        rect = pg.Rect(x, y, sw, sh)
        if not any(rect.colliderect(o) for o in obstacles):
            return rect
    return pg.Rect((C.WIDTH - sw)//2, (C.HEIGHT - sh)//2, sw, sh)

def draw_safezone(surface, rect, offset=(0,0)):
    ox, oy = offset
    r = pg.Rect(rect.x + ox, rect.y + oy, rect.w, rect.h)
    pg.draw.rect(surface, C.SAFEZONE_COLOR, r, border_radius=8)
    pg.draw.rect(surface, (30, 50, 38), r.inflate(-8, -8), width=2, border_radius=6)

# ---------- Reset helpers ----------
def reset_game(obstacles):
    boids = init_boids(C.INITIAL_BOIDS)
    player_pos = np.array([C.WIDTH * 0.5, C.HEIGHT * 0.5], dtype=float)
    for b in boids:
        if any(r.collidepoint(b.position[0], b.position[1]) for r in obstacles):
            b.position = rand_edge_pos()
    return boids, player_pos

def main():
    pg.init()
    screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
    pg.display.set_caption("Zombie Swarm AI — Niveles con Punto Seguro")
    clock = pg.time.Clock()
    font = pg.font.Font(None, 24)
    big_font = pg.font.Font(None, 72)
    help_font = pg.font.Font(None, 22)
    small_bold = pg.font.Font(None, 26)

    # UI/FX
    help_on = True

    grass_bg = generate_grass_surface(C.WIDTH, C.HEIGHT, seed=42)

    obstacles = build_field_obstacles()
    safezone = spawn_safezone(obstacles)

    boids, player_pos = reset_game(obstacles)
    auto_spawn = C.AUTO_SPAWN
    last_spawn = pg.time.get_ticks()
    game_over = False

    # Horda (alerta)
    alert_active = False
    alert_started_at = 0
    last_alert_at = 0

    # Niveles / tiempo
    level = 1
    level_start_time = pg.time.get_ticks()
    total_time_ms = 0
    best_total_time_ms = 0
    intermission = False
    intermission_until = 0

    # Dificultad base guardada
    base_max_boids = C.MAX_BOIDS
    base_spawn_interval = C.SPAWN_INTERVAL_MS
    base_detection = C.DETECTION_RADIUS
    base_weight_seek = C.WEIGHT_SEEK

    def apply_difficulty(lvl: int):
        C.MAX_BOIDS = base_max_boids + 6 * (lvl - 1)
        C.SPAWN_INTERVAL_MS = max(600, int(base_spawn_interval * (0.92 ** (lvl - 1))))
        C.DETECTION_RADIUS = int(base_detection * (1.06 ** (lvl - 1)))
        C.WEIGHT_SEEK = base_weight_seek * (1.06 ** (lvl - 1))

    apply_difficulty(level)

    running = True
    while running:
        # --- Input / eventos ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # vuelve al menú (no cerrar app)
                pg.event.clear()
                pg.quit()
                return
            elif event.type == pg.KEYDOWN:
                # salir al menú
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.event.clear()
                    pg.quit()
                    return
                # añadir/quitar zombis (debug útil)
                elif event.key in (pg.K_EQUALS, pg.K_PLUS):
                    if not game_over and not intermission and len(boids) < C.MAX_BOIDS:
                        boids.append(spawn_boid(near_edges=C.SPAWN_EDGE_ONLY))
                elif event.key == pg.K_MINUS:
                    if not game_over and not intermission and boids:
                        boids.pop()
                # toggle ayuda
                elif event.key == pg.K_h:
                    help_on = not help_on
                # opciones en GAME OVER
                elif game_over:
                    if event.key == pg.K_r:
                        # Reinicia mismo nivel
                        obstacles = build_field_obstacles()
                        safezone = spawn_safezone(obstacles)
                        boids = init_boids(C.INITIAL_BOIDS)
                        player_pos = np.array([C.WIDTH * 0.5, C.HEIGHT * 0.5], dtype=float)
                        last_spawn = pg.time.get_ticks()
                        alert_active = False
                        intermission = False
                        game_over = False
                        apply_difficulty(level)  # asegura escalado vigente
                        level_start_time = pg.time.get_ticks()  # reinicia reloj del nivel
                    elif event.key in (pg.K_RETURN, pg.K_SPACE):
                        pg.event.clear()
                        pg.quit()
                        return

        now_ticks = pg.time.get_ticks()

        # Movimiento del jugador
        if not game_over and not intermission:
            keys = pg.key.get_pressed()
            move = np.zeros(2, dtype=float)
            sprinting = keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                move[0] -= 1
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                move[0] += 1
            if keys[pg.K_w] or keys[pg.K_UP]:
                move[1] -= 1
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                move[1] += 1
            speed = C.PLAYER_SPEED_SPRINT if sprinting else C.PLAYER_SPEED
            if np.linalg.norm(move) > 0:
                move = move / np.linalg.norm(move) * speed
                player_pos += move
                player_pos = clamp_player(player_pos)

        # Spawning automático
        if not game_over and auto_spawn and len(boids) < C.MAX_BOIDS and not intermission:
            if now_ticks - last_spawn >= C.SPAWN_INTERVAL_MS:
                boids.append(spawn_boid(near_edges=C.SPAWN_EDGE_ONLY))
                last_spawn = now_ticks

        # Update boids + LOS + alerta
        chase_flags = [False] * len(boids)
        if not game_over and not intermission:
            vis_factor = 1.0
            keys = pg.key.get_pressed()
            if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
                vis_factor *= C.SPRINT_MULT
            effective_radius = C.DETECTION_RADIUS * vis_factor

            global_chase = alert_active
            someone_saw = False

            for i, b in enumerate(boids):
                d = np.linalg.norm(player_pos - b.position)
                can_see = (d < effective_radius) and has_line_of_sight(b.position, player_pos, obstacles)
                if can_see:
                    someone_saw = True
                chase = (global_chase or can_see)
                chase_flags[i] = chase
                b.update(boids, player_pos, chase=chase)

            if someone_saw and (now_ticks - last_alert_at >= C.ALERT_COOLDOWN_MS):
                alert_active = True
                alert_started_at = now_ticks
                last_alert_at = now_ticks

            if alert_active and (now_ticks - alert_started_at >= C.ALERT_DURATION_MS):
                alert_active = False

        # Colisiones (muerte)
        if not game_over and not intermission:
            pr = C.PLAYER_HIT_RADIUS + C.BOID_SIZE
            for b in boids:
                if np.linalg.norm(b.position - player_pos) <= pr and has_line_of_sight(b.position, player_pos, obstacles):
                    game_over = True
                    alert_active = False
                    break

        # Win condition: entrar en SafeZone
        if not game_over and not intermission:
            if safezone.collidepoint(int(player_pos[0]), int(player_pos[1])):
                intermission = True
                intermission_until = now_ticks + C.LEVEL_UP_PAUSE_MS
                total_time_ms += (now_ticks - level_start_time)
                level += 1
                apply_difficulty(level)

        # Completar intermission (cambio de nivel real)
        if intermission and now_ticks >= intermission_until:
            obstacles = build_field_obstacles()
            safezone = spawn_safezone(obstacles)
            boids = init_boids(C.INITIAL_BOIDS)
            player_pos = np.array([C.WIDTH * 0.5, C.HEIGHT * 0.5], dtype=float)
            last_spawn = pg.time.get_ticks()
            alert_active = False
            level_start_time = pg.time.get_ticks()
            intermission = False

        # --- Dibujo ---
        screen.blit(grass_bg, (0, 0))

        # Safezone primero
        draw_safezone(screen, safezone)

        # Obstáculos y entidades
        draw_obstacles(screen, obstacles)
        for b, chasing in zip(boids, chase_flags if not game_over else [False]*len(boids)):
            color = CHASE_COLOR if (alert_active or chasing) else PATROL_COLOR
            draw_boid(screen, b.position, b.velocity, color)
        draw_player(screen, player_pos, alive=not game_over)

        # Mini panel superior derecha: Nivel / Tiempo / Récord
        ui_lines = []
        live_total = total_time_ms + (0 if (game_over or intermission) else (pg.time.get_ticks() - level_start_time))
        def fmt(ms):
            s = ms//1000; m = s//60; s = s%60; return f"{m:02d}:{s:02d}"
        ui_lines.append(f"Nivel: {level}")
        ui_lines.append(f"Tiempo: {fmt(live_total)}")
        # (opcional) récord de sesión: añádelo si quieres persistir en JSON
        panel_w = 200
        panel_h = len(ui_lines)*22 + 16
        panel_rect = pg.Rect(C.WIDTH - panel_w - 10, 10, panel_w, panel_h)
        panel_surface = pg.Surface((panel_rect.w, panel_rect.h), pg.SRCALPHA)
        panel_surface.fill((20, 20, 24, 150))
        screen.blit(panel_surface, panel_rect.topleft)
        x, y = panel_rect.x + 10, panel_rect.y + 8
        for line in ui_lines:
            surf = small_bold.render(line, True, (225, 225, 235))
            screen.blit(surf, (x, y)); y += 22

        # Mensajes de estado
        if intermission:
            text = big_font.render(f"NIVEL {level}", True, (230, 230, 230))
            prompt = font.render("¡Sobrevive y llega al punto seguro!", True, (200, 230, 210))
            screen.blit(text, (C.WIDTH//2 - text.get_width()//2, C.HEIGHT//2 - 70))
            screen.blit(prompt, (C.WIDTH//2 - prompt.get_width()//2, C.HEIGHT//2 + 5))

        if game_over:
            text = big_font.render("GAME OVER", True, (230, 80, 80))
            prompt1 = font.render("Pulsa R para reiniciar este nivel", True, (210, 210, 220))
            prompt2 = font.render("ENTER o ESPACIO para volver al menú", True, (210, 210, 220))
            screen.blit(text, (C.WIDTH//2 - text.get_width()//2, C.HEIGHT//2 - 80))
            screen.blit(prompt1, (C.WIDTH//2 - prompt1.get_width()//2, C.HEIGHT//2 + 10))
            screen.blit(prompt2, (C.WIDTH//2 - prompt2.get_width()//2, C.HEIGHT//2 + 38))

        pg.display.flip()
        clock.tick(C.FPS)

    # Si alguna vez sales del bucle por otras razones:
    pg.quit()
    return

if __name__ == "__main__":
    main()
