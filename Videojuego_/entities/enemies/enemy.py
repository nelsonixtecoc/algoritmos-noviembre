"""Clase base de todos los enemigos."""

import pygame


class Enemy:
    """Enemigo base: se mueve hacia el jugador y le hace daño al tocarlo."""

    def __init__(self, x: float, y: float, hp: int, speed: float,
                damage: int, gold: int, color: tuple, radius: int,
                enemy_type: str = "enemy"):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.gold = gold
        self.color = color
        self.radius = radius
        self.type = enemy_type
        self.alive = True

        # Rect para colisiones (se actualiza en update)
        self.rect = pygame.Rect(0, 0, radius * 2, radius * 2)
        self.rect.center = (round(x), round(y))

    def update(self, dt: float, player_x: float, player_y: float):
        """Mueve al enemigo hacia el player."""
        if not self.alive:
            return

        dx = player_x - self.x
        dy = player_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist > 0:
            dx /= dist
            dy /= dist
            self.x += dx * self.speed * dt
            self.y += dy * self.speed * dt

        self.rect.center = (round(self.x), round(self.y))

    def take_damage(self, amount: int) -> bool:
        """Quita vida. Retorna True si murió."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def draw(self, surface: pygame.Surface):
        """Dibuja el enemigo como un círculo de color."""
        if not self.alive:
            return
        pygame.draw.circle(surface, self.color,
                        (int(self.x), int(self.y)), self.radius)

        # Barra de vida simple encima
        if self.hp < self.max_hp:
            bar_w = 30
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, (64, 64, 64),
                             (self.x - bar_w // 2, self.y - self.radius - 8,
                            bar_w, 4))
            pygame.draw.rect(surface, (0, 255, 0),
                             (self.x - bar_w // 2, self.y - self.radius - 8,
                              int(bar_w * ratio), 4))
