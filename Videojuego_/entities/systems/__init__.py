"""Systems package - sistemas desacoplados de combate, oleadas, etc."""

from entities.systems.combat import (
    apply_damage,
    check_projectile_collisions,
    check_player_enemy_collision,
    register_screen_shake,
    register_flash_callback,
)

__all__ = [
    "apply_damage",
    "check_projectile_collisions",
    "check_player_enemy_collision",
    "register_screen_shake",
    "register_flash_callback",
]
