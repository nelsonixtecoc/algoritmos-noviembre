"""Clase base abstracta para armas (Strategy Pattern)."""

from abc import ABC, abstractmethod
from typing import List, Optional
import pygame
import math
from entities.projectile import Projectile
from config import *


class Weapon(ABC):
    """Arma base - define interfaz común para todas las armas."""
    
    # Stats base (sobrescribir en subclases)
    name: str = "base"
    cooldown: float = 1.0
    damage: int = 10
    spread: float = 0.0
    projectile_speed: float = 500.0
    pellets: int = 1
    pierce: int = 0
    explosion_radius: float = 0.0
    color: tuple = (255, 255, 255)
    
    # Ammo system (opcional)
    max_ammo: int = -1  # -1 = infinito
    ammo: int = -1
    reload_time: float = 2.0
    
    # Visual/feedback
    muzzle_flash_duration: float = 0.05
    recoil_amount: float = 5.0
    screen_shake_intensity: float = 0.0
    
    # Sound hooks (sobrescribir con paths reales)
    shoot_sound: Optional[str] = None
    reload_sound: Optional[str] = None
    empty_sound: Optional[str] = None
    
    def __init__(self):
        self.last_shot_time: float = 0.0
        self._cooldown_timer: float = 0.0
        self._reloading: bool = False
        self._reload_timer: float = 0.0
        self._muzzle_flash_timer: float = 0.0
        self._recoil_offset: float = 0.0
    
    @abstractmethod
    def fire(self, x: float, y: float, angle: float, damage_mult: float = 1.0, 
            cooldown_mult: float = 1.0, spread_mult: float = 1.0, 
            speed_mult: float = 1.0, pierce_bonus: int = 0) -> List[Projectile]:
        """
        Dispara el arma y retorna lista de proyectiles creados.
        
        Args:
            x, y: Posición de spawn
            angle: Ángulo en radianes
            damage_mult: Multiplicador de daño (upgrades)
            cooldown_mult: Multiplicador de cooldown (upgrades)
            spread_mult: Multiplicador de spread (upgrades)
            speed_mult: Multiplicador de velocidad (upgrades)
            pierce_bonus: Perforación extra (upgrades)
            
        Returns:
            Lista de Projectile creados
        """
        pass
    
    def can_fire(self, current_time: float, cooldwn_mult: float = 1.0) -> bool:
        """Verifica si el arma puede disparar (cooldown listo y tiene munición)."""
        if self._reloading:
            return False
        if self.max_ammo > 0 and self.ammo <= 0:
            return False
        return current_time - self.last_shot_time >= self.get_effective_cooldown(cooldwn_mult)
    
    def get_effective_cooldown(self, cooldown_mult: float = 1.0) -> float:
        """Cooldown efectivo con multiplicador."""
        return self.cooldown * cooldown_mult
    
    def reset_cooldown(self, current_time: float):
        """Resetea el timer de cooldown."""
        self.last_shot_time = current_time
    
    def reload(self, current_time: float) -> bool:
        """
        Inicia recarga. Retorna True si empezó a recargar.
        """
        if self.max_ammo <= 0 or self.ammo >= self.max_ammo or self._reloading:
            return False
        self._reloading = True
        self._reload_timer = self.reload_time
        return True
    
    def update(self, dt: float, current_time: float):
        """Actualiza timers internos (llamar cada frame)."""
        # Cooldown
        if self._cooldown_timer > 0:
            self._cooldown_timer -= dt
        
        # Recarga
        if self._reloading:
            self._reload_timer -= dt
            if self._reload_timer <= 0:
                self.ammo = self.max_ammo
                self._reloading = False
        
        # Muzzle flash
        if self._muzzle_flash_timer > 0:
            self._muzzle_flash_timer -= dt
        
        # Recoil recovery
        if self._recoil_offset > 0:
            self._recoil_offset = max(0, self._recoil_offset - dt * 30)
    
    def trigger_muzzle_flash(self):
        """Activa flash de boca de cañón."""
        self._muzzle_flash_timer = self.muzzle_flash_duration
    
    def get_recoil_offset(self) -> float:
        """Retorna offset de retroceso actual para render."""
        return self._recoil_offset
    
    def is_muzzle_flashing(self) -> bool:
        return self._muzzle_flash_timer > 0
    
    def get_stats_dict(self) -> dict:
        """Retorna stats para UI/HUD."""
        return {
            "name": self.name,
            "cooldown": self.cooldown,
            "damage": self.damage,
            "spread": self.spread,
            "projectile_speed": self.projectile_speed,
            "pellets": self.pellets,
            "pierce": self.pierce,
            "explosion_radius": self.explosion_radius,
            "color": self.color,
            "ammo": self.ammo,
            "max_ammo": self.max_ammo,
            "reloading": self._reloading,
        }
    
    def _create_base_projectile(self, x: float, y: float, vx: float, vy: float,
                                damage: int, pierce: int, color: tuple) -> Projectile:
        """Helper para crear proyectil base con stats comunes."""
        return Projectile(
            x=x, y=y,
            vx=vx, vy=vy,
            damage=damage,
            pierce=pierce,
            explosion_radius=self.explosion_radius,
            color=color,
            owner="player"
        )


class ProjectileFactory:
    """Factory para crear proyectiles con variaciones."""
    
    @staticmethod
    def create_spread_projectiles(weapon: Weapon, x: float, y: float, angle: float,
                                damage_mult: float, speed_mult: float,
                                spread_mult: float, pierce_bonus: int) -> List[Projectile]:
        """Crea múltiples proyectiles con spread."""
        projectiles = []
        for _ in range(weapon.pellets):
            spread_angle = angle + __import__('random').uniform(
                -weapon.spread * spread_mult, weapon.spread * spread_mult
            )
            vx = math.cos(spread_angle) * weapon.projectile_speed * speed_mult
            vy = math.sin(spread_angle) * weapon.projectile_speed * speed_mult
            
            spawn_x = x + math.cos(spread_angle) * 20
            spawn_y = y + math.sin(spread_angle) * 20
            
            proj = weapon._create_base_projectile(
                spawn_x, spawn_y, vx, vy,
                damage=int(weapon.damage * damage_mult),
                pierce=weapon.pierce + pierce_bonus,
                color=weapon.color
            )
            projectiles.append(proj)
        return projectiles