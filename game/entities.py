import math
import random

import pygame

from . import settings


class BaseDot:
    def __init__(self, width, height, radius, color, vx=None, vy=None, x=None, y=None):
        self.width = width
        self.height = height
        self.radius = radius
        self.color = color
        if x is None or y is None:
            self.x = random.uniform(self.radius, self.width - self.radius)
            self.y = random.uniform(self.radius, self.height - self.radius)
        else:
            self.x = x
            self.y = y

        if vx is None or vy is None:
            vx, vy = self._gaussian_velocity()

        self.vx = vx
        self.vy = vy
        self.speed = settings.DOT_SPEED

    def update(self, now_ms=None, speed_factor=1.0):
        _ = now_ms
        self._apply_brownian_turn()
        self.x += self.vx * speed_factor
        self.y += self.vy * speed_factor

        if self.x - self.radius <= 0 or self.x + self.radius >= self.width:
            self.vx *= -1
            self.x = max(self.radius, min(self.x, self.width - self.radius))

        if self.y - self.radius <= 0 or self.y + self.radius >= self.height:
            self.vy *= -1
            self.y = max(self.radius, min(self.y, self.height - self.radius))

    def _apply_brownian_turn(self):
        max_turn = math.radians(settings.BROWNIAN_ANGLE_DEGREES)
        turn = random.uniform(-max_turn, max_turn)
        angle = math.atan2(self.vy, self.vx) + turn
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

    def _gaussian_velocity(self):
        while True:
            vx = random.gauss(0, settings.VELOCITY_STD)
            vy = random.gauss(0, settings.VELOCITY_STD)
            magnitude = math.hypot(vx, vy)
            if magnitude > 1e-6:
                scale = settings.DOT_SPEED / magnitude
                return vx * scale, vy * scale

    @staticmethod
    def gaussian_velocity_around(center_vx, center_vy):
        while True:
            vx = random.gauss(center_vx, settings.PREY_VELOCITY_STD)
            vy = random.gauss(center_vy, settings.PREY_VELOCITY_STD)
            magnitude = math.hypot(vx, vy)
            if magnitude > 1e-6:
                scale = settings.DOT_SPEED / magnitude
                return vx * scale, vy * scale

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x), int(self.y)),
            self.radius,
        )


class PreyDot(BaseDot):
    def __init__(self, width, height, vx=None, vy=None, x=None, y=None):
        super().__init__(
            width,
            height,
            settings.DOT_RADIUS,
            settings.DOT_COLOR,
            vx=vx,
            vy=vy,
            x=x,
            y=y,
        )


class PredatorDot(BaseDot):
    def __init__(
        self, width, height, vx=None, vy=None, x=None, y=None, spawn_ms=0
    ):
        super().__init__(
            width,
            height,
            settings.PREDATOR_RADIUS,
            settings.PREDATOR_COLOR,
            vx=vx,
            vy=vy,
            x=x,
            y=y,
        )
        self.slow_until_ms = 0
        self.repro_rest_until_ms = 0
        self.last_eat_ms = None
        self.last_starve_check_ms = 0
        self.spawn_ms = spawn_ms
        self.can_reproduce = False

    def update(self, now_ms=None, speed_factor=1.0):
        _ = speed_factor
        if now_ms is None:
            super().update()
            return
        if now_ms < self.repro_rest_until_ms:
            return
        speed_factor = (
            settings.PREDATOR_SLOW_MULTIPLIER
            if now_ms < self.slow_until_ms
            else 1.0
        )
        super().update(now_ms=now_ms, speed_factor=speed_factor)

    def rest(self, now_ms):
        self.slow_until_ms = now_ms + settings.PREDATOR_PAUSE_MS

    def on_eat(self, now_ms):
        self.last_eat_ms = now_ms
        self.last_starve_check_ms = now_ms
        self.can_reproduce = True

    def repro_rest(self, now_ms):
        self.repro_rest_until_ms = max(
            self.repro_rest_until_ms, now_ms + settings.PREDATOR_REPRO_PAUSE_MS
        )


class ApexPredatorDot(BaseDot):
    def __init__(
        self, width, height, vx=None, vy=None, x=None, y=None, spawn_ms=0
    ):
        super().__init__(
            width,
            height,
            settings.APEX_PREDATOR_RADIUS,
            settings.APEX_PREDATOR_COLOR,
            vx=vx,
            vy=vy,
            x=x,
            y=y,
        )
        self.rest_until_ms = 0
        self.last_eat_ms = None
        self.spawn_ms = spawn_ms
        self.slow_until_ms = 0

    def update(self, now_ms=None, speed_factor=1.0):
        _ = speed_factor
        if now_ms is None:
            super().update()
            return
        speed_factor = (
            settings.APEX_SLOW_MULTIPLIER
            if now_ms < self.slow_until_ms
            else 1.0
        )
        super().update(now_ms=now_ms, speed_factor=speed_factor)

    def rest(self, now_ms):
        self.slow_until_ms = now_ms + settings.APEX_PAUSE_MS

    def on_eat(self, now_ms):
        self.last_eat_ms = now_ms
