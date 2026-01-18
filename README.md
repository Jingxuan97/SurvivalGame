# Predator-Prey Dots (Pygame)

A simple pygame simulation of prey, predators, and an apex predator using
Brownian-like motion and probabilistic interactions.

## Requirements

- Python 3.9+
- `pygame` (see `requirements.txt`)

Install:

```bash
python3 -m pip install -r /Users/jingxuanyang/Projects/Game/requirements.txt
```

## Run

```bash
python3 /Users/jingxuanyang/Projects/Game/main.py
```

## Controls

- Close the window to quit.

## Configuration

Tune behavior in `game/settings.py`:

- **Counts:** `PREY_COUNT`, `PREDATOR_COUNT`, `APEX_PREDATOR_COUNT`
- **Motion:** `DOT_SPEED`, `BROWNIAN_ANGLE_DEGREES`, `VELOCITY_STD`
- **Prey reproduction:** `PREY_REPRO_INTERVAL_MS`, `PREY_REPRO_PROB`, `PREY_VELOCITY_STD`
- **Predator eating:** `EAT_RADIUS`, `EAT_PROBABILITY`, `EAT_COOLDOWN_MS`
- **Predator starvation:** `STARVE_AFTER_MS`, `STARVE_CHECK_MS`, `STARVE_PROBABILITY`
- **Predator reproduction:** `PREDATOR_REPRO_RADIUS`, `PREDATOR_REPRO_PAUSE_MS`,
  `PREDATOR_REPRO_PROBS`
- **Apex predator:** `APEX_EAT_RADIUS`, `APEX_EAT_PROBABILITY`,
  `APEX_PAUSE_MS`, `APEX_EAT_COOLDOWN_MS`
- **Rendering:** `BACKGROUND_COLOR`, `DOT_COLOR`, `PREDATOR_COLOR`,
  `APEX_PREDATOR_COLOR`

## Behavior Summary

- Prey wander with Brownian-like motion and can reproduce over time.
- Predators can eat prey after a cooldown; after eating they may later reproduce
  only when meeting another predator.
- Predators can starve if they go too long without eating.
- Apex predators can eat both prey and predators.
