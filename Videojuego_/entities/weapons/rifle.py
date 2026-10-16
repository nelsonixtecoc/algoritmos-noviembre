"""Rifle - Arma de precisión: 1 bala rápida, cooldown bajo, perfora enemigos."""

import math
import random
from typing import List
from entities.weapons.weapon import Weapon, ProjectileFactory
from entities.projectile import Projectile
from config import *


class Rifle(Weapon):
    name: str = "rifle"
    cooldown: float = WEAPON_RIFLE_COOLDOWN
    damage: int = WEAPON_RIFLE_DAMAGE
    spread: float = WEAPON_RIFLE_SPREAD
    projectile_speed: float = WEAPON_RIFLE_PROJECTILE_SPEED
    pellets: int = 1
    pierce: int = WEAPON_RIFLE_PIERCE
    explosion_radius: float = 0.0
    color: tuple = CYAN
    
    # Visual
    muzzle_flash_duration: float = 0.03
    recoil_amount: float = 5.0
    screen_shake_intensity: float = 1.5
    
    def fire(self, x: float, y: float, angle: float, damage_mult: float = 1.0,
             cooldown_mult: float = 1.0, spread_mult: float = 1.0,
             speed_mult: float = 1.0, pierce_bonus: int = 0) -> List[Projectile]:
        
        return ProjectileFactory.create_spread_projectiles(
            self, x, y, angle, damage_mult, speed_mult, spread_mult, pierce_bonus
        )