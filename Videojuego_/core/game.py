import pygame
import math
import random
from config import *
from core.events import event_bus, EventType
from enum import Enum

# Ensure set is the built-in type (prevent conflicts from imports)
builtin_set = set

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
from systems.config_manager import load_prefs, set, get, toggle_fullscreen, DEFAULT_PREFS, save_prefs


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
        self.wave_number = 0  # Start at 0, first wave will make it 1
        self.enemies_killed = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        #fonts / tipografia 
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        #spawn_player
        self.spawn_player()
        #test cuadrado rojo (borrar en la version final)
        
        #configurar el fullscreen
        self.keys_pressed = builtin_set()
        self.mouse_pressed = False
        self.is_fullscreen = self.config.get("fullscreen", False)

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
    
    def spawn_enemy(self, enemy_type="basic", x=None, y=None):
        """Create and return an enemy dict"""
        if x is None:
            x = random.randint(50, WIDTH - 50)
        if y is None:
            y = random.randint(50, HEIGHT - 50)
        
        if enemy_type == "basic":
            return {
                "x": x,
                "y": y,
                "hp": ENEMY_BASIC_HP,
                "max_hp": ENEMY_BASIC_HP,
                "speed": ENEMY_BASIC_SPEED,
                "damage": ENEMY_BASIC_DAMAGE,
                "gold": ENEMY_BASIC_GOLD,
                "type": "basic",
                "rect": pygame.Rect(x - 16, y - 16, 32, 32),
                "alive": True
            }
        elif enemy_type == "speedy":
            return {
                "x": x,
                "y": y,
                "hp": ENEMY_SPEEDY_HP,
                "max_hp": ENEMY_SPEEDY_HP,
                "speed": ENEMY_SPEEDY_SPEED,
                "damage": ENEMY_SPEEDY_DAMAGE,
                "gold": ENEMY_SPEEDY_GOLD,
                "type": "speedy",
                "rect": pygame.Rect(x - 12, y - 12, 24, 24),
                "alive": True
            }
        elif enemy_type == "tank":
            return {
                "x": x,
                "y": y,
                "hp": ENEMY_TANK_HP,
                "max_hp": ENEMY_TANK_HP,
                "speed": ENEMY_TANK_SPEED,
                "damage": ENEMY_TANK_DAMAGE,
                "gold": ENEMY_TANK_GOLD,
                "type": "tank",
                "rect": pygame.Rect(x - 24, y - 24, 48, 48),
                "alive": True
            }
        return None
    
    def spawn_wave(self):
        """Spawn all enemies for the current wave"""
        self.enemies = []
        num_enemies = 5 + (self.wave_number - 1) * 2  # 5, 7, 9, 11...
        
        # Determine enemy mix based on wave
        # Early waves: mostly basic, later waves add tank/speedy
        num_basic = max(3, num_enemies - 2 - (self.wave_number // 3))
        num_speedy = min(2, self.wave_number // 3)
        num_tank = min(2, (self.wave_number - 1) // 4)
        
        # Adjust if we have enough
        remaining = num_enemies - num_basic - num_speedy - num_tank
        if remaining > 0:
            num_basic += remaining
        
        # Spawn basic enemies in a spread
        for i in range(num_basic):
            angle = (i / max(1, num_basic)) * math.pi * 2
            radius = 100 + i * 30
            x = self.player["x"] + math.cos(angle) * radius
            y = self.player["y"] + math.sin(angle) * radius
            enemy = self.spawn_enemy("basic", x, y)
            if enemy:
                self.enemies.append(enemy)
        
        # Spawn speedy enemies in circles
        for i in range(num_speedy):
            angle = (i / max(1, num_speedy)) * math.pi * 2 + math.pi / 2
            radius = 150 + i * 40
            x = self.player["x"] + math.cos(angle) * radius
            y = self.player["y"] + math.sin(angle) * radius
            enemy = self.spawn_enemy("speedy", x, y)
            if enemy:
                self.enemies.append(enemy)
        
        # Spawn tank enemies
        for i in range(num_tank):
            angle = (i / max(1, num_tank)) * math.pi * 2
            radius = 200 + i * 50
            x = self.player["x"] + math.cos(angle) * radius
            y = self.player["y"] + math.sin(angle) * radius
            enemy = self.spawn_enemy("tank", x, y)
            if enemy:
                self.enemies.append(enemy)
        
        # Publish spawn event
        event_bus.publish(EventType.ENEMY_SPAWNED, {"wave": self.wave_number, "count": len(self.enemies)})
        
        # Reset spawn timer
        self.spawn_timer = 0.0
    
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
    
    def handle_events_playing(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.PAUSED)
                elif event.key == pygame.K_f:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_1:
                    self.player["weapon"] = "pistol"
                elif event.key == pygame.K_2:
                    self.player["weapon"] = "shotgun"
                elif event.key == pygame.K_3:
                    self.player["weapon"] = "rifle"
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN: #click izquierdo
                if event.button == 1:
                    self.mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
    
    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        flags = pygame.FULLSCREEN if self.is_fullscreen else 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    
    def handle_events_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Seleccionar la opción destacada (JUGAR)
                    if not hasattr(self, 'button_config_rect') or not hasattr(self, 'button_records_rect'):
                        self.change_state(GameState.PLAYING)
                    elif self.button_jugar_rect.collidepoint(pygame.mouse.get_pos()) if pygame.mouse.get_pressed()[1] else False:
                        self.change_state(GameState.PLAYING)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: #click izquierdo
                    # Verificar si hay rectángulos de botón definidos
                    if hasattr(self, 'button_jugar_rect') and self.button_jugar_rect.collidepoint(event.pos):
                        self.change_state(GameState.PLAYING)
                    elif hasattr(self, 'button_config_rect') and self.button_config_rect.collidepoint(event.pos):
                        self.change_state(GameState.CONFIG)
                    elif hasattr(self, 'button_records_rect') and self.button_records_rect.collidepoint(event.pos):
                        self.change_state(GameState.HIGHSCORES)
                    elif hasattr(self, 'button_salir_rect') and self.button_salir_rect.collidepoint(event.pos):
                        self.running = False
    
    def handle_events_paused(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.PLAYING)
    
    
    def handle_events_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Guardar puntuación antes de volver al menú
                    # Usar nombre por defecto ya que input() no funciona en Pygame window
                    player_name = "Jugador"
                    if self.player:
                        add_highscore(player_name, self.gold)
                    self.change_state(GameState.MENU)
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.MENU)
    
    def draw_menu(self):
        self.screen.fill(BLACK)

        title = self.big_font.render("Videojuego XDDD", True, WHITE)
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
        # Draw enemies
        if self.enemies:
            for enemy in self.enemies:
                if enemy["alive"]:
                    # Draw enemy rect based on type
                    if enemy["type"] == "tank":
                        color = (139, 69, 19)  # Brown for tank
                        pygame.draw.rect(self.screen, color, 
                            (enemy["rect"].x, enemy["rect"].y, enemy["rect"].width, enemy["rect"].height))
                    elif enemy["type"] == "speedy":
                        color = (255, 255, 0)  # Yellow for speedy
                        pygame.draw.ellipse(self.screen, color, 
                            (enemy["rect"].x, enemy["rect"].y, enemy["rect"].width, enemy["rect"].height))
                    else:
                        # Basic enemy - red
                        color = (220, 20, 60)  # Dark red
                        pygame.draw.rect(self.screen, color, 
                            (enemy["rect"].x, enemy["rect"].y, enemy["rect"].width, enemy["rect"].height))
        # Draw projectiles
        if self.projectiles:
            for proj in self.projectiles:
                if proj["alive"]:
                    pygame.draw.circle(self.screen, proj["color"], 
                        (int(proj["x"]), int(proj["y"])), proj["radius"])
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
        
        # Guardar cambios
        if pygame.mouse.get_pressed()[0]:
            if toggle_rect.collidepoint(pygame.mouse.get_pos()):
                toggle_fullscreen()
                save_prefs()
        
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
                    # Guardar y volver al menú
                    save_prefs()
                    self.change_state(GameState.MENU)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Alternar pantalla completa si se hace clic
                    toggle_fullscreen()
                    save_prefs()
    
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
    
        sub = self.font.render("ENTER para volver al menú", True, WHITE)
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(sub, sub_rect)
        
        # Mostrar highscore actual
        scores = get_highscores()
        if scores:
            hs_text = self.font.render("Récords:", True, YELLOW)
            hs_rect = hs_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            self.screen.blit(hs_text, hs_rect)
            for i, entry in enumerate(scores[:3]):
                entry_text = self.small_font.render(
                    f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE
                )
                entry_rect = entry_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 130 + i * 30))
                self.screen.blit(entry_text, entry_rect)
    
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
                "owner" : "player",
                "alive" : True
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
    
    def update_enemies(self, dt):
        """Update all enemies and return list of enemies to remove"""
        to_remove = []
        
        for enemy in self.enemies:
            if not enemy["alive"]:
                to_remove.append(enemy)
                continue
            
            # Simple AI: move toward player
            dx = self.player["x"] - enemy["x"]
            dy = self.player["y"] - enemy["y"]
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            
            # Normalize and move
            enemy["x"] += (dx / dist) * enemy["speed"] * dt
            enemy["y"] += (dy / dist) * enemy["speed"] * dt
            
            # Update rect
            enemy["rect"].center = (enemy["x"], enemy["y"])
            
            # Check collision with player
            player_rect = pygame.Rect(self.player["x"] - 16, self.player["y"] - 16, 32, 32)
            if enemy["rect"].colliderect(player_rect):
                # Player takes damage
                if self.player["invuln_timer"] <= 0:
                    self.player["hp"] -= enemy["damage"]
                    self.player["invuln_timer"] = PLAYER_INVULN_TIME
                    
                    # Check if player died
                    if self.player["hp"] <= 0:
                        self.change_state(GameState.GAME_OVER)
                        self._game_over_triggered = True
            
            # Check if enemy reached base (close enough to player)
            if dist < 80:
                to_remove.append(enemy)  # Enemy reached base, remove
        
        # Remove dead enemies and update score
        for enemy in to_remove:
            if enemy in self.enemies and enemy["alive"]:
                enemy["alive"] = False
                self.enemies_killed += 1
                self.gold += enemy["gold"]
                event_bus.publish(EventType.ENEMY_DIED, {
                    "enemy": enemy,
                    "gold": self.gold,
                    "wave": self.wave_number
                })
        
        # Filter out dead enemies
        self.enemies = [e for e in self.enemies if e["alive"]]
        
        return len(to_remove)
    
    def update_projectiles(self, dt):
        """Update projectiles and check collisions"""
        to_remove = []
        
        for i, proj in enumerate(self.projectiles):
            if not proj["alive"]:
                to_remove.append(i)
                continue
            
            # Move projectile
            proj["x"] += proj["vx"] * dt
            proj["y"] += proj["vy"] * dt
            
            # Update rect
            proj["rect"] = pygame.Rect(proj["x"] - proj["radius"], proj["y"] - proj["radius"], proj["radius"] * 2, proj["radius"] * 2)
            
            # Check bounds
            if (proj["x"] < 0 or proj["x"] > WIDTH or 
                proj["y"] < 0 or proj["y"] > HEIGHT):
                proj["alive"] = False
                to_remove.append(i)
                continue
            
            # Check collision with enemies
            for enemy in self.enemies:
                if not enemy["alive"]:
                    continue
                if proj["rect"].colliderect(enemy["rect"]):
                    # Deal damage
                    enemy["hp"] -= proj["damage"]
                    proj["pierce"] -= 1
                    
                    # Mark projectile as removed if no pierce left
                    if proj["pierce"] <= 0:
                        proj["alive"] = False
                        to_remove.append(i)
                    
                    # Check if enemy died
                    if enemy["hp"] <= 0:
                        enemy["alive"] = False
                        self.enemies_killed += 1
                        self.gold += enemy["gold"]
                        
                        # Chance to spawn power-up
                        if random.random() < 0.15:
                            pass  # Would spawn powerup here
                    
                    event_bus.publish(EventType.ENEMY_DIED, {
                        "enemy": enemy,
                        "gold": self.gold,
                        "wave": self.wave_number
                    })
                    
                    # Break to avoid hitting same enemy multiple times
                    break
        
        # Remove projectiles (in reverse order to maintain indices)
        for idx in sorted(to_remove, reverse=True):
            if 0 <= idx < len(self.projectiles):
                self.projectiles.pop(idx)
    
    def update(self, dt):
        self.update_player(dt)
        
        # Update de todo, enemies, projectiles, collisions
        # Verificar Game Over (vida del jugador a cero)
        if self.player and self.player.get("hp", 0) <= 0:
            self.change_state(GameState.GAME_OVER)
            # Registrar puntuación una sola vez
            if not self._game_over_triggered:
                self._game_over_triggered = True
                if self.player and is_new_highscore(self.gold):
                    # Marcar para que el handler de eventos guarde el récord
                    pass  # Se hará en handle_events_game_over
        
        # Update enemies and projectiles
        if self.state == GameState.PLAYING:
            # Spawn wave if no enemies left
            if not self.enemies and self.spawn_timer <= 0:
                self.wave_number += 1
                self.spawn_wave()
                if self.wave_number > 10:
                    self.change_state(GameState.GAME_OVER)
                    if not self._victory_triggered:
                        self._victory_triggered = True
                        if self.player and is_new_highscore(self.gold):
                            pass  # Se hará en handle_events_game_over
            
            if self.enemies:
                self.update_enemies(dt)
            
            self.update_projectiles(dt)
            
            # Wave timer
            self.wave_timer += dt
            if self.wave_timer > 10.0 and self.enemies:
                # If wave takes too long, maybe increase difficulty or something
                pass
    
    def handle_events_upgrade(self):
        """Maneja los eventos durante el estado de mejora."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.change_state(self.previous_state or GameState.MENU)
                elif event.key == pygame.K_RETURN:
                    # Comprar la mejora seleccionada (la primera asequible)
                    affordable = get_affordable_upgrades(self.gold)
                    if affordable:
                        success, new_gold, updated_stats = upgrade_purchase(
                            affordable[0]["id"], self.gold
                        )
                        if success:
                            self.gold = new_gold
                            # Aplicar efectos al jugador
                            if updated_stats:
                                # Actualizar estadísticas del jugador con los efectos de la mejora
                                if "weapon_pierce" in updated_stats:
                                    # Almacenar pierna por arma
                                    if not hasattr(self.player, '__dict__') or 'weapon_pierce' not in self.player:
                                        self.player['weapon_pierce'] = updated_stats['weapon_pierce']
                                if "weapon_damage" in updated_stats:
                                    if 'weapon_damage' not in self.player:
                                        self.player['weapon_damage'] = updated_stats['weapon_damage']
                                if "weapon_spread" in updated_stats:
                                    if 'weapon_spread' not in self.player:
                                        self.player['weapon_spread'] = updated_stats['weapon_spread']
                                if "weapon_cooldown" in updated_stats:
                                    if 'weapon_cooldown' not in self.player:
                                        self.player['weapon_cooldown'] = updated_stats['weapon_cooldown']
                                if "max_hp" in updated_stats:
                                    self.player['max_hp'] = updated_stats['max_hp']
                                    self.player['hp'] = min(self.player.get('hp', 1), self.player['max_hp'])
                            # Volver al estado anterior o menú
                            self.change_state(self.previous_state or GameState.MENU)
    
    def draw_upgrade(self):
        """Dibuja la interfaz de la tienda de mejoras."""
        # Limpiar pantalla
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("TIENDA DE MEJORAS", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)
        
        # Dibujar la tienda
        from ui.upgrade_ui import draw_upgrade_shop
        clicked_rects = draw_upgrade_shop(
            self.screen,
            self.font,
            self.small_font,
            self.gold,
            show_purchased=True
        )
        
        # Detectar click en cualquier mejora
        mouse_pos = pygame.mouse.get_pos()
        for i, click_rect in enumerate(clicked_rects):
            if click_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                # Comprar la mejora correspondiente
                affordable = get_affordable_upgrades(self.gold)
                if i < len(affordable):
                    success, new_gold, updated_stats = upgrade_purchase(
                        affordable[i]["id"], self.gold
                    )
                    if success:
                        self.gold = new_gold
                        # Volver al estado anterior o menú
                        self.change_state(self.previous_state or GameState.MENU)
        
        # Mostrar oro
        gold_text = self.font.render(f"Oro: {self.gold}", True, WHITE)
        self.screen.blit(gold_text, (WIDTH - 120, 30))
        
        # Instrucciones
        instr = self.font.render(
            "PRECIONA ENTER PARA COMPRAR O ESC PARA VOLVER", True, DARK_GRAY
        )
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        self.screen.blit(instr, instr_rect)
        
        pygame.display.flip()
    
    def draw_game_over(self):
        """Dibuja la pantalla de game over."""
        self.screen.fill(BLACK)
        
        if self.state == GameState.GAME_OVER and self._game_over_triggered:
            # Check if player died
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
        elif self.state == GameState.GAME_OVER and self._victory_triggered:
            text = self.big_font.render("¡VICTORIA!", True, GREEN)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, rect)
            
            text = self.font.render(f"Llegaste a la oleada {self.wave_number}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)
            
            text = self.font.render("PRECIONA ENTER PARA VOLVER AL MENÚ", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.screen.blit(text, rect)
        
        pygame.display.flip()


# Test block
if __name__ == "__main__":
    import sys
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombies Test")
        game = Game(screen)
        
        # Force playing state to test spawning
        game.change_state(GameState.PLAYING)
        
        running = True
        while running:
            dt = game.clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            game.update(dt)
            game.draw_playing()
        
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)