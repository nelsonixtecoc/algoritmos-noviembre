"""Sistema de tienda de mejoras para el videojuego.

Maneja la compra, aplicación y seguimiento de mejoras del jugador.
Conecta con la configuración de upgrades.json y las estadísticas del juego.
"""

import json
from pathlib import Path

import pygame

from config import (
    WIDTH,
    HEIGHT,
    WHITE,
    YELLOW,
    CYAN,
    DARK_GRAY,
    STARTING_GOLD,
)

# Cargar configuración de mejoras
_UPGRADES_FILE = Path(__file__).resolve().parents[1] / "config" / "upgrades.json"

try:
    with open(_UPGRADES_FILE, "r", encoding="utf-8") as f:
        _UPGRADE_CONFIG = json.load(f)["upgrades"]
except (FileNotFoundError, json.JSONDecodeError):
    _UPGRADE_CONFIG = []

# Seguimiento de compras: {upgrade_id: True/False}
_purchased_upgrades: dict[str, bool] = {}

# Efectos aplicados permanentemente a las estadísticas del jugador
_applied_effects: dict[str, float | int] = {}


def get_upgrade(upgrade_id: str) -> dict | None:
    """Obtener la definición de una mejora por su ID."""
    for up in _UPGRADE_CONFIG:
        if up["id"] == upgrade_id:
            return up
    return None


def get_all_upgrades() -> list[dict]:
    """Obtener todas las definiciones de mejoras."""
    return _UPGRADE_CONFIG


def is_purchased(upgrade_id: str) -> bool:
    """Verificar si una mejora ya fue comprada."""
    return _purchased_upgrades.get(upgrade_id, False)


def mark_purchased(upgrade_id: str) -> None:
    """Marcar una mejora como comprada."""
    _purchased_upgrades[upgrade_id] = True


def can_afford(upgrade_id: str, current_gold: int) -> bool:
    """Verificar si el jugador puede permitirse una mejora."""
    up = get_upgrade(upgrade_id)
    if up is None:
        return False
    return current_gold >= up["cost"]


def apply_effect(upgrade_id: str, player_stats: dict) -> dict:
    """Aplicar el efecto de una mejora a las estadísticas del jugador.

    Returns las estadísticas actualizadas.
    """
    # Copiar estadísticas base
    stats = dict(player_stats)

    up = get_upgrade(upgrade_id)
    if up is None:
        return stats

    effect_type = up.get("effect", "")
    effect_value = up.get("effect_value", 0)

    if effect_type == "pierce":
        # Affects weapon pierce - stored per-weapon
        weapon = up.get("weapon", "pistol")
        if "weapon_pierce" not in stats:
            stats["weapon_pierce"] = {}
        stats["weapon_pierce"][weapon] = effect_value

    elif effect_type == "spread":
        # Reduce spread (negative value means less spread)
        current_spread = stats.get("weapon_spread", {}).get(up.get("weapon", "shotgun"), 0)
        stats.setdefault("weapon_spread", {})[up.get("weapon", "shotgun")] = current_spread + effect_value

    elif effect_type == "damage":
        # Increase weapon damage
        weapon = up.get("weapon", "rifle")
        current_damage = stats.get("weapon_damage", {}).get(weapon, 0)
        stats.setdefault("weapon_damage", {})[weapon] = current_damage + effect_value

    elif effect_type == "max_hp":
        # Increase player max HP
        stats["max_hp"] = stats.get("max_hp", 3) + effect_value
        # Also increase current HP proportionally
        stats["hp"] = min(stats.get("hp", 1), stats["max_hp"])

    elif effect_type == "reload_mult":
        # Reduce cooldown (multiply by factor < 1 speeds up)
        weapon = up.get("weapon", "pistol")
        current_cooldown = stats.get("weapon_cooldown", {}).get(weapon, 0.3)
        # Apply multiplicative reduction, but don't go below a minimum
        stats.setdefault("weapon_cooldown", {})[weapon] = max(0.05, current_cooldown * effect_value)

    elif effect_type == "starting_gold_bonus":
        # This is applied between games, not during a game session
        pass

    elif effect_type == "pierce_all":
        # Apply pierce to all weapons
        if "weapon_pierce_all" not in stats:
            stats["weapon_pierce_all"] = effect_value

    return stats


def get_affordable_upgrades(current_gold: int) -> list[dict]:
    """Obtener lista de mejoras que el jugador puede permitirse."""
    affordable = []
    for up in _UPGRADE_CONFIG:
        if not is_purchased(up["id"]) and can_afford(up["id"], current_gold):
            affordable.append(up)
    return affordable


def get_purchased_upgrades() -> list[dict]:
    """Obtener lista de mejoras ya compradas."""
    purchased = []
    for up in _UPGRADE_CONFIG:
        if is_purchased(up["id"]):
            purchased.append(up)
    return purchased


def upgrade_purchase(upgrade_id: str, current_gold: int) -> tuple[bool, int, dict]:
    """Intentar comprar una mejora.

    Returns:
        (success, new_gold, updated_stats)
        - success: bool si la compra fue exitosa
        - new_gold: nuevo amount of gold after purchase (or original if failed)
        - updated_stats: dict with applied effects (or original if failed)
    """
    up = get_upgrade(upgrade_id)
    if up is None:
        return False, current_gold, {}

    if is_purchased(upgrade_id):
        # Already purchased - still return success but don't deduct
        return True, current_gold, {}

    if not can_afford(upgrade_id, current_gold):
        # Not enough gold
        return False, current_gold, {}

    # Perform the purchase
    new_gold = current_gold - up["cost"]
    mark_purchased(upgrade_id)

    # Start with current stats, apply the effect
    # We'll use default player stats if none provided
    default_stats = {
        "max_hp": 3,
        "hp": 3,
        "weapon": "pistol",
        "weapon_damage": {"pistol": 10, "shotgun": 6, "rifle": 8, "launcher": 40},
        "weapon_spread": {"pistol": 0.0, "shotgun": 0.26, "rifle": 0.0, "launcher": 0.0},
        "weapon_cooldown": {"pistol": 0.3, "shotgun": 0.8, "rifle": 0.15, "launcher": 1.5},
        "weapon_pierce": {"pistol": 0, "shotgun": 0, "rifle": 0, "launcher": 0},
    }

    updated_stats = apply_effect(upgrade_id, default_stats)

    return True, new_gold, updated_stats