"""Weapons package - Strategy Pattern para armas del jugador."""

from entities.weapons.weapon import Weapon
from entities.weapons.pistol import Pistol
from entities.weapons.shotgun import Shotgun
from entities.weapons.rifle import Rifle

__all__ = ["Weapon", "Pistol", "Shotgun", "Rifle"]

# Factory para crear armas por nombre
WEAPON_CLASSES = {
    "pistol": Pistol,
    "shotgun": Shotgun,
    "rifle": Rifle,
}

def create_weapon(weapon_name: str) -> Weapon:
    """Crea una instancia de arma por nombre."""
    cls = WEAPON_CLASSES.get(weapon_name.lower())
    if cls is None:
        raise ValueError(f"Arma desconocida: {weapon_name}. Disponibles: {list(WEAPON_CLASSES.keys())}")
    return cls()