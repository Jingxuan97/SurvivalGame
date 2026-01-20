import math
import random

from typing import Any

import pygame as _pygame

pygame: Any = _pygame

from . import settings
from .entities import ApexPredatorDot, BaseDot, PredatorDot, PreyDot


def run():
    getattr(pygame, "init")()
    screen = pygame.display.set_mode(
        (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
    )
    pygame.display.set_caption(settings.WINDOW_TITLE)

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    start_ms = pygame.time.get_ticks()
    prey = [
        PreyDot(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
        for _ in range(settings.PREY_COUNT)
    ]
    predators = [
        PredatorDot(
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT,
            spawn_ms=start_ms,
        )
        for _ in range(settings.PREDATOR_COUNT)
    ]
    apex_predators = [
        ApexPredatorDot(
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT,
            spawn_ms=start_ms,
        )
        for _ in range(settings.APEX_PREDATOR_COUNT)
    ]
    last_repro_ms = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == getattr(pygame, "QUIT"):
                running = False

        now_ms = pygame.time.get_ticks()

        for dot in prey:
            dot.update()

        new_predators = []
        for predator in predators:
            predator.update(now_ms)
            if now_ms >= predator.repro_rest_until_ms:
                last_eat = (
                    predator.last_eat_ms
                    if predator.last_eat_ms is not None
                    else predator.spawn_ms
                )
                if now_ms - last_eat >= settings.EAT_COOLDOWN_MS:
                    for dot in list(prey):
                        distance = math.hypot(predator.x - dot.x, predator.y - dot.y)
                        if distance <= settings.EAT_RADIUS:
                            if random.random() < settings.EAT_PROBABILITY:
                                prey.remove(dot)
                                predator.rest(now_ms)
                                predator.on_eat(now_ms)
                            break
        predators.extend(new_predators)

        for apex in apex_predators:
            apex.update(now_ms)
            last_eat = apex.last_eat_ms if apex.last_eat_ms is not None else apex.spawn_ms
            if now_ms - last_eat < settings.APEX_EAT_COOLDOWN_MS:
                continue
            for dot in list(predators):
                distance = math.hypot(apex.x - dot.x, apex.y - dot.y)
                if distance <= settings.APEX_EAT_RADIUS:
                    if random.random() < settings.APEX_EAT_PROBABILITY:
                        predators.remove(dot)
                        apex.rest(now_ms)
                        apex.on_eat(now_ms)
                    break

        for predator in list(predators):
            last_eat = (
                predator.last_eat_ms
                if predator.last_eat_ms is not None
                else predator.spawn_ms
            )
            if now_ms - last_eat >= settings.STARVE_AFTER_MS:
                if now_ms - predator.last_starve_check_ms >= settings.STARVE_CHECK_MS:
                    predator.last_starve_check_ms = now_ms
                    if random.random() < settings.STARVE_PROBABILITY:
                        predators.remove(predator)

        if len(predators) > 1:
            used = set()
            for i, a in enumerate(predators):
                if (
                    i in used
                    or now_ms < a.repro_rest_until_ms
                    or not a.can_reproduce
                ):
                    continue
                for j in range(i + 1, len(predators)):
                    if j in used:
                        continue
                    b = predators[j]
                    if now_ms < b.repro_rest_until_ms or not b.can_reproduce:
                        continue
                    distance = math.hypot(a.x - b.x, a.y - b.y)
                    if distance <= settings.PREDATOR_REPRO_RADIUS:
                        a.repro_rest(now_ms)
                        b.repro_rest(now_ms)
                        a.can_reproduce = False
                        b.can_reproduce = False
                        used.add(i)
                        used.add(j)
                        roll = random.random()
                        if roll < settings.PREDATOR_REPRO_PROBS[0]:
                            offspring = 0
                        elif roll < settings.PREDATOR_REPRO_PROBS[0] + settings.PREDATOR_REPRO_PROBS[1]:
                            offspring = 1
                        else:
                            offspring = 2
                        for _ in range(offspring):
                            vx, vy = BaseDot.gaussian_velocity_around(
                                (a.vx + b.vx) / 2, (a.vy + b.vy) / 2
                            )
                            new_predators.append(
                                PredatorDot(
                                    settings.WINDOW_WIDTH,
                                    settings.WINDOW_HEIGHT,
                                    vx=vx,
                                    vy=vy,
                                    x=(a.x + b.x) / 2,
                                    y=(a.y + b.y) / 2,
                                    spawn_ms=now_ms,
                                )
                            )
                        break
            predators.extend(new_predators)

        if now_ms - last_repro_ms >= settings.PREY_REPRO_INTERVAL_MS:
            prey_count = max(1, len(prey))
            repro_prob = settings.PREY_REPRO_PROB * (
                settings.PREY_COUNT / prey_count
            )
            repro_prob = min(1.0, repro_prob)
            for dot in list(prey):
                if random.random() < repro_prob:
                    vx, vy = BaseDot.gaussian_velocity_around(dot.vx, dot.vy)
                    jitter = dot.radius * 2
                    x = min(
                        settings.WINDOW_WIDTH - dot.radius,
                        max(dot.radius, dot.x + random.uniform(-jitter, jitter)),
                    )
                    y = min(
                        settings.WINDOW_HEIGHT - dot.radius,
                        max(dot.radius, dot.y + random.uniform(-jitter, jitter)),
                    )
                    prey.append(
                        PreyDot(
                            settings.WINDOW_WIDTH,
                            settings.WINDOW_HEIGHT,
                            vx=vx,
                            vy=vy,
                            x=x,
                            y=y,
                        )
                    )
            last_repro_ms = now_ms
        screen.fill(settings.BACKGROUND_COLOR)
        for dot in prey:
            dot.draw(screen)
        for predator in predators:
            predator.draw(screen)
        for apex in apex_predators:
            apex.draw(screen)
        prey_text = font.render(f"Prey: {len(prey)}", True, (0, 0, 0))
        predator_text = font.render(
            f"Predators: {len(predators)}", True, (0, 0, 0)
        )
        apex_text = font.render(f"Apex: {len(apex_predators)}", True, (0, 0, 0))
        screen.blit(prey_text, (10, 10))
        screen.blit(predator_text, (10, 32))
        screen.blit(apex_text, (10, 54))
        pygame.display.flip()
        clock.tick(settings.FPS)

    getattr(pygame, "quit")()
