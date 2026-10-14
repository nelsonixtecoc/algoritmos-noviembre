import json
import math
from pathlib import Path
from utils.helpers import random_spawn_point
from core.events import event_bus, EventType, GameState
from config import *


class WaveManager:
    """Gestiona oleadas de enemigos: spawneo, timers, eventos."""

    def __init__(self, game):
        self.game = game
        self.waves_data = self._load_waves()
        self.current_wave_index = 0
        self.wave_timer = 0.0
        self.spawn_queue = []  # lista de dicts: {"type", "hp_mult", "spawn_time"}
        self.enemies_spawned_this_wave = 0
        self.total_enemies_this_wave = 0
        self.wave_active = False
        self.between_waves = False
        self.upgrade_shop_active = False

    def _load_waves(self):
        path = Path(__file__).resolve().parents[1] / "config" / "waves.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["waves"]

    def start_wave(self, wave_number):
        """Inicia una oleada específica (1-indexed)."""
        self.current_wave_index = wave_number - 1
        wave = self.waves_data[self.current_wave_index]
        self.wave_active = True
        self.between_waves = False
        self.upgrade_shop_active = False
        self.enemies_spawned_this_wave = 0
        self.wave_timer = 0.0

        # Construir cola de spawn
        self.spawn_queue = []
        self.total_enemies_this_wave = 0
        for enemy_group in wave["enemies"]:
            count = enemy_group["count"]
            hp_mult = enemy_group["hp_mult"]
            spawn_interval = enemy_group["spawn_interval"]
            for i in range(count):
                spawn_time = i * spawn_interval
                self.spawn_queue.append({
                    "type": enemy_group["type"],
                    "hp_mult": hp_mult,
                    "spawn_time": spawn_time
                })
                self.total_enemies_this_wave += 1

        # Ordenar por tiempo de spawn
        self.spawn_queue.sort(key=lambda x: x["spawn_time"])

        event_bus.publish(EventType.WAVE_STARTED, {
            "wave": wave_number,
            "total_enemies": self.total_enemies_this_wave
        })

    def update(self, dt):
        if not self.wave_active:
            if self.between_waves:
                self.wave_timer -= dt
                if self.wave_timer <= 0:
                    next_wave = self.current_wave_index + 2  # +1 para 1-indexed, +1 para siguiente
                    if next_wave <= len(self.waves_data):
                        self.start_wave(next_wave)
                    else:
                        # Juego completado (no debería pasar, wave 10 es final)
                        event_bus.publish(EventType.VICTORY, {"wave": 10})
            return

        # Actualizar timer de oleada
        self.wave_timer += dt

        # Spawn enemigos según cola
        while self.spawn_queue and self.spawn_queue[0]["spawn_time"] <= self.wave_timer:
            enemy_data = self.spawn_queue.pop(0)
            self._spawn_enemy(enemy_data["type"], enemy_data["hp_mult"])
            self.enemies_spawned_this_wave += 1

        # Chequear fin de oleada: todos spawneados Y ningún enemigo vivo
        if self.enemies_spawned_this_wave >= self.total_enemies_this_wave:
            if len(self.game.enemies) == 0:
                self._wave_completed()

    def _spawn_enemy(self, enemy_type, hp_mult):
        """Spawnea un enemigo con multiplicador de HP."""
        x, y = random_spawn_point(WIDTH, HEIGHT, margin=50)

        base_stats = {
            "basic": {"hp": ENEMY_BASIC_HP, "speed": ENEMY_BASIC_SPEED, "damage": ENEMY_BASIC_DAMAGE, "gold": ENEMY_BASIC_GOLD, "color": (200, 50, 50), "radius": 16, "knockback_resist": 0.0},
            "tank": {"hp": ENEMY_TANK_HP, "speed": ENEMY_TANK_SPEED, "damage": ENEMY_TANK_DAMAGE, "gold": ENEMY_TANK_GOLD, "color": (100, 100, 200), "radius": 20, "knockback_resist": ENEMY_TANK_KNOCKBACK_RESIST},
            "speedy": {"hp": ENEMY_SPEEDY_HP, "speed": ENEMY_SPEEDY_SPEED, "damage": ENEMY_SPEEDY_DAMAGE, "gold": ENEMY_SPEEDY_GOLD, "color": (50, 200, 50), "radius": 12, "knockback_resist": 0.0, "dodge_chance": ENEMY_SPEEDY_DODGE_CHANCE},
        }

        stats = base_stats.get(enemy_type, base_stats["basic"]).copy()
        stats["hp"] = int(stats["hp"] * hp_mult)
        stats["max_hp"] = stats["hp"]
        stats["x"] = x
        stats["y"] = y
        stats["type"] = enemy_type

        self.game.enemies.append(stats)
        event_bus.publish(EventType.ENEMY_SPAWNED, {"enemy": stats, "type": enemy_type})

    def _wave_completed(self):
        wave = self.waves_data[self.current_wave_index]
        wave_number = self.current_wave_index + 1
        self.wave_active = False

        if wave.get("is_final"):
            event_bus.publish(EventType.VICTORY, {"wave": wave_number})
            self.game._victory_triggered = True
            self.game.change_state(GameState.GAME_OVER)
            return

        # Entre oleadas: upgrade shop
        self.between_waves = True
        self.wave_timer = self.waves_data[0].get("wave_cooldown", 5.0)
        event_bus.publish(EventType.WAVE_COMPLETED, {"wave": wave_number, "gold_bonus": 50})
        self.game.change_state(GameState.UPGRADE)