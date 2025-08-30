import sys
import math
import random
import pygame as pg
from . import config as C

# ======== Paleta campo (verde + tierra) ========
GRASS_DARK  = (16, 44, 24)
GRASS_MID   = (28, 68, 36)
DIRT_BROWN  = (74, 58, 42)
ACCENT      = (186, 102, 60)   # acento cálido
TEXT        = (236, 238, 232)
MUTED       = (196, 204, 196)
BTN_BG      = (34, 56, 40, 200)
BTN_BG_HV   = (44, 74, 52, 220)
BTN_BR      = (90, 124, 96)

# ======== Fondo: pradera + manchas de tierra ========
def generate_grass_surface(w, h, seed=42):
    rnd = random.Random(seed)
    surf = pg.Surface((w, h))
    # degradado verde
    strip = pg.Surface((1, h))
    for y in range(h):
        t = y / max(1, h-1)
        r = int(GRASS_DARK[0]*(1-t) + GRASS_MID[0]*t)
        g = int(GRASS_DARK[1]*(1-t) + GRASS_MID[1]*t)
        b = int(GRASS_DARK[2]*(1-t) + GRASS_MID[2]*t)
        strip.set_at((0, y), (r, g, b))
    surf.blit(pg.transform.scale(strip, (w, h)), (0, 0))
    # parches de césped
    shades = [(30,72,38), (24,60,30), (32,78,40)]
    for _ in range((w*h)//900):
        col = rnd.choice(shades)
        x = rnd.randrange(0, w); y = rnd.randrange(0, h)
        rw = rnd.randint(3, 7); rh = rnd.randint(3, 7)
        surf.fill(col, (x, y, rw, rh))
    # caminos de tierra
    for _ in range(2):
        px, py = rnd.randint(0, w), rnd.randint(0, h)
        for i in range(240):
            dx = int(10 * math.sin(i * 0.09 + rnd.random()))
            dy = int(10 * math.cos(i * 0.09 + rnd.random()))
            rect = pg.Rect((px + dx) % w, (py + dy) % h, 12, 6)
            surf.fill(DIRT_BROWN, rect)
            px = (px + rnd.randint(-6, 8)) % w
            py = (py + rnd.randint(-3, 3)) % h
    return surf

def vignette_green(surface, strength=110):
    """Viñeta suave, sin paneles negros."""
    w, h = surface.get_size()
    mask = pg.Surface((w, h), pg.SRCALPHA)
    for i in range(14):
        alpha = int(strength * (i/14) * 0.8)
        pg.draw.rect(mask, (10, 20, 14, alpha),
                     (i*3, i*3, w - i*6, h - i*6), border_radius=10)
    surface.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_SUB)

class DustMotes:
    """Motas de polvo flotando (sutil)."""
    def __init__(self, w, h, count=120):
        rnd = random.Random(7)
        self.w, self.h = w, h
        self.m = []
        for _ in range(count):
            x = rnd.uniform(0, w); y = rnd.uniform(0, h)
            r = rnd.uniform(0.15, 0.8)
            sx = rnd.uniform(-0.02, 0.02); sy = rnd.uniform(-0.03, 0.01)
            phase = rnd.uniform(0, 6.28)
            self.m.append([x, y, r, sx, sy, phase])
    def update_draw(self, surface, dt_ms):
        dt = dt_ms
        for p in self.m:
            p[0] += p[3] * dt; p[1] += p[4] * dt
            p[5] += 0.0015 * dt
            if p[0] < -5: p[0] = self.w + 5
            if p[0] > self.w+5: p[0] = -5
            if p[1] < -5: p[1] = self.h + 5
            if p[1] > self.h+5: p[1] = -5
            a = 50 + int(30 * (0.5 + 0.5*math.sin(p[5])))
            col = (220, 228, 210, a)
            pg.draw.circle(surface, col, (int(p[0]), int(p[1])), max(1, int(p[2]*3)))

