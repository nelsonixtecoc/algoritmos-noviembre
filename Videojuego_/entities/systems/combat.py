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
_damage_number_callback: Optional[Callable[[float, float, int, Tuple[int, int, int]], None]] = None
_flash_callback: Optional[Callable[[object, float], None]] = None


def register_screen_shake(callback: Callable[[float, float], None]):
    """Registra callback para screen shake: callback(intensity, duration)."""
    global _screen_shake_callback
    _screen_shake_callback = callback


def register_damage_number(callback: Callable[[float, float, int, Tuple[int, int, int]], None]):
    """Registra callback para números de daño: callback(x, y, amount, color)."""
    global _damage_number_callback
    _damage_number_callback = callback


def register_flash_callback(callback: Callable[[object, float], None]):
    """Registra callback para flash visual: callback(entity, duration)."""
    global _flash_callback
    _flash_callback = callback


def _trigger_screen_shake(intensity: float, duration: float = 0.2):
    if _screen_shake_callback:
        _screen_shake_callback(intensity, duration)


def _show_damage_number(x: float, y: float, amount: int, color: Tuple[int, int, int] = WHITE):
    if _damage_number_callback:
        _damage_number_callback(x, y, amount, color)


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
    
    # Número de daño
    dmg_color = YELLOW if damage_type == "critical" else WHITE
    if damage_type == "explosion":
        dmg_color = ORANGE
    elif damage_type == "fire":
        dmg_color = (255, 100, 0)
    _show_damage_number(_get_attr(target, "x"), _get_attr(target, "y") - 20, amount, dmg_color)
    
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


def check_enemy_barrier_collision(enemies: List[dict], barriers: List) -> List[Tuple[dict, object]]:
    """
    Verifica colisiones enemigo-barrera.
    
    Returns:
        Lista de tuplas (enemy, barrier) que colisionaron
    """
    collisions = []
    
    for enemy in enemies:
        if not enemy.get("alive", True):
            continue
            
        enemy_rect = pygame.Rect(
            enemy["x"] - enemy.get("radius", 16),
            enemy["y"] - enemy.get("radius", 16),
            enemy.get("radius", 16) * 2,
            enemy.get("radius", 16) * 2
        )
        
        for barrier in barriers:
            if not barrier.alive:
                continue
            if barrier.rect.colliderect(enemy_rect):
                collisions.append((enemy, barrier))
                break  # Una barrera por enemigo por frame
    
    return collisions


def check_explosion_collisions(explosion_x: float, explosion_y: float, 
                                explosion_radius: float, targets: List[dict]) -> List[dict]:
    """
    Verifica qué objetivos están en el radio de explosión.
    """
    hit = []
    for target in targets:
        if not target.get("alive", True):
            continue
        dx = target["x"] - explosion_x
        dy = target["y"] - explosion_y
        if math.hypot(dx, dy) <= explosion_radius + target.get("radius", 16):
            hit.append(target)
    return hit


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


def circle_collision(x1: float, y1: float, r1: float,
                    x2: float, y2: float, r2: float) -> bool:
    """Verifica colisión círculo-círculo."""
    dx = x1 - x2
    dy = y1 - y2
    return math.hypot(dx, dy) < (r1 + r2)


def rect_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """Verifica colisión rect-rect."""
    return rect1.colliderect(rect2)


def point_in_circle(px: float, py: float, cx: float, cy: float, r: float) -> bool:
    """Verifica si punto está dentro de círculo."""
    dx = px - cx
    dy = py - cy
    return dx*dx + dy*dy <= r*r

# UTILIDADES DE COMBATE

def calculate_dps(weapon: object, damage_mult: float = 1.0) -> float:
    """Calcula DPS teórico de un arma."""
    if not hasattr(weapon, 'damage') or not hasattr(weapon, 'cooldown'):
        return 0
    return (weapon.damage * damage_mult * weapon.pellets) / weapon.cooldown


def get_weapon_recommendation(enemies_count: int, enemy_types: List[str]) -> str:
    """Recomienda arma según situación."""
    if enemies_count > 5 and "basic" in enemy_types:
        return "shotgun"
    elif "tank" in enemy_types:
        return "rifle"
    return "pistol"


def format_damage_number(amount: int) -> str:
    """Formatea número de daño para UI."""
    if amount >= 1000:
        return f"{amount/1000:.1f}k"
    return str(amount)