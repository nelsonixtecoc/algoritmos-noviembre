from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from config import (
    PARTICLE_DEFAULT_SIZE,
    PARTICLE_DEFAULT_SPEED,
    PARTICLE_FADE_OUT,
    PARTICLE_LIFETIME,
    PARTICLE_POOL_SIZE,
    PARTICLE_SPRITE_SIZE_MULT,
)


# Ruta a los sprites de partículas. systems/ -> Videojuego_/assets/sprites/particles
_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "particles"


class Particle:
    """Partícula simple reutilizable en el object pool.

    Propiedades básicas:
    - active: indica si la partícula está en uso
    - x, y: posición
    - velocidad: magnitud o se puede usar vx, vy
    - vida: tiempo de vida restante (segundos)
    - sprite: superficie opcional con el sprite cargado
    """

    def __init__(self) -> None:
        self.active: bool = False
        self.x: float = 0.0
        self.y: float = 0.0
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.velocidad: float = PARTICLE_DEFAULT_SPEED
        self.vida: float = PARTICLE_LIFETIME
        self.vida_max: float = PARTICLE_LIFETIME
        self.size: int = PARTICLE_DEFAULT_SIZE
        self.color: Tuple[int, int, int] = (255, 255, 255)
        self.sprite: Optional[pygame.Surface] = None
        self.sprite_key: Optional[str] = None

    def reset(self) -> None:
        """Reinicia la partícula para volver a usarla."""
        self.active = False
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.velocidad = PARTICLE_DEFAULT_SPEED
        self.vida = PARTICLE_LIFETIME
        self.vida_max = PARTICLE_LIFETIME
        self.size = PARTICLE_DEFAULT_SIZE
        self.color = (255, 255, 255)
        self.sprite = None
        self.sprite_key = None

    def update(self, dt: float) -> None:
        """Actualiza la posición y la vida de la partícula."""
        if not self.active:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vida -= dt
        if self.vida <= 0.0:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la partícula si está activa."""
        if not self.active:
            return
        if self.sprite is not None:
            # Dibuja el sprite centrado en (x,y)
            rect = self.sprite.get_rect(center=(int(round(self.x)), int(round(self.y))))
            surface.blit(self.sprite, rect)
            return
        # Rectángulo de color si no hay sprite
        rect = pygame.Rect(0, 0, self.size, self.size)
        rect.center = (int(round(self.x)), int(round(self.y)))
        pygame.draw.rect(surface, self.color, rect)


class ParticlePool:
    """Object pool de partículas con reutilización.

    Crea PARTICLE_POOL_SIZE partículas al inicio. 
    - emit(x,y,tipo): despierta una libre; si no hay, la ignora.
    - update(dt): mueve las activas y duerme las que terminan.
    - draw(surface): dibuja las activas.
    """

    # Caché de sprites compartido
    _SPRITE_CACHE: Dict[str, pygame.Surface] = {}

    def __init__(self) -> None:
        self.size: int = PARTICLE_POOL_SIZE
        self.particles: List[Particle] = []
        for _ in range(self.size):
            self.particles.append(Particle())
        # Tipos de partículas soportados y sus colores de respaldo
        self._tipo_colores: Dict[str, Tuple[int, int, int]] = {
            "spark": (255, 255, 0),  # amarillo
            "smoke": (128, 128, 128),  # gris
            "blood": (255, 0, 0),  # rojo
            "ring": (0, 255, 255),  # cian
        }

    def get_free_particle(self) -> Optional[Particle]:
        """Devuelve la primera partícula libre, o None si todas están activas."""
        for p in self.particles:
            if not p.active:
                return p
        return None

    def emit(self, x: float, y: float, tipo: str) -> bool:
        """Despierta una partícula libre en (x,y) del tipo indicado.

        Si no hay partículas libres, la ignora (devuelve False).
        """
        p = self.get_free_particle()
        if p is None:
            return False
        # Reset
        p.reset()
        p.active = True
        p.x = float(x)
        p.y = float(y)
        p.vida = PARTICLE_LIFETIME
        p.vida_max = PARTICLE_LIFETIME

        tipo_norm = tipo.lower().strip() if tipo else "spark"
        # Velocidad aleatoria en un cono pequeño
        ang = random.uniform(0.0, math.tau)
        speed = random.uniform(PARTICLE_DEFAULT_SPEED * 0.5, PARTICLE_DEFAULT_SPEED * 1.5)
        p.velocidad = speed
        p.vx = math.cos(ang) * speed
        p.vy = math.sin(ang) * speed

        # Tamaño base
        p.size = PARTICLE_DEFAULT_SIZE

        # Cargar sprite si existe
        sprite = self._load_sprite(tipo_norm)
        if sprite is not None:
            p.sprite = sprite
            p.sprite_key = tipo_norm
        else:
            # Color de respaldo
            p.color = self._tipo_colores.get(tipo_norm, (255, 255, 255))

        return True

    @classmethod
    def _load_sprite(cls, tipo: str) -> Optional[pygame.Surface]:
        """Carga (con caché) un sprite si existe; si no, devuelve None."""
        key = tipo.lower().strip()
        if key in cls._SPRITE_CACHE:
            return cls._SPRITE_CACHE[key]
        path = _ASSETS_DIR / f"{key}.png"
        if not path.exists():
            return None
        try:
            image = pygame.image.load(str(path)).convert_alpha()
            # Escala según multiplicador si se desea (constante)
            base_size = max(1, PARTICLE_DEFAULT_SIZE)
            target = max(1, int(round(base_size * PARTICLE_SPRITE_SIZE_MULT)))
            if image.get_width() != target or image.get_height() != target:
                image = pygame.transform.scale(image, (target, target))
            cls._SPRITE_CACHE[key] = image
            return image
        except Exception:
            return None

    def update(self, dt: float) -> None:
        """Actualiza todas las partículas activas y duerme las que terminan."""
        for p in self.particles:
            if not p.active:
                continue
            p.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja todas las partículas activas."""
        for p in self.particles:
            if not p.active:
                continue
            p.draw(surface)