# ======== UI ========
def draw_title(surface, text, t):
    title_font = pg.font.Font(None, 92)
    y_off = 1.3 * math.sin(t * 0.35)
    color = (int(ACCENT[0]*0.95), int(ACCENT[1]*0.75), int(ACCENT[2]*0.7))
    surf = title_font.render(text, True, color)
    surface.blit(surf, (C.WIDTH//2 - surf.get_width()//2, 90 + y_off))

class Button:
    def __init__(self, text, center):
        self.text = text
        self.center = center
        self.rect = pg.Rect(0, 0, 1, 1)
        self.hover = False
        self.font = pg.font.Font(None, 40)
        self.fixed_size = None
    def set_size(self, size_tuple):
        self.fixed_size = size_tuple
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
    def draw(self, surface):
        label = self.font.render(self.text, True, TEXT)
        pad_x, pad_y = 24, 12
        if self.fixed_size:
            w, h = self.fixed_size
        else:
            w = label.get_width() + pad_x*2
            h = label.get_height() + pad_y*2
        x = self.center[0] - w//2
        y = self.center[1] - h//2
        self.rect = pg.Rect(x, y, w, h)
        btn = pg.Surface((w, h), pg.SRCALPHA)
        btn.fill(BTN_BG_HV if self.hover else BTN_BG)
        pg.draw.rect(btn, BTN_BR + (180,), btn.get_rect(), width=2, border_radius=12)
        surface.blit(btn, (x, y))
        surface.blit(label, (x + pad_x, y + pad_y))

def draw_help_panel(surface):
    font = pg.font.Font(None, 30)
    lines = [
        "CONTROLES",
        "WASD / Flechas — Moverse",
        "Shift          — Correr (más visible)",
        "C              — Agacharse (menos visible)",
        "R              — Reiniciar nivel",
        "Z              — Spawn automático ON/OFF",
        "+ / -          — Añadir/Quitar zombis",
        "T / L          — Trails / Linterna",
        "R              — Reiniciar",
        "H              — Ayuda en partida",
        "ESC / Q        — Salir",
    ]
    x, y = 40, 150
    for i, line in enumerate(lines):
        col = TEXT if i == 0 else (226, 232, 224)
        surf = font.render(line, True, col)
        surface.blit(surf, (x, y)); y += 28

# ======== MENÚ PRINCIPAL ========
def main_menu():
    pg.init()
    screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
    pg.display.set_caption("Zombie Swarm AI — Menú")
    clock = pg.time.Clock()

    grass_bg = generate_grass_surface(C.WIDTH, C.HEIGHT, seed=42)
    dust = DustMotes(C.WIDTH, C.HEIGHT, count=110)
    t0 = pg.time.get_ticks()

    # Botones
    play_btn = Button("Jugar",     (C.WIDTH//2, 330))
    help_btn = Button("Controles", (C.WIDTH//2, 400))
    exit_btn = Button("Salir",     (C.WIDTH//2, 470))
    buttons  = [play_btn, help_btn, exit_btn]
    selected = 0

    # Igualar tamaño
    tmp_font = play_btn.font
    label_ws = [tmp_font.size(b.text)[0] for b in buttons]
    label_h  = tmp_font.get_height()
    pad_x, pad_y = 24, 12
    btn_w = max(label_ws) + pad_x*2
    btn_h = label_h + pad_y*2
    for b in buttons:
        b.set_size((btn_w, btn_h))

    while True:
        dt = clock.get_time()
        mouse_pos = pg.mouse.get_pos()

        # Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.quit(); sys.exit()
                elif event.key in (pg.K_UP, pg.K_w):
                    selected = (selected - 1) % len(buttons)
                elif event.key in (pg.K_DOWN, pg.K_s):
                    selected = (selected + 1) % len(buttons)
                elif event.key in (pg.K_RETURN, pg.K_SPACE):
                    choice = buttons[selected].text.lower()
                    return "jugar" if choice=="jugar" else ("controles" if choice=="controles" else "salir")
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.rect.collidepoint(mouse_pos):
                        txt = b.text.lower()
                        return "jugar" if txt=="jugar" else ("controles" if txt=="controles" else "salir")

        # Hover
        for i, b in enumerate(buttons):
            b.update(mouse_pos)
            if b.hover: selected = i

        # --- Dibujo ---
        screen.blit(grass_bg, (0, 0))
        dust.update_draw(screen, dt)
        t = (pg.time.get_ticks() - t0) / 1000.0
        draw_title(screen, "Zombie Swarm AI", t)

        # Botones
        for i, b in enumerate(buttons):
            b.draw(screen)
            if i == selected:
                pg.draw.circle(screen, ACCENT, (b.rect.left - 18, b.rect.centery), 5)

        vignette_green(screen, strength=110)
        pg.display.flip()
        clock.tick(60)

# ======== PANTALLA CONTROLES ========
def show_controls():
    screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
    pg.display.set_caption("Zombie Swarm AI — Controles")
    clock = pg.time.Clock()

    grass_bg = generate_grass_surface(C.WIDTH, C.HEIGHT, seed=77)
    dust = DustMotes(C.WIDTH, C.HEIGHT, count=100)
    back_btn = Button("Volver", (C.WIDTH//2, C.HEIGHT - 100))
    back_btn.set_size((180, 50))

    while True:
        dt = clock.get_time()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q, pg.K_RETURN, pg.K_SPACE):
                    return
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.rect.collidepoint(mouse_pos):
                    return

        screen.blit(grass_bg, (0, 0))
        dust.update_draw(screen, dt)

        draw_help_panel(screen)
        head = pg.font.Font(None, 50).render("Sobrevive… y llega al punto seguro", True, (220, 210, 200))
        screen.blit(head, (C.WIDTH//2 - head.get_width()//2, 70))

        back_btn.update(mouse_pos)
        back_btn.draw(screen)

        vignette_green(screen, strength=110)
        pg.display.flip()
        clock.tick(60)
import sys
import math
import random
import pygame as pg
from . import config as C

# ======== Paleta campo (verde + tierra) ========
GRASS_DARK  = (16, 44, 24)
GRASS_MID   = (28, 68, 36)
DIRT_BROWN  = (74, 58, 42)
ACCENT      = (186, 102, 60)   # acento cálido
TEXT        = (236, 238, 232)
MUTED       = (196, 204, 196)
BTN_BG      = (34, 56, 40, 200)
BTN_BG_HV   = (44, 74, 52, 220)
BTN_BR      = (90, 124, 96)

# ======== Fondo: pradera + manchas de tierra ========
def generate_grass_surface(w, h, seed=42):
    rnd = random.Random(seed)
    surf = pg.Surface((w, h))
    # degradado verde
    strip = pg.Surface((1, h))
    for y in range(h):
        t = y / max(1, h-1)
        r = int(GRASS_DARK[0]*(1-t) + GRASS_MID[0]*t)
        g = int(GRASS_DARK[1]*(1-t) + GRASS_MID[1]*t)
        b = int(GRASS_DARK[2]*(1-t) + GRASS_MID[2]*t)
        strip.set_at((0, y), (r, g, b))
    surf.blit(pg.transform.scale(strip, (w, h)), (0, 0))
    # parches de césped
    shades = [(30,72,38), (24,60,30), (32,78,40)]
    for _ in range((w*h)//900):
        col = rnd.choice(shades)
        x = rnd.randrange(0, w); y = rnd.randrange(0, h)
        rw = rnd.randint(3, 7); rh = rnd.randint(3, 7)
        surf.fill(col, (x, y, rw, rh))
    # caminos de tierra
    for _ in range(2):
        px, py = rnd.randint(0, w), rnd.randint(0, h)
        for i in range(240):
            dx = int(10 * math.sin(i * 0.09 + rnd.random()))
            dy = int(10 * math.cos(i * 0.09 + rnd.random()))
            rect = pg.Rect((px + dx) % w, (py + dy) % h, 12, 6)
            surf.fill(DIRT_BROWN, rect)
            px = (px + rnd.randint(-6, 8)) % w
            py = (py + rnd.randint(-3, 3)) % h
    return surf

def vignette_green(surface, strength=110):
    """Viñeta suave, sin paneles negros."""
    w, h = surface.get_size()
    mask = pg.Surface((w, h), pg.SRCALPHA)
    for i in range(14):
        alpha = int(strength * (i/14) * 0.8)
        pg.draw.rect(mask, (10, 20, 14, alpha),
                     (i*3, i*3, w - i*6, h - i*6), border_radius=10)
    surface.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_SUB)

class DustMotes:
    """Motas de polvo flotando (sutil)."""
    def __init__(self, w, h, count=110):
        rnd = random.Random(7)
        self.w, self.h = w, h
        self.m = []
        for _ in range(count):
            x = rnd.uniform(0, w); y = rnd.uniform(0, h)
            r = rnd.uniform(0.15, 0.8)
            sx = rnd.uniform(-0.02, 0.02); sy = rnd.uniform(-0.03, 0.01)
            phase = rnd.uniform(0, 6.28)
            self.m.append([x, y, r, sx, sy, phase])
    def update_draw(self, surface, dt_ms):
        dt = dt_ms
        for p in self.m:
            p[0] += p[3] * dt; p[1] += p[4] * dt
            p[5] += 0.0015 * dt
            if p[0] < -5: p[0] = self.w + 5
            if p[0] > self.w+5: p[0] = -5
            if p[1] < -5: p[1] = self.h + 5
            if p[1] > self.h+5: p[1] = -5
            a = 50 + int(30 * (0.5 + 0.5*math.sin(p[5])))
            col = (220, 228, 210, a)
            pg.draw.circle(surface, col, (int(p[0]), int(p[1])), max(1, int(p[2]*3)))

# ======== UI ========
def draw_title(surface, text, t):
    title_font = pg.font.Font(None, 92)
    y_off = 1.0 * math.sin(t * 0.35)
    color = (int(ACCENT[0]*0.95), int(ACCENT[1]*0.75), int(ACCENT[2]*0.7))
    surf = title_font.render(text, True, color)
    surface.blit(surf, (C.WIDTH//2 - surf.get_width()//2, 90 + y_off))

class Button:
    def __init__(self, text, center):
        self.text = text
        self.center = center
        self.rect = pg.Rect(0, 0, 1, 1)
        self.hover = False
        self.font = pg.font.Font(None, 40)
        self.fixed_size = None
    def set_size(self, size_tuple):
        self.fixed_size = size_tuple
    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
    def draw(self, surface):
        label = self.font.render(self.text, True, TEXT)
        pad_x, pad_y = 24, 12
        if self.fixed_size:
            w, h = self.fixed_size
        else:
            w = label.get_width() + pad_x*2
            h = label.get_height() + pad_y*2
        x = self.center[0] - w//2
        y = self.center[1] - h//2
        self.rect = pg.Rect(x, y, w, h)
        btn = pg.Surface((w, h), pg.SRCALPHA)
        btn.fill(BTN_BG_HV if self.hover else BTN_BG)
        pg.draw.rect(btn, BTN_BR + (180,), btn.get_rect(), width=2, border_radius=12)
        surface.blit(btn, (x, y))
        surface.blit(label, (x + pad_x, y + pad_y))

def draw_help_panel(surface):
    # Controles mínimos y reales
    font = pg.font.Font(None, 30)
    lines = [
        "CONTROLES",
        "WASD / Flechas — Moverse",
        "Shift          — Correr (más visible)",
        "+ / -          — Añadir/Quitar zombis",
        "H              — Mostrar/Ocultar ayuda",
        "R              — Reiniciar nivel",
        "ESC / Q        — Salir",
    ]
    x, y = 40, 150
    for i, line in enumerate(lines):
        col = TEXT if i == 0 else (226, 232, 224)
        surf = font.render(line, True, col)
        surface.blit(surf, (x, y)); y += 28

# ======== MENÚ PRINCIPAL ========
def main_menu():
    pg.init()
    screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
    pg.display.set_caption("Zombie Swarm AI — Menú")
    clock = pg.time.Clock()

    grass_bg = generate_grass_surface(C.WIDTH, C.HEIGHT, seed=42)
    dust = DustMotes(C.WIDTH, C.HEIGHT, count=110)
    t0 = pg.time.get_ticks()

    # Botones
    play_btn = Button("Jugar",     (C.WIDTH//2, 330))
    help_btn = Button("Controles", (C.WIDTH//2, 400))
    exit_btn = Button("Salir",     (C.WIDTH//2, 470))
    buttons  = [play_btn, help_btn, exit_btn]
    selected = 0

    # Igualar tamaño
    tmp_font = play_btn.font
    label_ws = [tmp_font.size(b.text)[0] for b in buttons]
    label_h  = tmp_font.get_height()
    pad_x, pad_y = 24, 12
    btn_w = max(label_ws) + pad_x*2
    btn_h = label_h + pad_y*2
    for b in buttons:
        b.set_size((btn_w, btn_h))

    while True:
        dt = clock.get_time()
        mouse_pos = pg.mouse.get_pos()

        # Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.quit(); sys.exit()
                elif event.key in (pg.K_UP, pg.K_w):
                    selected = (selected - 1) % len(buttons)
                elif event.key in (pg.K_DOWN, pg.K_s):
                    selected = (selected + 1) % len(buttons)
                elif event.key in (pg.K_RETURN, pg.K_SPACE):
                    choice = buttons[selected].text.lower()
                    return "jugar" if choice=="jugar" else ("controles" if choice=="controles" else "salir")
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for b in buttons:
                    if b.rect.collidepoint(mouse_pos):
                        txt = b.text.lower()
                        return "jugar" if txt=="jugar" else ("controles" if txt=="controles" else "salir")

        # Hover
        for i, b in enumerate(buttons):
            b.update(mouse_pos)
            if b.hover: selected = i

        # --- Dibujo ---
        screen.blit(grass_bg, (0, 0))
        dust.update_draw(screen, dt)
        t = (pg.time.get_ticks() - t0) / 1000.0
        draw_title(screen, "Zombie Swarm AI", t)

        # Botones
        for i, b in enumerate(buttons):
            b.draw(screen)
            if i == selected:
                pg.draw.circle(screen, ACCENT, (b.rect.left - 18, b.rect.centery), 5)

        vignette_green(screen, strength=110)
        pg.display.flip()
        clock.tick(60)

# ======== PANTALLA CONTROLES ========
def show_controls():
    screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
    pg.display.set_caption("Zombie Swarm AI — Controles")
    clock = pg.time.Clock()

    grass_bg = generate_grass_surface(C.WIDTH, C.HEIGHT, seed=77)
    dust = DustMotes(C.WIDTH, C.HEIGHT, count=100)
    back_btn = Button("Volver", (C.WIDTH//2, C.HEIGHT - 100))
    back_btn.set_size((180, 50))

    while True:
        dt = clock.get_time()
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q, pg.K_RETURN, pg.K_SPACE):
                    return
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.rect.collidepoint(mouse_pos):
                    return

        screen.blit(grass_bg, (0, 0))
        dust.update_draw(screen, dt)

        draw_help_panel(screen)
        head = pg.font.Font(None, 50).render("Sobrevive… y llega al punto seguro", True, (220, 210, 200))
        screen.blit(head, (C.WIDTH//2 - head.get_width()//2, 70))

        back_btn.update(mouse_pos)
        back_btn.draw(screen)

        vignette_green(screen, strength=110)
        pg.display.flip()
        clock.tick(60)
