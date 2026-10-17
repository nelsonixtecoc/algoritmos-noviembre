"""Pistola - Arma base: 1 bala, cooldown medio, sin spread, munición infinita."""

import math
import random
from typing import List
from entities.weapons.weapon import Weapon, ProjectileFactory
from entities.projectile import Projectile
from config import *


class Pistol(Weapon):
    name: str = "pistol"
    cooldown: float = WEAPON_PISTOL_COOLDOWN
    damage: int = WEAPON_PISTOL_DAMAGE
    spread: float = WEAPON_PISTOL_SPREAD
    projectile_speed: float = WEAPON_PISTOL_PROJECTILE_SPEED
    pellets: int = 1
    pierce: int = 0
    explosion_radius: float = 0.0
    color: tuple = YELLOW
    
    # Visual
    muzzle_flash_duration: float = 0.04
    recoil_amount: float = 3.0
    screen_shake_intensity: float = 1.0
    
    def fire(self, x: float, y: float, angle: float, damage_mult: float = 1.0,
            cooldown_mult: float = 1.0, spread_mult: float = 1.0,
            speed_mult: float = 1.0, pierce_bonus: int = 0) -> List[Projectile]:
        
        return ProjectileFactory.create_spread_projectiles(
            self, x, y, angle, damage_mult, speed_mult, spread_mult, pierce_bonus
        )