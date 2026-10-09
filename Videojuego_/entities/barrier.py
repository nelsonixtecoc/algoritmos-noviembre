from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence

import pygame

from config import (
    BARRIER_GRID_SIZE,
    BARRIER_MAX_HP,
    DARK_GRAY,
    GREEN,
    HEIGHT,
    RED,
    WIDTH,
    YELLOW,
)

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "barrier"


class Barrier:
    """Barrera defensiva con HP, barra de vida y colocacion en grid.

    Clase autocontenida: no hereda de ``Entity`` mientras
    ``entities/entity.py`` no este disponible.
    """

    SIZE: int = BARRIER_GRID_SIZE
    _SPRITE_CACHE: dict[str, pygame.Surface] = {}

    def __init__(self, x: float, y: float) -> None:
        snapped_x, snapped_y = self.snap_to_grid((x, y))
        self.x: float = float(snapped_x)
        self.y: float = float(snapped_y)
        self.max_hp: int = BARRIER_MAX_HP
        self.hp: int = self.max_hp
        self.alive: bool = True
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = (snapped_x, snapped_y)

    @property
    def hp_ratio(self) -> float:
        """Fraccion de vida restante (0.0 a 1.0)."""
        if self.max_hp <= 0:
            return 0.0
        return max(0.0, self.hp / self.max_hp)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x, self.y)

    @classmethod
    def snap_to_grid(cls, pos: tuple[float, float]) -> tuple[int, int]:
        """Alinea una posicion al centro del grid de tamano ``SIZE``."""
        gx = round(pos[0] / cls.SIZE) * cls.SIZE
        gy = round(pos[1] / cls.SIZE) * cls.SIZE
        return (int(gx), int(gy))

    @classmethod
    def can_place(
        cls,
        pos: tuple[float, float],
        barriers: Optional[Sequence["Barrier"]] = None,
        margin: int = 0,
    ) -> Optional[tuple[int, int]]:
        """Devuelve la posicion alineada al grid si es valida, o ``None``."""
        snapped = cls.snap_to_grid(pos)
        probe = pygame.Rect(0, 0, cls.SIZE + margin * 2, cls.SIZE + margin * 2)
        probe.center = snapped
        if probe.left < 0 or probe.top < 0:
            return None
        if probe.right > WIDTH or probe.bottom > HEIGHT:
            return None
        for barrier in barriers or ():
            if barrier.alive and probe.colliderect(barrier.rect):
                return None
        return snapped

    def take_damage(self, amount: int) -> bool:
        """Reduce HP. Devuelve ``True`` si la barrera fue destruida."""
        if not self.alive or amount <= 0:
            return False
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False
            return True
        return False

    def repair(self, amount: int) -> int:
        """Repara hasta ``amount`` HP y devuelve el HP realmente restaurado."""
        if not self.alive or amount <= 0:
            return 0
        repaired = min(amount, self.max_hp - self.hp)
        self.hp += repaired
        return repaired

    def sprite_name(self) -> str:
        """Selecciona el sprite segun el estado de la barrera."""
        if not self.alive:
            return "destroyed.png"
        ratio = self.hp_ratio
        if ratio > 0.75:
            return "barrier_1.png"
        if ratio > 0.5:
            return "barrier_2.png"
        if ratio > 0.25:
            return "barrier_3.png"
        return "barrier_4.png"

    def sprite(self) -> Optional[pygame.Surface]:
        """Carga (con cache) el sprite correspondiente, o ``None`` si no existe."""
        name = self.sprite_name()
        if name in self._SPRITE_CACHE:
            return self._SPRITE_CACHE[name]
        path = _ASSETS_DIR / name
        if not path.exists():
            return None
        image = pygame.image.load(str(path)).convert_alpha()
        image = pygame.transform.scale(image, (self.SIZE, self.SIZE))
        self._SPRITE_CACHE[name] = image
        return image

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la barrera y su barra de vida."""
        sprite = self.sprite()
        if sprite is not None:
            surface.blit(sprite, self.rect)
        else:
            pygame.draw.rect(surface, DARK_GRAY if self.alive else RED, self.rect)
            pygame.draw.rect(surface, GREEN, self.rect, 1)
        if self.alive:
            self.draw_health_bar(surface)

    def draw_health_bar(self, surface: pygame.Surface) -> None:
        """Dibuja una barra de vida sobre la barrera."""
        ratio = self.hp_ratio
        bar_h = 4
        x = self.rect.left
        y = self.rect.top - bar_h - 2
        pygame.draw.rect(surface, DARK_GRAY, (x, y, self.SIZE, bar_h))
        if ratio > 0.6:
            color = GREEN
        elif ratio > 0.3:
            color = YELLOW
        else:
            color = RED
        pygame.draw.rect(surface, color, (x, y, int(self.SIZE * ratio), bar_h))

    @classmethod
    def default_positions(cls) -> list[tuple[int, int]]:
        """Cuatro posiciones fijas (esquinas de la zona del jugador)."""
        offset_x = 120
        offset_y = 80
        return [
            cls.snap_to_grid((WIDTH // 2 - offset_x, HEIGHT // 2 - offset_y)),
            cls.snap_to_grid((WIDTH // 2 + offset_x, HEIGHT // 2 - offset_y)),
            cls.snap_to_grid((WIDTH // 2 - offset_x, HEIGHT // 2 + offset_y)),
            cls.snap_to_grid((WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y)),
        ]
