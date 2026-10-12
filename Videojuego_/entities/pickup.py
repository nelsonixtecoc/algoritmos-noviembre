from __future__ import annotations

from pathlib import Path
from typing import Optional

import pygame

from config import (
    CYAN,
    HEALTH_PICKUP_HEAL,
    PICKUP_SIZE,
    RED,
    SPEED_PICKUP_BONUS,
)

# Ruta a los sprites. pickup.py esta en entities/, entonces parents[1] = Videojuego_
_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites"


class Pickup:
    """Objeto recogible por el jugador.

    Es la clase base: define posicion, rect y colision. Cada hija decide
    que efecto hace en ``apply`` y como se ve en ``draw``.
    """

    SIZE: int = PICKUP_SIZE
    # Cache de sprites compartida por todas las hijas (evita recargar de disco).
    _SPRITE_CACHE: dict[str, pygame.Surface] = {}

    def __init__(self, x: float, y: float) -> None:
        self.x: float = float(x)
        self.y: float = float(y)
        self.alive: bool = True
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (round(x), round(y))

    @property
    def center(self) -> tuple[float, float]:
        """Centro del pickup (util para partículas o efectos)."""
        return (self.x, self.y)

    def collides(self, player_rect: pygame.Rect) -> bool:
        """Devuelve True si el pickup toca el rect del jugador."""
        return self.rect.colliderect(player_rect)

    def apply(self, player: dict) -> None:
        """Aplica el efecto al diccionario del jugador (game.player).

        Las hijas sobreescriben este metodo.
        """
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el pickup en pantalla. Las hijas sobreescriben esto."""
        raise NotImplementedError

    @classmethod
    def _load_sprite(cls, key: str, path: Path) -> Optional[pygame.Surface]:
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

    def apply(self, player: dict) -> None:
        """Suma vida, pero nunca pasa de player['max_hp']."""
        player["hp"] = min(player["max_hp"], player["hp"] + HEALTH_PICKUP_HEAL)

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self._load_sprite("health", self._SPRITE)
        if sprite is not None:
            surface.blit(sprite, self.rect)
            return
        # Si no existe el sprite, rectangulo rojo de respaldo.
        pygame.draw.rect(surface, self._FALLBACK_COLOR, self.rect)


class SpeedPickup(Pickup):
    """Rayo que sube la velocidad del jugador."""

    # No existe sprite de velocidad todavia -> se usa rectangulo de color.
    _SPRITE = _ASSETS_DIR / "ui" / "speed.png"
    _FALLBACK_COLOR = CYAN

    def apply(self, player: dict) -> None:
        """Aumenta la velocidad base del jugador."""
        player["speed"] += SPEED_PICKUP_BONUS

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self._load_sprite("speed", self._SPRITE)
        if sprite is not None:
            surface.blit(sprite, self.rect)
            return
        # Sin sprite disponible: rectangulo cian de respaldo.
        pygame.draw.rect(surface, self._FALLBACK_COLOR, self.rect)
