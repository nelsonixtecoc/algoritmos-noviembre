"""Interfaz de usuario de la tienda de mejoras.

Muestra las disponibles para comprar y maneja la interacción
del jugador con la tienda durante el estado UPGRADE.
"""

import pygame
from pathlib import Path

from config import (
    WIDTH,
    HEIGHT,
    WHITE,
    YELLOW,
    CYAN,
    DARK_GRAY,
    BLACK,
    FPS,
    GREEN,
    GRAY,
)

from systems.upgrade_shop import (
    get_all_upgrades,
    is_purchased,
    can_afford,
    get_affordable_upgrades,
    get_purchased_upgrades,
    _UPGRADE_CONFIG,
)

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "ui"


def _load_upgrade_icon(upgrade_id: str, size: int = 32) -> pygame.Surface | None:
    """Cargar un icono representativo para una mejora."""
    # Mapeo de IDs a activos existentes
    icon_map = {
        "piercing_shots": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "weapons"
        / "bullet.png",
        "shotgun_spread": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "weapons"
        / "pellet.png",
        "rifle_damage": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "weapons"
        / "rifle.png",
        "starting_gold": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "ui"
        / "coin.png",
        "max_health": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "ui"
        / "heart_full.png",
        "reload_speed": Path(__file__).resolve().parents[2]
        / "assets"
        / "sprites"
        / "weapons"
        / "bullet.png",
    }
    path = icon_map.get(upgrade_id)
    if path and Path(path).exists():
        try:
            icon = pygame.image.load(str(path)).convert_alpha()
            return pygame.transform.scale(icon, (size, size))
        except Exception:
            pass
    # Fallback: rect colorido por tipo
    color_map = {
        "piercing_shots": CYAN,
        "shotgun_spread": YELLOW,
        "rifle_damage": WHITE,
        "starting_gold": YELLOW,
        "max_health": RED,
        "reload_speed": CYAN,
    }
    color = color_map.get(upgrade_id, WHITE)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, size, size), 3)
    return surf


def draw_upgrade_box(
    surface: pygame.Surface,
    upgrade: dict,
    x: int,
    y: int,
    width: int,
    height: int,
    font: pygame.font.Font,
    font_small: pygame.font.Font,
    purchased: bool,
    affordable: bool,
) -> pygame.Rect:
    """Dibuja una caja de mejora con su información."""
    # Fondo
    if purchased:
        color = DARK_GRAY
        border_color = GREEN
    elif affordable:
        color = DARK_GRAY
        border_color = YELLOW
    else:
        color = DARK_GRAY
        border_color = GRAY

    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)

    # Icono
    icon = _load_upgrade_icon(upgrade["id"], size=32)
    if icon:
        surface.blit(icon, (x + 10, y + 10))
    else:
        # Rectángulo de fallback
        fallback_color = YELLOW if affordable else GRAY if not purchased else GREEN
        pygame.draw.rect(surface, fallback_color, (x + 10, y + 10, 32, 32))

    # Nombre
    name_text = font.render(upgrade["name"], True, WHITE)
    surface.blit(name_text, (x + 48, y + 10))

    # Costo
    cost_text = font_small.render(f"Costo: {up['cost']}", True, YELLOW if affordable else DARK_GRAY)
    surface.blit(cost_text, (x + 48, y + 38))

    # Descripción (línea única corta)
    desc = upgrade["description"]
    desc_max_width = width - 60
    # Simple wrapping by character
    lines = []
    words = desc.split()
    line = ""
    for word in words:
        test_line = line + (" " if line else "") + word
        test_width = font_small.size(test_line)[0]
        if test_width <= desc_max_width:
            line = test_line
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    for i, line in enumerate(lines[:2]):  # Máximo 2 líneas
        desc_render = font_small.render(line, True, WHITE)
        surface.blit(desc_render, (x + 48, y + 68 + i * 20))

    return pygame.Rect(x + 2, y + 2, width - 4, height - 4)


def draw_upgrade_shop(
    surface: pygame.Surface,
    font: pygame.font.Font,
    font_small: pygame.font.Font,
    player_gold: int,
    show_purchased: bool = True,
) -> list[pygame.Rect]:
    """Dibuja la tienda completa y devuelve los rectángulos de clic.

    Returns la lista de rectángulos de cada mejora para detección de clicks.
    """
    upgrades = get_all_upgrades()

    # Filtrar: mostrar disponibles o compradas
    if show_purchased:
        display_upgrades = [u for u in upgrades if is_purchased(u["id"]) or can_afford(u["id"], player_gold)]
    else:
        display_upgrades = get_affordable_upgrades(player_gold)

    # Layout
    box_width = 300
    box_height = 180
    spacing = 20
    start_x = WIDTH // 2 - (box_width + spacing) // 2
    start_y = 100
    cols = 1  # Una columna para simplicidad
    max_height = len(display_upgrades) * (box_height + spacing) + 50

    # Recortar si excede la pantalla
    if start_y + max_height > HEIGHT - 100:
        start_y = HEIGHT - max_height - 50
    if start_x < 0:
        start_x = 0

    clicked_rects = []

    for i, upgrade in enumerate(display_upgrades):
        y = start_y + i * (box_height + spacing)
        if y > HEIGHT - 150:
            break

        rect = draw_upgrade_box(
            surface,
            upgrade,
            start_x,
            y,
            box_width,
            box_height,
            font,
            font_small,
            is_purchased(upgrade["id"]),
            can_afford(upgrade["id"], player_gold),
        )

        # Texto de "YA COMPRADO" si corresponde
        if is_purchased(upgrade["id"]) and show_purchased:
            purchased_text = font_small.render("YA COMPRADO", True, GREEN)
            surface.blit(purchased_text, (start_x + 10, y + 10))

        # Rect para click (un poco más grande que el dibujo)
        click_rect = pygame.Rect(start_x - 10, y - 10, box_width + 20, box_height + 20)
        clicked_rects.append(click_rect)

    # Mostrar oro del jugador
    gold_text = font_small.render(f"Oro: {player_gold}", True, YELLOW)
    surface.blit(gold_text, (WIDTH - 150, 30))

    # Instrucciones
    instr = font_small.render(
        "PRECIONA ENTER PARA COMPRAR O ESC PARA SALIR", True, DARK_GRAY
    )
    surface.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 40))

    return clicked_rects