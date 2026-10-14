import math
import random
from enum import Enum

import pygame

from config import *
from core.events import EventType, event_bus


class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    UPGRADE = "upgrade"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
    #inicializar el gamestate dentro de Game
        self.state = GameState.MENU
        self.previous_state = None
    #Entidades
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.barriers = []
        self.particles = []
        self.powerups = []
    #Game state
        self.gold = STARTING_GOLD
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
    #fonts / tipografia
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
    #spawn_player
        self.spawn_player()
        self.spawn_barriers()
    #test cuadrado rojo (borrar en la version final)
        #self.player_rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 32, 32) #esto es temporal solo para ver un cuadrado rojo

    #configurar el fullscreen
        self.keys_pressed = set()
        self.mouse_pressed = False
        self.is_fullscreen = False

    def spawn_player(self):
        self.player = {
            "x" : WIDTH // 2,
            "y" : HEIGHT // 2,
            "hp" : PLAYER_HP,
            "max_hp" : PLAYER_MAX_HP,
            "weapon" : "pistol",
            "cooldown" : 0.0,
            "invuln_timer" : 0.0,
            "speed" : PLAYER_SPEED
        }
     
    def spawn_barriers(self):
        """crear 4 barrerar fijas en su posición por defecto"""
        from entities.barrier import Barrier
        for pos in Barrier.default_positions():
            self.barriers.append(Barrier(*pos))

    def spawn_enemy(self, enemy_type="basic"):
        """Spawnea un enemigo en un borde aleatorio de la pantalla."""
        from utils.helpers import random_spawn_point
        
        x, y = random_spawn_point(WIDTH, HEIGHT, margin=50)
        
        if enemy_type == "basic":
            enemy = {
                "x": x,
                "y": y,
                "hp": ENEMY_BASIC_HP,
                "max_hp": ENEMY_BASIC_HP,
                "speed": ENEMY_BASIC_SPEED,
                "damage": ENEMY_BASIC_DAMAGE,
                "gold": ENEMY_BASIC_GOLD,
                "type": "basic",
                "color": (200, 50, 50),  # rojo oscuro para basic
                "radius": 16,
                "knockback_resist": 0.0,
            }
        # TODO: añadir "tank", "speedy" luego
        
        self.enemies.append(enemy)
        event_bus.publish(EventType.ENEMY_SPAWNED, {"enemy": enemy, "type": enemy_type})

        #run
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

    def handle_events_menu(self):
        events = pygame.event.get()
        self.handle_global_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.change_state(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
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
                    self.change_state(GameState.MENU)
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.MENU)

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.big_font.render("Defiende la Base", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)
        options = ["JUGAR", "CONFIGURACIÓN", "RECORDS", "SALIR"]
        for i, opt in enumerate(options):
            color = YELLOW if i == 0 else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            self.screen.blit(text, rect)
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

    def draw_game_over(self):
        self.screen.fill(BLACK)
        text = self.big_font.render("GAME OVER", True, RED)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, rect)
        sub = self.font.render("ENTER para volver al menu", True, WHITE)
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(sub, sub_rect)
        pygame.display.flip()

    def change_state(self, new_state: GameState):
        """Cambia de estado y avisa al EventBus."""
        old_state = self.state
        self.previous_state = old_state
        self.state = new_state
        #importeamos de manera local
        event_bus.publish(EventType.STATE_CHANGED, {
            "old_state" : old_state,
            "new_state" : new_state
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

        for i in range(stats["pellets"]):
            spread_angle = angle + random.uniform(-stats["spread"], stats["spread"])
            vx = math.cos(spread_angle) * stats["speed"]
            vy = math.sin(spread_angle) * stats["speed"]

            spawn_x = self.player["x"] + math.cos(spread_angle) * 20
            spawn_y = self.player["y"] + math.sin(spread_angle) * 20

            projectile = {
                "x" : spawn_x,
                "y" : spawn_y,
                "vx" : vx,
                "vy" : vy,
                "damage" : stats["damage"],
                "pierce" : stats["pierce"],
                "explosion_radius" : stats["explosion_radius"],
                "radius" : 4,
                "color" : stats["color"],
                "owner" : "player"
            }
            self.projectiles.append(projectile)
        self.player["cooldown"] = stats["cooldown"]

    def update_player(self, dt):
        p = self.player
        speed = p["speed"]

        #movimiento WASD
        dx = dy = 0
        if pygame.K_w in self.keys_pressed: dy -= 1
        if pygame.K_s in self.keys_pressed: dy += 1
        if pygame.K_a in self.keys_pressed: dx -= 1
        if pygame.K_d in self.keys_pressed: dx += 1

        #normalizar diagona
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        #ligero cambio solo de prueba
        p["x"] += dx * speed * dt
        p["y"] += dy * speed * dt
        #self.player_rect.center = (p["x"], p["y"]) #Este es temporal para que el cuadrado rojo spawnee en el centro
        #pantalla o campo que podemos ver
        radius = 16
        p["x"] = max(radius, min(WIDTH - radius, p["x"]))
        p["y"] = max(radius, min(HEIGHT - radius, p["y"]))

        #apuntar con mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - p["y"], mouse_x -p["x"])
        p["aim_angle"] = angle

        #disparar si click y cooldown estan listos
        if self.mouse_pressed and p["cooldown"] <= 0:
            self.fire_weapon(angle)

        #timers
        if p["cooldown"] > 0:
            p["cooldown"] -= dt
        if p["invuln_timer"] > 0:
            p["invuln_timer"] -= dt
             
    def update_projectiles(self, dt):
        """Mueve los proyectiles y los borra cuando salen de la pantalla"""
        for proj in self.projectiles[:]:  # copia para borrar mientras iteramos
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
                    # Rect del enemigo para colisión
                    enemy_rect = pygame.Rect(enemy["x"] - enemy["radius"], enemy["y"] - enemy["radius"], enemy["radius"] * 2, enemy["radius"] * 2)
                    if barrier.rect.colliderect(enemy_rect):
                        destroyed = barrier.take_damage(enemy["damage"])
                        event_bus.publish(EventType.BARRIER_DAMAGED, {"barrier": barrier, "damage": enemy["damage"]})
                        if destroyed:
                            event_bus.publish(EventType.BARRIER_DESTROYED, {"barrier": barrier})
                        break  # Una barrera por frame
            
            # Colisión con player (daño)
            dist_to_player = math.hypot(px - enemy["x"], py - enemy["y"])
            if dist_to_player < enemy["radius"] + 16:  # 16 = radio player
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
        
        # Spawn timer simple (1 enemigo cada 2 segundos)
        self.spawn_timer += dt
        if self.spawn_timer >= 2.0:
            self.spawn_enemy("basic")
            self.spawn_timer = 0.0