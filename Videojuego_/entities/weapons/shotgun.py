"""Escopeta - Arma de dispersión: múltiples perdigones, cooldown alto, spread amplio."""

import math
import random
from typing import List
from entities.weapons.weapon import Weapon, ProjectileFactory
from entities.projectile import Projectile
from config import *


class Shotgun(Weapon):
    name: str = "shotgun"
    cooldown: float = WEAPON_SHOTGUN_COOLDOWN
    damage: int = WEAPON_SHOTGUN_DAMAGE
    spread: float = WEAPON_SHOTGUN_SPREAD
    projectile_speed: float = WEAPON_SHOTGUN_PROJECTILE_SPEED
    pellets: int = WEAPON_SHOTGUN_PELLETS
    pierce: int = 0
    explosion_radius: float = 0.0
    color: tuple = ORANGE
    
    # Visual
    muzzle_flash_duration: float = 0.08
    recoil_amount: float = 12.0
    screen_shake_intensity: float = 3.0
    
    def fire(self, x: float, y: float, angle: float, damage_mult: float = 1.0,
            cooldown_mult: float = 1.0, spread_mult: float = 1.0,
            speed_mult: float = 1.0, pierce_bonus: int = 0) -> List[Projectile]:
        
        return ProjectileFactory.create_spread_projectiles(
            self, x, y, angle, damage_mult, speed_mult, spread_mult, pierce_bonus
        )