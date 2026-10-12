import pygame
import math
import random
from config import *
from core.events import event_bus, EventType
from enum import Enum


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
        options = ["JUGAR", "CONFIGURACIÓN", "RECORDS" "SALIR"]
        for i, opt in enumerate(options):
            color = YELLOW if i == 0 else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            self.screen.blit(text, rect)
        pygame.display.flip()

    def draw_playing(self):
        self.screen.fill(BLACK)
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
        from core.events import event_bus, EventType
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
            },
            "launcher": {
                "cooldown": WEAPON_LAUNCHER_COOLDOWN,
                "damage": WEAPON_LAUNCHER_DAMAGE,
                "spread": 0.0,
                "speed": WEAPON_LAUNCHER_PROJECTILE_SPEED,
                "pellets": 1,
                "pierce": 0,
                "explosion_radius": WEAPON_LAUNCHER_EXPLOSION_RADIUS,
                "color": RED
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
    def update(self, dt):
        self.update_player(dt)
        #Update de todo, enemies, projectiles, collisions
