from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from . import config as C

def limit(vec: np.ndarray, max_value: float) -> np.ndarray:
    speed = np.linalg.norm(vec)
    if speed > max_value and speed > 0.0:
        return vec * (max_value / speed)
    return vec

def wrap_position(pos: np.ndarray) -> np.ndarray:
    x, y = pos
    x = x % C.WIDTH
    y = y % C.HEIGHT
    return np.array([x, y], dtype=float)

@dataclass
class Boid:
    position: np.ndarray  # (x, y)
    velocity: np.ndarray  # (vx, vy)

    def update(self, boids: list['Boid'], player_pos: np.ndarray | None = None, chase: bool = False) -> None:
        # Patrulla (boids clásicos)
        steer_sep = self.separation(boids) * C.WEIGHT_SEPARATION
        steer_align = self.alignment(boids) * C.WEIGHT_ALIGNMENT
        steer_cohesion = self.cohesion(boids) * C.WEIGHT_COHESION

        acceleration = steer_sep + steer_align + steer_cohesion

        # Caza si tiene permiso (línea de visión y dentro de radio)
        if chase and player_pos is not None:
            acceleration += self.seek(player_pos) * C.WEIGHT_SEEK

        self.velocity += acceleration
        self.velocity = limit(self.velocity, C.MAX_SPEED)
        self.position = wrap_position(self.position + self.velocity)

    # ---------- Reglas base ----------
    def neighbors(self, boids: list['Boid'], radius: float) -> list['Boid']:
        neighs = []
        for b in boids:
            if b is self:
                continue
            d = np.linalg.norm(b.position - self.position)
            if d < radius:
                neighs.append(b)
        return neighs

    def separation(self, boids: list['Boid']) -> np.ndarray:
        steer = np.zeros(2, dtype=float)
        total = 0
        for b in self.neighbors(boids, C.SEPARATION_RADIUS):
            diff = self.position - b.position
            dist = np.linalg.norm(diff)
            if dist > 0:
                steer += diff / (dist * dist)
                total += 1
        if total > 0:
            steer /= total
        if np.linalg.norm(steer) > 0:
            steer = limit(steer, C.MAX_FORCE)
        return steer

    def alignment(self, boids: list['Boid']) -> np.ndarray:
        avg_vel = np.zeros(2, dtype=float)
        total = 0
        for b in self.neighbors(boids, C.NEIGHBOR_RADIUS):
            avg_vel += b.velocity
            total += 1
        if total > 0:
            avg_vel /= total
            desired = limit(avg_vel, C.MAX_SPEED)
            steer = desired - self.velocity
            return limit(steer, C.MAX_FORCE)
        return np.zeros(2, dtype=float)

    def cohesion(self, boids: list['Boid']) -> np.ndarray:
        center = np.zeros(2, dtype=float)
        total = 0
        for b in self.neighbors(boids, C.NEIGHBOR_RADIUS):
            center += b.position
            total += 1
        if total > 0:
            center /= total
            desired = center - self.position
            if np.linalg.norm(desired) > 0:
                desired = limit(desired, C.MAX_SPEED)
                steer = desired - self.velocity
                return limit(steer, C.MAX_FORCE)
        return np.zeros(2, dtype=float)

    # ---------- Steering helpers ----------
    def seek(self, target: np.ndarray) -> np.ndarray:
        desired = target - self.position
        if np.linalg.norm(desired) > 0:
            desired = limit(desired, C.MAX_SPEED)
            steer = desired - self.velocity
            return limit(steer, C.MAX_FORCE)
        return np.zeros(2, dtype=float)
