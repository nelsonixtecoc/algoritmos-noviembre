from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

import pygame
from config import (
    CYAN,
    GREEN,
    HEALTH_PICKUP_HEAL,
    PICKUP_LIFETIME,
    PICKUP_SIZE,
    RED,
    REPAIR_PICKUP_AMOUNT,
    SPEED_PICKUP_BONUS,
    SPEED_PICKUP_MAX_SPEED,
)

# Ruta a los sprites. pickup.py esta en entities/, entonces parents[1] = Videojuego_
_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


def _get(player, key: str):
    """Lee player[key] si es dict, o player.key si es objeto."""
    return player[key] if isinstance(player, dict) else getattr(player, key)


def _set(player, key: str, value) -> None:
    """Escribe player[key] si es dict, o player.key si es objeto."""
    if isinstance(player, dict):
        player[key] = value
    else:
        setattr(player, key, value)


class Pickup:
    """Objeto recogible por el jugador.

    Es la clase base: define posicion, rect y colision. Cada hija decide
    que efecto hace en ``apply`` y como se ve en ``draw``.
    """

    SIZE: int = PICKUP_SIZE
    # Cache de sprites compartida por todas las hijas (evita recargar de disco).
    _SPRITE_CACHE: ClassVar[dict[str, pygame.Surface]] = {}

    def __init__(self, x: float, y: float) -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.alive: bool = True
        self.age: float = 0.0  # segundos desde que aparecio
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (round(x), round(y))

    def update(self, dt: float) -> None:
        """Suma el tiempo de vida. Al llegar a PICKUP_LIFETIME se desvanece."""
        if not self.alive:
            return
        self.age += dt
        if self.age >= PICKUP_LIFETIME:
            self.alive = False

    @property
    def center(self) -> tuple[float, float]:
        """Centro del pickup (util para partículas o efectos)."""
        return (self.x, self.y)

    def collides(self, player_rect: pygame.Rect) -> bool:
        """Devuelve True si el pickup toca el rect del jugador."""
        return self.rect.colliderect(player_rect)

    def apply(self, player: dict, barriers=None) -> None:
        """Aplica el efecto al diccionario del jugador (game.player).

        ``barriers`` es opcional y solo lo usa ``RepairPickup``.
        Las hijas sobreescriben este metodo.
        """
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el pickup en pantalla. Las hijas sobreescriben esto."""
        raise NotImplementedError

    @classmethod
    def _load_sprite(cls, key: str, path: Path) -> pygame.Surface | None:
        """Carga (con cache) un sprite si existe; si no, devuelve None."""
        if key in cls._SPRITE_CACHE:
            return cls._SPRITE_CACHE[key]
        if not path.exists():
            return None
        image = pygame.image.load(str(path)).convert_alpha()
        image = pygame.transform.scale(image, (cls.SIZE, cls.SIZE))
        cls._SPRITE_CACHE[key] = image
        return image


class HealthPickup(Pickup):
    """Corazon que cura vida sin pasar del maximo (max_hp)."""

    # Sprite existente en assets/sprites/ui/heart_full.png
    _SPRITE = _ASSETS_DIR / "ui" / "heart_full.png"
    _FALLBACK_COLOR = RED

    def apply(self, player: dict, barriers=None) -> None:
        """Suma vida, pero nunca pasa del max_hp."""
        hp = _get(player, "hp")
        max_hp = _get(player, "max_hp")
        _set(player, "hp", min(max_hp, hp + HEALTH_PICKUP_HEAL))

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el corazon, con un rectangulo de respaldo si falta el sprite."""
        sprite = self._load_sprite("health", self._SPRITE)
        if sprite is not None:
            surface.blit(sprite, self.rect)
            return
        # Si no existe el sprite, rectangulo rojo de respaldo.
        pygame.draw.rect(surface, self._FALLBACK_COLOR, self.rect)


class SpeedPickup(Pickup):
    """Rayo que sube la velocidad del jugador."""

    # Sprite del rayo; si falta el archivo se usa un rectángulo de color de respaldo.
    _SPRITE = _ASSETS_DIR / "ui" / "lightning.png"
    _FALLBACK_COLOR = CYAN

    def apply(self, player: dict, barriers=None) -> None:
        """Aumenta la velocidad sin superar SPEED_PICKUP_MAX_SPEED.

        Si la velocidad actual ya alcanzó el tope, no se modifica.
        """
        current = _get(player, "speed")
        if current >= SPEED_PICKUP_MAX_SPEED:
            return
        _set(player, "speed", min(current + SPEED_PICKUP_BONUS, SPEED_PICKUP_MAX_SPEED))

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el rayo, con un rectangulo de respaldo si falta el sprite."""
        sprite = self._load_sprite("speed", self._SPRITE)
        if sprite is not None:
            surface.blit(sprite, self.rect)
            return
        # Sin sprite disponible: rectangulo cian de respaldo.
        pygame.draw.rect(surface, self._FALLBACK_COLOR, self.rect)


class RepairPickup(Pickup):
    """Herramienta que repara la barrera viva con menos vida."""

    # No existe sprite de reparacion todavia -> se usa rectangulo de color.
    _SPRITE = _ASSETS_DIR / "pickups" / "repair.png"
    _FALLBACK_COLOR = GREEN

    def apply(self, player, barriers=None) -> None:
        """Repara la barrera viva con menor proporcion de vida."""
        if not barriers:
            return
        target = None
        for barrier in barriers:
            if not barrier.alive or barrier.hp >= barrier.max_hp:
                continue
            if target is None or barrier.hp / barrier.max_hp < target.hp / target.max_hp:
                target = barrier
        if target is not None:
            target.repair(REPAIR_PICKUP_AMOUNT)

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la herramienta, con un rectangulo de respaldo si falta el sprite."""
        sprite = self._load_sprite("repair", self._SPRITE)
        if sprite is not None:
            surface.blit(sprite, self.rect)
            return
        # Sin sprite disponible: rectangulo verde de respaldo.
        pygame.draw.rect(surface, self._FALLBACK_COLOR, self.rect)
