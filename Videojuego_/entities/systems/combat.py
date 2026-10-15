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
_spawn_particles_callback: Optional[Callable[[str, float, float, Tuple[int, int, int], int], None]] = None
_damage_number_callback: Optional[Callable[[float, float, int, Tuple[int, int, int]], None]] = None
_flash_callback: Optional[Callable[[dict, float], None]] = None


def register_screen_shake(callback: Callable[[float, float], None]):
    """Registra callback para screen shake: callback(intensity, duration)."""
    global _screen_shake_callback
    _screen_shake_callback = callback


def register_spawn_particles(callback: Callable[[str, float, float, Tuple[int, int, int], int], None]):
    """Registra callback para partículas: callback(type, x, y, color, count)."""
    global _spawn_particles_callback
    _spawn_particles_callback = callback


def register_damage_number(callback: Callable[[float, float, int, Tuple[int, int, int]], None]):
    """Registra callback para números de daño: callback(x, y, amount, color)."""
    global _damage_number_callback
    _damage_number_callback = callback


def register_flash_callback(callback: Callable[[dict, float], None]):
    """Registra callback para flash visual: callback(entity, duration)."""
    global _flash_callback
    _flash_callback = callback


def _trigger_screen_shake(intensity: float, duration: float = 0.2):
    if _screen_shake_callback:
        _screen_shake_callback(intensity, duration)


def _spawn_particles(p_type: str, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
    if _spawn_particles_callback:
        _spawn_particles_callback(p_type, x, y, color, count)


def _show_damage_number(x: float, y: float, amount: int, color: Tuple[int, int, int] = WHITE):
    if _damage_number_callback:
        _damage_number_callback(x, y, amount, color)


def _trigger_flash(entity: dict, duration: float = 0.1):
    if _flash_callback:
        _flash_callback(entity, duration)

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
    if target.get("invuln_timer", 0) > 0:
        return False
    
    # Verificar si está vivo
    if not target.get("alive", True):
        return False
    
    # Aplicar daño
    old_hp = target.get("hp", 0)
    target["hp"] = max(0, old_hp - amount)
    
    # Invulnerabilidad post-daño SOLO para player (tiene "weapon" key)
    # Enemigos NO reciben invulnerabilidad para permitir multi-hit
    if "weapon" in target:
        target["invuln_timer"] = PLAYER_INVULN_TIME
    
    # Knockback
    if knockback > 0 and knockback_resist < 1.0:
        effective_knockback = knockback * (1.0 - knockback_resist)
        # La dirección se calcula fuera y se aplica via resolve_knockback
    
    # Flash visual
    _trigger_flash(target, 0.1)
    
    # Número de daño
    dmg_color = YELLOW if damage_type == "critical" else WHITE
    if damage_type == "explosion":
        dmg_color = ORANGE
    elif damage_type == "fire":
        dmg_color = (255, 100, 0)
    _show_damage_number(target["x"], target["y"] - 20, amount, dmg_color)
    
    # Partículas de impacto
    _spawn_particles("impact", target["x"], target["y"], WHITE, 8)
    
    # Screen shake leve
    _trigger_screen_shake(2.0, 0.1)
    
    # Evento de daño
    event_type = EventType.PLAYER_DAMAGED if "weapon" in target else EventType.ENEMY_DIED
    event_bus.publish(event_type, {
        "attacker": attacker,
        "target": target,
        "damage": amount,
        "damage_type": damage_type,
        "old_hp": old_hp,
        "new_hp": target["hp"]
    })
    
    # Verificar muerte
    if target["hp"] <= 0:
        target["hp"] = 0
        target["alive"] = False
        
        # Partículas de muerte
        _spawn_particles("death", target["x"], target["y"], target.get("color", RED), 20)
        
        # Screen shake mayor
        _trigger_screen_shake(5.0, 0.3)
        
        event_bus.publish(EventType.ENEMY_DIED if "weapon" not in target else EventType.PLAYER_DIED, {
            "entity": target,
            "killer": attacker,
            "gold": target.get("gold", 0)
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
            if not enemy.get("alive", True):
                continue
            
            dx = proj.x - enemy["x"]
            dy = proj.y - enemy["y"]
            distance = math.hypot(dx, dy)
            
            if distance < proj.radius + enemy.get("radius", 16):
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
        if not enemy.get("alive", True):
            continue
            
        dx = player["x"] - enemy["x"]
        dy = player["y"] - enemy["y"]
        distance = math.hypot(dx, dy)
        
        if distance < player_radius + enemy.get("radius", 16):
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
    elif any(t in enemy_types for t in ["tank", "boss"]):
        return "rifle"
    return "pistol"


def format_damage_number(amount: int) -> str:
    """Formatea número de daño para UI."""
    if amount >= 1000:
        return f"{amount/1000:.1f}k"
    return str(amount)