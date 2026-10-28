"""Enemigo básico: equilibrado."""

from entities.enemies.enemy import Enemy
from config import ENEMY_BASIC_HP, ENEMY_BASIC_SPEED, ENEMY_BASIC_DAMAGE, ENEMY_BASIC_GOLD


class Basic(Enemy):
    """Enemigo estándar."""

    def __init__(self, x: float, y: float):
        super().__init__(
            x=x, y=y,
            hp=ENEMY_BASIC_HP,
            speed=ENEMY_BASIC_SPEED,
            damage=ENEMY_BASIC_DAMAGE,
            gold=ENEMY_BASIC_GOLD,
            color=(200, 50, 50),
            radius=16,
            enemy_type="basic",
        )
