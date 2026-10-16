"""Enemigo tanque: mucha vida, lento, hace más daño."""

from entities.enemies.enemy import Enemy
from config import ENEMY_TANK_HP, ENEMY_TANK_SPEED, ENEMY_TANK_DAMAGE, ENEMY_TANK_GOLD


class Tank(Enemy):
    """Enemigo tanque."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(
            x=x, y=y,
            hp=ENEMY_TANK_HP,
            speed=ENEMY_TANK_SPEED,
            damage=ENEMY_TANK_DAMAGE,
            gold=ENEMY_TANK_GOLD,
            color=(100, 100, 200),
            radius=20,
            enemy_type="tank",
        )
