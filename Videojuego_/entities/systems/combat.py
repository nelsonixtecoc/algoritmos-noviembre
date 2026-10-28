"""Sistema de combate desacoplado - funciones puras para daño, colisiones, efectos."""

import math
import pygame
import random
from typing import List, Tuple, Optional, Callable
from entities.projectile import Projectile
from config import *
from core.events import event_bus, EventType

# CALLBACKS PARA EFECTOS VISUALES (se registran desde game.py)

_screen_shake_callback: Optional[Callable[[float, float], None]] = None
_flash_callback: Optional[Callable[[object, float], None]] = None


def register_screen_shake(callback: Callable[[float, float], None]):
    """Registra callback para screen shake: callback(intensity, duration)."""
    global _screen_shake_callback
    _screen_shake_callback = callback


def register_flash_callback(callback: Callable[[object, float], None]):
    """Registra callback para flash visual: callback(entity, duration)."""
    global _flash_callback
    _flash_callback = callback


def _trigger_screen_shake(intensity: float, duration: float = 0.2):
    if _screen_shake_callback:
        _screen_shake_callback(intensity, duration)


def _trigger_flash(entity: object, duration: float = 0.1):
    if _flash_callback:
        _flash_callback(entity, duration)


# Helpers para leer/escribir atributos en objetos (Enemy) o diccionarios (player)
def _get_attr(obj: object, key: str, default=None):
    """Lee un atributo si es objeto, o una clave si es diccionario."""
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default


def _set_attr(obj: object, key: str, value):
    """Escribe un atributo si es objeto, o una clave si es diccionario."""
    if hasattr(obj, key):
        setattr(obj, key, value)
    else:
        obj[key] = value

# DAÑO Y COMBATE

def apply_damage(attacker: dict, target: dict, amount: int, 
                knockback: float = 0.0, knockback_resist: float = 0.0,
                damage_type: str = "normal") -> bool:
    """
    Aplica daño a un objetivo y maneja knockback, flash, eventos.
    
    Args:
        attacker: Dict del atacante (para eventos)
        target: Dict del objetivo (debe tener 'hp', 'invuln_timer', 'x', 'y', 'alive')
        amount: Cantidad de daño base
        knockback: Fuerza de retroceso en píxeles
        knockback_resist: Resistencia al knockback [0.0, 1.0]
        damage_type: "normal", "critical", "explosion", "fire", etc.
    
    Returns:
        True si el objetivo murió, False en caso contrario
    """
    # Verificar invulnerabilidad
    if _get_attr(target, "invuln_timer", 0) > 0:
        return False
    
    # Verificar si está vivo
    if not _get_attr(target, "alive", True):
        return False
    
    # Aplicar daño
    old_hp = _get_attr(target, "hp", 0)
    _set_attr(target, "hp", max(0, old_hp - amount))
    
    # Invulnerabilidad post-daño SOLO para player (tiene "weapon" key)
    # Enemigos NO reciben invulnerabilidad para permitir multi-hit
    if _get_attr(target, "weapon", None) is not None:
        _set_attr(target, "invuln_timer", PLAYER_INVULN_TIME)
    
    # Knockback
    if knockback > 0 and knockback_resist < 1.0:
        if _get_attr(attacker, "x", None) is not None and _get_attr(attacker, "y", None) is not None:
            resolve_knockback(target, _get_attr(attacker, "x"), _get_attr(attacker, "y"), knockback, knockback_resist)
    
    # Flash visual
    _trigger_flash(target, 0.1)
    
    # Screen shake leve
    _trigger_screen_shake(2.0, 0.1)
    
    # Evento de daño (solo el jugador tiene un evento propio de "dañado";
    # ENEMY_DIED se publica más abajo, únicamente cuando el enemigo muere de verdad)
    if _get_attr(target, "weapon", None) is not None:
        event_bus.publish(EventType.PLAYER_DAMAGED, {
            "attacker": attacker,
            "target": target,
            "damage": amount,
            "damage_type": damage_type,
            "old_hp": old_hp,
            "new_hp": _get_attr(target, "hp")
        })
    
    # Verificar muerte
    if _get_attr(target, "hp") <= 0:
        _set_attr(target, "hp", 0)
        _set_attr(target, "alive", False)
        
        # Screen shake mayor
        _trigger_screen_shake(5.0, 0.3)
        
        event_bus.publish(EventType.ENEMY_DIED if _get_attr(target, "weapon", None) is None else EventType.PLAYER_DIED, {
            "entity": target,
            "killer": attacker,
            "gold": _get_attr(target, "gold", 0)
        })
        return True
    
    return False


def check_projectile_collisions(projectiles: List[Projectile], enemies: List[dict]) -> List[Tuple[Projectile, dict]]:
    """
    Verifica colisiones proyectil-enemigo usando círculos.
    
    Returns:
        Lista de tuplas (projectile, enemy) que colisionaron
    """
    collisions = []
    
    for proj in projectiles:
        if not proj.alive or proj.exploding:
            continue
            
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            dx = proj.x - enemy.x
            dy = proj.y - enemy.y
            distance = math.hypot(dx, dy)
            
            if distance < proj.radius + enemy.radius:
                collisions.append((proj, enemy))
                break  # Un proyectil golpea un enemigo por frame
    
    return collisions


def check_player_enemy_collision(player: dict, enemies: List[dict]) -> List[dict]:
    """
    Verifica colisiones player-enemigo.
    
    Returns:
        Lista de enemigos que colisionaron con el player
    """
    collisions = []
    player_radius = player.get("radius", 16)
    
    for enemy in enemies:
        if not enemy.alive:
            continue
            
        dx = player["x"] - enemy.x
        dy = player["y"] - enemy.y
        distance = math.hypot(dx, dy)
        
        if distance < player_radius + enemy.radius:
            collisions.append(enemy)
    
    return collisions


def resolve_knockback(target: dict, source_x: float, source_y: float, 
                    force: float, resist: float = 0.0) -> None:
    """
    Aplica knockback al target alejándolo de la fuente.
    """
    dx = target["x"] - source_x
    dy = target["y"] - source_y
    dist = math.hypot(dx, dy)
    
    if dist > 0:
        effective_force = force * (1.0 - resist)
        target["x"] += (dx / dist) * effective_force
        target["y"] += (dy / dist) * effective_force


