
import pygame

from config import (
    WIDTH,
    HEIGHT,
    WHITE,
    RED,
    YELLOW,
    CYAN,
    DARK_GRAY,
)
import pygame as pg
from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "sprites" / "ui"

# Cargar icono de moneda (con cache)
_coin_icon_cache = None
def _get_coin_icon():
    global _coin_icon_cache
    if _coin_icon_cache is None:
        path = Path(_ASSETS_DIR) / "coin.png"
        if path.exists():
            _coin_icon_cache = pg.image.load(str(path)).convert_alpha()
            _coin_icon_cache = pg.transform.scale(_coin_icon_cache, (20, 20))
        else:
            _coin_icon_cache = None
    return _coin_icon_cache


class HUD:
    """Interfaz que muestra la información de la partida."""

    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 18)

    def draw(self, screen, player, wave_number, enemies_alive, gold):
        """Dibuja los datos actuales de la partida."""

        # Vidas del jugador
        hp = max(0, player["hp"])
        max_hp = player["max_hp"]

        for i in range(max_hp):
            color = RED if i < hp else DARK_GRAY
            pygame.draw.rect(
                screen,
                color,
                (12 + i * 25, 12, 19, 17),
            )

        # Ronda actual
        wave_text = self.font.render(
            f"OLEADA {wave_number}/10", True, WHITE
        )
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 12))

        # Enemigos vivos y oro
        enemies_text = self.small_font.render(
            f"Enemigos: {enemies_alive}", True, WHITE
        )
        screen.blit(enemies_text, (12, 43))

        # Oro con icono
        coin_icon = _get_coin_icon()
        if coin_icon:
            screen.blit(coin_icon, (WIDTH - 170, 44))
        gold_text = self.small_font.render(
            f"{gold}", True, YELLOW
        )
        screen.blit(gold_text, (WIDTH - 145, 43))

        # Arma seleccionada
        weapons = {
            "pistol": ("1", "PISTOLA"),
            "shotgun": ("2", "ESCOPETA"),
            "rifle": ("3", "RIFLE"),
        }

        weapon_key, weapon_name = weapons.get(
            player["weapon"], ("?", player["weapon"].upper())
        )

        weapon_text = self.font.render(
            f"Arma {weapon_key}: {weapon_name}", True, CYAN
        )
        screen.blit(weapon_text, (12, HEIGHT - 32))

        # Barra de recarga
        cooldown = max(0, player["cooldown"])
        cooldowns = {
            "pistol": 0.3,
            "shotgun": 0.8,
            "rifle": 0.15,
        }
        max_cooldown = cooldowns.get(player["weapon"], 0.3)

        progress = 1 - min(cooldown / max_cooldown, 1)

        bar_x = WIDTH - 142
        bar_y = HEIGHT - 27
        bar_width = 130
        bar_height = 12

        pygame.draw.rect(
            screen, DARK_GRAY,
            (bar_x, bar_y, bar_width, bar_height)
        )
        pygame.draw.rect(
            screen, CYAN,
            (bar_x, bar_y, int(bar_width * progress), bar_height)
        )

