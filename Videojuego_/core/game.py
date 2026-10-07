import pygame
import math
import random
from config import *

class Game:   
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
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
            self.handle_events()
            if not self.paused:
                self.update(dt)
            self.draw()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_1:
                    self.player["weapon"] = "pistol"
                elif event.key == pygame.K_2:
                    self.player["weapon"] = "shotgun"
                elif event.key == pygame.K_3:
                    self.player["weapon"] = "rifle"
                elif event.key == pygame.K_4:
                    self.player["weapon"] = "launcher"
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN: #click izquierdo
                if event.button == 1:
                    self.mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
        pass #Leer input (WASD, mouse, ESC, etc)
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pygame.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        
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
        p["x"] += dx * speed * dt
        p["y"] += dy * speed * dt
        
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
        
    def draw(self):
        self.screen.fill(BLACK)
        #dibujar player, enemies, projectiles, HUD
        pygame.display.flip()
