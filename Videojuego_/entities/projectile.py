"""Clase base para proyectiles - usado por el sistema de armas Strategy Pattern."""

import pygame
import math
import random
from typing import Tuple, Optional, List
from config import *


class Projectile:
    """Proyectil base con física simple, lifetime, sprites y efectos."""
    
    # Class-level sprite cache
    _sprite_cache: dict = {}
    
    def __init__(self, x: float, y: float, vx: float, vy: float,
                damage: int, pierce: int = 0, explosion_radius: float = 0.0,
                color: Tuple[int, int, int] = (255, 255, 255),
                radius: int = 4, owner: str = "player",
                lifetime: float = 3.0, sprite_name: Optional[str] = None):
        
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.damage: int = damage
        self.pierce: int = pierce
        self.explosion_radius: float = explosion_radius
        self.color: Tuple[int, int, int] = color
        self.radius: int = radius
        self.owner: str = owner  # "player" o "enemy"
        self.lifetime: float = lifetime
        self.max_lifetime: float = lifetime
        self.alive: bool = True
        
        # Sprite
        self.sprite_name: Optional[str] = sprite_name
        self.sprite: Optional[pygame.Surface] = None
        self._load_sprite()
        
        # Trail effect
        self.trail_points: List[Tuple[float, float]] = []
        self.max_trail_length: int = 8
        self.trail_timer: float = 0.0
        self.trail_interval: float = 0.02
        
        # Explosion
        self.exploding: bool = False
        self.explosion_timer: float = 0.0
        self.explosion_duration: float = 0.3
        self.explosion_max_radius: float = explosion_radius
        
        # Rect para colisiones
        self.rect = pygame.Rect(
            int(x - radius), int(y - radius), 
            radius * 2, radius * 2
        )
        
        # Rotation para sprite
        self.angle: float = math.atan2(vy, vx) if (vx != 0 or vy != 0) else 0
    
    def _load_sprite(self):
        """Carga sprite desde assets (con cache)."""
        if self.sprite_name and self.sprite_name in Projectile._sprite_cache:
            self.sprite = Projectile._sprite_cache[self.sprite_name]
            return
        
        if self.sprite_name:
            try:
                path = f"assets/sprites/weapons/projectiles/{self.sprite_name}"
                sprite = pygame.image.load(path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (self.radius * 2, self.radius * 2))
                Projectile._sprite_cache[self.sprite_name] = sprite
                self.sprite = sprite
            except (pygame.error, FileNotFoundError):
                self.sprite = None
    
    @property
    def pos(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def update(self, dt: float):
        """Actualiza posición, lifetime, trail y explosión."""
        if not self.alive:
            return
        
        # Movimiento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Actualizar ángulo para sprite rotado
        if self.vx != 0 or self.vy != 0:
            self.angle = math.atan2(self.vy, self.vx)
        
        # Actualizar rect
        self.rect.center = (int(self.x), int(self.y))
        
        # Trail effect
        self.trail_timer += dt
        if self.trail_timer >= self.trail_interval:
            self.trail_points.append((self.x, self.y))
            if len(self.trail_points) > self.max_trail_length:
                self.trail_points.pop(0)
            self.trail_timer = 0.0
        
        # Lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
        
        # Explosión
        if self.exploding:
            self.explosion_timer += dt
            if self.explosion_timer >= self.explosion_duration:
                self.alive = False
    
    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        """Dibuja el proyectil con sprite, trail y explosión."""
        if not self.alive:
            return
        
        ox, oy = camera_offset
        draw_x = int(self.x - ox)
        draw_y = int(self.y - oy)
        
        # Trail
        if len(self.trail_points) > 1:
            trail_color = (*self.color, 128)
            for i, (tx, ty) in enumerate(self.trail_points):
                alpha = int(255 * (i / len(self.trail_points)))
                size = max(1, int(self.radius * (i / len(self.trail_points))))
                tx_int = int(tx - ox)
                ty_int = int(ty - oy)
                pygame.draw.circle(surface, self.color, (tx_int, ty_int), size)
        
        # Proyectil principal
        if self.exploding:
            # Explosión expanding
            progress = self.explosion_timer / self.explosion_duration
            current_radius = int(self.explosion_max_radius * progress)
            alpha = int(255 * (1 - progress))
            explosion_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surface, (*self.color, alpha), (current_radius, current_radius), current_radius)
            surface.blit(explosion_surface, (draw_x - current_radius, draw_y - current_radius))
        elif self.sprite:
            # Sprite rotado
            rotated = pygame.transform.rotate(self.sprite, -math.degrees(self.angle))
            rect = rotated.get_rect(center=(draw_x, draw_y))
            surface.blit(rotated, rect)
        else:
            # Fallback círculo
            pygame.draw.circle(surface, self.color, (draw_x, draw_y), self.radius)
    
    def is_off_screen(self, width: int = WIDTH, height: int = HEIGHT, margin: int = 50) -> bool:
        """Verifica si el proyectil salió de pantalla."""
        return (self.x < -margin or self.x > width + margin or
                self.y < -margin or self.y > height + margin)
    
    def on_hit(self) -> bool:
        """
        Llamado cuando el proyectil impacta algo.
        Retorna True si el proyectil debe destruirse, False si puede continuar (pierce).
        """
        if self.pierce > 0:
            self.pierce -= 1
            return False  # Sigue vivo
        
        # Si tiene explosión, inicia explosión en lugar de morir instantáneo
        if self.explosion_radius > 0:
            self.exploding = True
            self.explosion_timer = 0.0
            self.vx = 0
            self.vy = 0
            return False  # Se destruirá cuando termine explosión
        
        return True  # Se destruye
    
    def trigger_explosion(self):
        """Fuerza explosión inmediata (para impacto con pared, etc)."""
        if self.explosion_radius > 0:
            self.exploding = True
            self.explosion_timer = 0.0
            self.vx = 0
            self.vy = 0
    
    def get_rect(self) -> pygame.Rect:
        return self.rect
    
    def get_damage_area(self) -> pygame.Rect:
        """Retorna rect del área de daño (para explosiones)."""
        if self.exploding:
            r = int(self.explosion_max_radius * (self.explosion_timer / self.explosion_duration))
            return pygame.Rect(
                int(self.x - r), int(self.y - r), r * 2, r * 2
            )
        return self.rect
    
    @classmethod
    def clear_cache(cls):
        """Limpia cache de sprites (llamar al salir)."""
        cls._sprite_cache.clear()


# Factory functions para crear proyectiles estándar
def create_bullet(x: float, y: float, angle: float, speed: float, damage: int, 
                color: Tuple[int, int, int] = YELLOW, pierce: int = 0) -> Projectile:
    """Crea una bala estándar (pistola/rifle)."""
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    return Projectile(x, y, vx, vy, damage, pierce=pierce, color=color, 
                    sprite_name="bullet.png", radius=4)

def create_pellet(x: float, y: float, angle: float, speed: float, damage: int,
                color: Tuple[int, int, int] = ORANGE) -> Projectile:
    """Crea un perdigón de escopeta."""
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    return Projectile(x, y, vx, vy, damage, pierce=0, color=color,
                    sprite_name="pellet.png", radius=3)

def create_rocket(x: float, y: float, angle: float, speed: float, damage: int,
                explosion_radius: float = 60.0) -> Projectile:
    """Crea un cohete explosivo."""
    vx = math.cos(angle) * speed
    vy = math.sin(angle) * speed
    return Projectile(x, y, vx, vy, damage, pierce=0, 
                    explosion_radius=explosion_radius, color=RED,
                    sprite_name="rocket.png", radius=8)