"""Enemigo speedy: poca vida, muy rápido."""

from entities.enemies.enemy import Enemy
from config import ENEMY_SPEEDY_HP, ENEMY_SPEEDY_SPEED, ENEMY_SPEEDY_DAMAGE, ENEMY_SPEEDY_GOLD


class Speedy(Enemy):
    """Enemigo rápido y frágil."""

    def __init__(self, x: float, y: float):
        super().__init__(
            x=x, y=y,
            hp=ENEMY_SPEEDY_HP,
            speed=ENEMY_SPEEDY_SPEED,
            damage=ENEMY_SPEEDY_DAMAGE,
            gold=ENEMY_SPEEDY_GOLD,
            color=(50, 200, 50),
            radius=12,
            enemy_type="speedy",
        )
