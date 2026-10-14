import math
import random
from enum import Enum

import pygame

from config import *
from core.events import EventType, event_bus
from ui.hud import HUD
from systems.upgrade_shop import (
    get_affordable_upgrades,
    can_afford,
    is_purchased,
    mark_purchased,
    upgrade_purchase,
    _UPGRADE_CONFIG,
)
from ui.upgrade_ui import draw_upgrade_shop
from systems.highscore import add_highscore, is_new_highscore, get_highscores
from systems.config_manager import load_prefs, set as config_set, get as config_get, toggle_fullscreen, DEFAULT_PREFS, save_prefs


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    UPGRADE = "upgrade"
    PAUSED = "paused"
    CONFIG = "config"
    HIGHSCORES = "highscores"
    GAME_OVER = "game_over"


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.config = load_prefs()  # Cargar configuración al iniciar
        self.upgrade_shop = None  # Se inicializa después cuando sea necesario
        self.running = True
        # inicializar el gamestate dentro de Game
        self.state = GameState.MENU
        self.previous_state = None
        # Entidades
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.barriers = []
        self.particles = []
        self.powerups = []
        # Game state
        self.gold = STARTING_GOLD
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        # flags
        self._game_over_triggered = False
        self._victory_triggered = False
        # fonts / tipografia
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)
        # spawn_player
        self.spawn_player()
        self.spawn_barriers()
        # test cuadrado rojo (borrar en la version final)
        # self.player_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 32, 32) # esto es temporal solo para ver un cuadrado rojo

        # configurar el fullscreen
        self.keys_pressed = set()
        self.mouse_pressed = False
        self.is_fullscreen = self.config.get("fullscreen", False)

    def spawn_player(self):
        self.player = {
            "x": WIDTH // 2,
            "y": HEIGHT // 2,
            "hp": PLAYER_HP,
            "max_hp": PLAYER_MAX_HP,
            "weapon": "pistol",
            "cooldown": 0.0,
            "invuln_timer": 0.0,
            "speed": PLAYER_SPEED,
        }

    def spawn_barriers(self):
        """crear 4 barreras fijas en su posición por defecto"""
        from entities.barrier import Barrier
        for pos in Barrier.default_positions():
            self.barriers.append(Barrier(*pos))

    def spawn_enemy(self, enemy_type="basic", hp_mult=1.0):
        """Spawnea un enemigo en un borde aleatorio de la pantalla."""
        from utils.helpers import random_spawn_point

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

        self.enemies.append(stats)
        event_bus.publish(EventType.ENEMY_SPAWNED, {"enemy": stats, "type": enemy_type})

    # run
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Input según estado
            if self.state == GameState.MENU:
                self.handle_events_menu()
            elif self.state == GameState.PLAYING:
                self.handle_events_playing()
            elif self.state == GameState.PAUSED:
                self.handle_events_paused()
            elif self.state == GameState.CONFIG:
                self.handle_events_config()
            elif self.state == GameState.HIGHSCORES:
                self.handle_events_highscore()
            elif self.state == GameState.UPGRADE:
                self.handle_events_upgrade()
            elif self.state == GameState.GAME_OVER:
                self.handle_events_game_over()

            # Update según estado
            if self.state == GameState.PLAYING:
                self.update(dt)

            # Draw según estado
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_playing()
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            elif self.state == GameState.CONFIG:
                self.draw_config()
            elif self.state == GameState.HIGHSCORES:
                self.draw_highscore_screen()
            elif self.state == GameState.UPGRADE:
                self.draw_upgrade()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()

    def handle_global_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.toggle_fullscreen()

    def handle_events_playing(self):
        events = pygame.event.get()
        self.handle_global_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.PAUSED)
                elif event.key == pygame.K_1:
                    self.player["weapon"] = "pistol"
                elif event.key == pygame.K_2:
                    self.player["weapon"] = "shotgun"
                elif event.key == pygame.K_3:
                    self.player["weapon"] = "rifle"
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        # Guardar preferencia
        self.config["fullscreen"] = self.is_fullscreen
        save_prefs()

    def handle_events_menu(self):
        events = pygame.event.get()
        self.handle_global_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.change_state(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if hasattr(self, 'button_jugar_rect') and self.button_jugar_rect.collidepoint(event.pos):
                        self.change_state(GameState.PLAYING)
                    elif hasattr(self, 'button_config_rect') and self.button_config_rect.collidepoint(event.pos):
                        self.change_state(GameState.CONFIG)
                    elif hasattr(self, 'button_records_rect') and self.button_records_rect.collidepoint(event.pos):
                        self.change_state(GameState.HIGHSCORES)
                    elif hasattr(self, 'button_salir_rect') and self.button_salir_rect.collidepoint(event.pos):
                        self.running = False

    def handle_events_paused(self):
        events = pygame.event.get()
        self.handle_global_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.PLAYING)

    def handle_events_game_over(self):
        events = pygame.event.get()
        self.handle_global_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.player:
                        add_highscore("Jugador", self.gold)
                    self.change_state(GameState.MENU)
                    self._game_over_triggered = False
                    self._victory_triggered = False
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.MENU)
                    self._game_over_triggered = False
                    self._victory_triggered = False

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.big_font.render("Defiende la Base", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)
        options = ["JUGAR", "CONFIGURACIÓN", "RÉCORDS", "SALIR"]
        for i, opt in enumerate(options):
            color = YELLOW if i == 0 else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            self.screen.blit(text, rect)
            # Crear áreas de botón con margen
            if i == 0:
                self.button_jugar_rect = rect.inflate(40, 20)
            elif i == 1:
                self.button_config_rect = rect.inflate(40, 20)
            elif i == 2:
                self.button_records_rect = rect.inflate(40, 20)
            else:
                self.button_salir_rect = rect.inflate(40, 20)

        pygame.display.flip()

    def draw_playing(self):
        self.screen.fill(BLACK)
        # Proyectiles (círculos de colores)
        for proj in self.projectiles:
            pygame.draw.circle(self.screen, proj["color"], (int(proj["x"]), int(proj["y"])), proj["radius"])
        # Enemigos
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, enemy["color"], (int(enemy["x"]), int(enemy["y"])), enemy["radius"])
            # Barra de vida simple
            if enemy["hp"] < enemy["max_hp"]:
                bar_w = 30
                ratio = enemy["hp"] / enemy["max_hp"]
                pygame.draw.rect(self.screen, (64, 64, 64), (enemy["x"] - bar_w//2, enemy["y"] - enemy["radius"] - 8, bar_w, 4))
                pygame.draw.rect(self.screen, (0, 255, 0), (enemy["x"] - bar_w//2, enemy["y"] - enemy["radius"] - 8, int(bar_w * ratio), 4))
        # Barreras
        for barrier in self.barriers:
            barrier.draw(self.screen)
        # Player (cuadrado rojo)
        if self.player:
            player_rect = pygame.Rect(self.player["x"] - 16, self.player["y"] - 16, 32, 32)
            pygame.draw.rect(self.screen, RED, player_rect)
            self.hud.draw(
                self.screen,
                self.player,
                self.wave_number,
                len(self.enemies),
                self.gold
            )
        pygame.display.flip()

    def draw_paused(self):
        self.draw_playing()
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render("PAUSA", True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, rect)
        sub = self.font.render("ESC para continuar", True, GRAY)
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(sub, sub_rect)
        pygame.display.flip()

    def draw_config(self):
        """Dibuja la pantalla de configuración."""
        self.screen.fill(BLACK)

        title_text = self.big_font.render("CONFIGURACIÓN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        # Modo pantalla completa
        fullscreen = self.config.get("fullscreen", False)
        fullscreen_text = self.font.render(
            f"Pantalla completa: {'Sí' if fullscreen else 'No'}", True, WHITE
        )
        fullscreen_rect = fullscreen_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(fullscreen_text, fullscreen_rect)

        # Botón para alternar pantalla completa
        toggle_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40)
        pygame.draw.rect(self.screen, DARK_GRAY, toggle_rect)
        toggle_text = self.font.render("Alternar pantalla completa", True, WHITE)
        self.screen.blit(toggle_text, (WIDTH // 2 - 95, HEIGHT // 2 + 102))

        # Instrucciones
        instr = self.font.render("PRECIONA ESC PARA VOLVER AL MENÚ", True, DARK_GRAY)
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(instr, instr_rect)

        pygame.display.flip()

    def handle_events_config(self):
        """Maneja los eventos durante el estado de configuración."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)
                elif event.key == pygame.K_RETURN:
                    save_prefs()
                    self.change_state(GameState.MENU)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if toggle_rect.collidepoint(pygame.mouse.get_pos()):
                        self.toggle_fullscreen()

    def draw_highscore_screen(self):
        """Dibuja la pantalla de mejores puntuaciones."""
        self.screen.fill(BLACK)

        title_text = self.big_font.render("MEJORES PUNTUACIONES", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        scores = get_highscores()
        if scores:
            for i, entry in enumerate(scores):
                entry_text = self.font.render(
                    f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE
                )
                entry_rect = entry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
                self.screen.blit(entry_text, entry_rect)
        else:
            no_text = self.font.render("Aún no hay récords", True, DARK_GRAY)
            no_rect = no_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(no_text, no_rect)

        back_text = self.font.render("PRECIONA ENTER PARA VOLVER", True, DARK_GRAY)
        back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

        pygame.display.flip()

    def handle_events_highscore(self):
        """Maneja los eventos durante el estado de récords."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.change_state(self.previous_state or GameState.MENU)
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)

    def change_state(self, new_state: GameState):
        """Cambia de estado y avisa al EventBus."""
        old_state = self.state
        self.previous_state = old_state
        self.state = new_state
        event_bus.publish(EventType.STATE_CHANGED, {
            "old_state": old_state,
            "new_state": new_state
        })

    def get_weapon_stats(self, weapon):
        stats = {
            "pistol": {
                "cooldown": WEAPON_PISTOL_COOLDOWN,
                "damage": WEAPON_PISTOL_DAMAGE,
                "spread": WEAPON_PISTOL_SPREAD,
                "speed": WEAPON_PISTOL_PROJECTILE_SPEED,
                "pellets": 1,
                "pierce": 0,
                "explosion_radius": 0,
                "color": YELLOW
            },
            "shotgun": {
                "cooldown": WEAPON_SHOTGUN_COOLDOWN,
                "damage": WEAPON_SHOTGUN_DAMAGE,
                "spread": WEAPON_SHOTGUN_SPREAD,
                "speed": WEAPON_SHOTGUN_PROJECTILE_SPEED,
                "pellets": WEAPON_SHOTGUN_PELLETS,
                "pierce": 0,
                "explosion_radius": 0,
                "color": ORANGE
            },
            "rifle": {
                "cooldown": WEAPON_RIFLE_COOLDOWN,
                "damage": WEAPON_RIFLE_DAMAGE,
                "spread": WEAPON_RIFLE_SPREAD,
                "speed": WEAPON_RIFLE_PROJECTILE_SPEED,
                "pellets": 1,
                "pierce": WEAPON_RIFLE_PIERCE,
                "explosion_radius": 0,
                "color": CYAN
            }
        }
        return stats.get(weapon, stats["pistol"])

    def fire_weapon(self, angle):
        stats = self.get_weapon_stats(self.player["weapon"])

        for _i in range(stats["pellets"]):
            spread_angle = angle + random.uniform(-stats["spread"], stats["spread"])
            vx = math.cos(spread_angle) * stats["speed"]
            vy = math.sin(spread_angle) * stats["speed"]

            spawn_x = self.player["x"] + math.cos(spread_angle) * 20
            spawn_y = self.player["y"] + math.sin(spread_angle) * 20

            projectile = {
                "x": spawn_x,
                "y": spawn_y,
                "vx": vx,
                "vy": vy,
                "damage": stats["damage"],
                "pierce": stats["pierce"],
                "explosion_radius": stats["explosion_radius"],
                "radius": 4,
                "color": stats["color"],
                "owner": "player"
            }
            self.projectiles.append(projectile)
        self.player["cooldown"] = stats["cooldown"]

    def update_player(self, dt):
        p = self.player
        speed = p["speed"]

        # movimiento WASD
        dx = dy = 0
        if pygame.K_w in self.keys_pressed: dy -= 1
        if pygame.K_s in self.keys_pressed: dy += 1
        if pygame.K_a in self.keys_pressed: dx -= 1
        if pygame.K_d in self.keys_pressed: dx += 1

        # normalizar diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        p["x"] += dx * speed * dt
        p["y"] += dy * speed * dt
        # pantalla o campo que podemos ver
        radius = 16
        p["x"] = max(radius, min(WIDTH - radius, p["x"]))
        p["y"] = max(radius, min(HEIGHT - radius, p["y"]))

        # apuntar con mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - p["y"], mouse_x - p["x"])
        p["aim_angle"] = angle

        # disparar si click y cooldown estan listos
        if self.mouse_pressed and p["cooldown"] <= 0:
            self.fire_weapon(angle)

        # timers
        if p["cooldown"] > 0:
            p["cooldown"] -= dt
        if p["invuln_timer"] > 0:
            p["invuln_timer"] -= dt

    def update_projectiles(self, dt):
        """Mueve los proyectiles y los borra cuando salen de la pantalla"""
        for proj in self.projectiles[:]:
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt
            # margen fuera de pantalla
            margin = 50
            if (proj["x"] < -margin or proj["x"] > WIDTH + margin or
                proj["y"] < -margin or proj["y"] > HEIGHT + margin):
                self.projectiles.remove(proj)

    def update_enemies(self, dt):
        """Mueve enemigos hacia el player/barreras y chequea colisiones."""
        if not self.player:
            return

        px, py = self.player["x"], self.player["y"]

        for enemy in self.enemies[:]:
            # Buscar barrera viva más cercana
            target_barrier = None
            min_dist = float('inf')
            for barrier in self.barriers:
                if barrier.alive:
                    bdx = barrier.x - enemy["x"]
                    bdy = barrier.y - enemy["y"]
                    bdist = math.hypot(bdx, bdy)
                    if bdist < min_dist:
                        min_dist = bdist
                        target_barrier = barrier

            # Objetivo: barrera cercana (rango 200px) o player
            if target_barrier and min_dist < 200:
                tx, ty = target_barrier.x, target_barrier.y
            else:
                tx, ty = px, py

            # Vector hacia objetivo
            dx = tx - enemy["x"]
            dy = ty - enemy["y"]
            dist = math.hypot(dx, dy)

            if dist > 0:
                # Normalizar y mover
                dx /= dist
                dy /= dist
                enemy["x"] += dx * enemy["speed"] * dt
                enemy["y"] += dy * enemy["speed"] * dt

            # Colisión con barrera (atacar)
            for barrier in self.barriers:
                if barrier.alive:
                    enemy_rect = pygame.Rect(enemy["x"] - enemy["radius"], enemy["y"] - enemy["radius"], enemy["radius"] * 2, enemy["radius"] * 2)
                    if barrier.rect.colliderect(enemy_rect):
                        destroyed = barrier.take_damage(enemy["damage"])
                        event_bus.publish(EventType.BARRIER_DAMAGED, {"barrier": barrier, "damage": enemy["damage"]})
                        if destroyed:
                            event_bus.publish(EventType.BARRIER_DESTROYED, {"barrier": barrier})
                        break  # Una barrera por frame

            # Colisión con player (daño)
            dist_to_player = math.hypot(px - enemy["x"], py - enemy["y"])
            if dist_to_player < enemy["radius"] + 16:
                self.damage_player(enemy["damage"])
                # Knockback leve al player
                if dist_to_player > 0:
                    ndx = (enemy["x"] - px) / dist_to_player
                    ndy = (enemy["y"] - py) / dist_to_player
                    self.player["x"] += ndx * 50 * dt
                    self.player["y"] += ndy * 50 * dt

    def update_barriers(self, dt):
        """Actualizar las barreras y que se eliminen las destruidas"""
        for barrier in self.barriers[:]:
            if not barrier.alive:
                self.barriers.remove(barrier)
                event_bus.publish(EventType.BARRIER_DESTROYED, {"barrier": barrier})

    def check_projectile_enemy_collisions(self):
        for proj in self.projectiles[:]:
            for enemy in self.enemies[:]:
                dx = proj["x"] - enemy["x"]
                dy = proj["y"] - enemy["y"]
                dist = math.hypot(dx, dy)

                if dist < proj["radius"] + enemy["radius"]:
                    # Daño
                    enemy["hp"] -= proj["damage"]
                    # Proyectil perforante?
                    if proj["pierce"] <= 0:
                        self.projectiles.remove(proj)
                    else:
                        proj["pierce"] -= 1

                    # Muerte
                    if enemy["hp"] <= 0:
                        self.enemies.remove(enemy)
                        self.gold += enemy["gold"]
                        self.enemies_killed += 1
                        event_bus.publish(EventType.ENEMY_DIED, {"enemy": enemy, "gold": enemy["gold"]})
                    break  # Un proyectil golpea un enemigo por frame

    def damage_player(self, amount):
        if not self.player or self.player["invuln_timer"] > 0:
            return
        self.player["hp"] -= amount
        self.player["invuln_timer"] = PLAYER_INVULN_TIME  # 1 segundo
        event_bus.publish(EventType.PLAYER_DAMAGED, {"damage": amount, "hp": self.player["hp"]})

        if self.player["hp"] <= 0:
            self.player_died()

    def player_died(self):
        event_bus.publish(EventType.PLAYER_DIED, {})
        self.change_state(GameState.GAME_OVER)

    def update(self, dt):
        self.update_player(dt)
        self.update_projectiles(dt)
        self.update_enemies(dt)
        self.check_projectile_enemy_collisions()
        self.update_barriers(dt)

        # Spawn timer simple (1 enemigo cada 2 segundos) - temporal hasta WaveManager
        self.spawn_timer += dt
        if self.spawn_timer >= 2.0:
            self.spawn_enemy("basic")
            self.spawn_timer = 0.0

    def handle_events_upgrade(self):
        """Maneja los eventos durante el estado de mejora."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)
                elif event.key == pygame.K_RETURN:
                    affordable = get_affordable_upgrades(self.gold)
                    if affordable:
                        success, new_gold, updated_stats = upgrade_purchase(
                            affordable[0]["id"], self.gold
                        )
                        if success:
                            self.gold = new_gold
                            if updated_stats:
                                if "weapon_pierce" in updated_stats:
                                    self.player['weapon_pierce'] = updated_stats['weapon_pierce']
                                if "weapon_damage" in updated_stats:
                                    self.player['weapon_damage'] = updated_stats['weapon_damage']
                                if "weapon_spread" in updated_stats:
                                    self.player['weapon_spread'] = updated_stats['weapon_spread']
                                if "weapon_cooldown" in updated_stats:
                                    self.player['weapon_cooldown'] = updated_stats['weapon_cooldown']
                                if "max_hp" in updated_stats:
                                    self.player['max_hp'] = updated_stats['max_hp']
                                    self.player['hp'] = min(self.player.get('hp', 1), self.player['max_hp'])
                            self.change_state(self.previous_state or GameState.MENU)

    def draw_upgrade(self):
        """Dibuja la interfaz de la tienda de mejoras."""
        self.screen.fill(BLACK)

        title_text = self.big_font.render("TIENDA DE MEJORAS", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        clicked_rects = draw_upgrade_shop(
            self.screen,
            self.font,
            self.small_font,
            self.gold,
            show_purchased=True
        )

        mouse_pos = pygame.mouse.get_pos()
        for i, click_rect in enumerate(clicked_rects):
            if click_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                affordable = get_affordable_upgrades(self.gold)
                if i < len(affordable):
                    success, new_gold, updated_stats = upgrade_purchase(
                        affordable[i]["id"], self.gold
                    )
                    if success:
                        self.gold = new_gold
                        self.change_state(self.previous_state or GameState.MENU)

        gold_text = self.font.render(f"Oro: {self.gold}", True, WHITE)
        self.screen.blit(gold_text, (WIDTH - 120, 30))

        instr = self.font.render(
            "PRECIONA ENTER PARA COMPRAR O ESC PARA VOLVER", True, DARK_GRAY
        )
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(instr, instr_rect)

        pygame.display.flip()

    def draw_game_over(self):
        """Dibuja la pantalla de game over / victoria."""
        self.screen.fill(BLACK)

        if self._victory_triggered:
            text = self.big_font.render("¡VICTORIA!", True, GREEN)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, rect)

            text = self.font.render(f"Llegaste a la oleada {self.wave_number}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)
        else:
            text = self.big_font.render("GAME OVER", True, RED)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, rect)

            text = self.font.render(f"Oleada: {self.wave_number}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)

            text = self.font.render(f"Oro: {self.gold}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(text, rect)

        text = self.font.render("PRECIONA ENTER PARA VOLVER AL MENÚ", True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(text, rect)

        pygame.display.flip()