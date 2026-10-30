import math
import random

import pygame

from config import *
from core.events import EventType, event_bus, GameState
from ui.hud import HUD
from systems.highscore import add_highscore, is_new_highscore, get_highscores
from systems.config_manager import load_prefs, toggle_fullscreen, save_prefs
from systems.wave_manager import WaveManager
from entities.weapons import create_weapon
from entities.projectile import Projectile
from entities.pickup import HealthPickup, RepairPickup, SpeedPickup
from entities.systems.combat import (
    apply_damage,
    check_projectile_collisions,
    check_player_enemy_collision,
    register_screen_shake,
    register_flash_callback,
)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.config = load_prefs()  # Cargar configuración al iniciar
        self.wave_manager = WaveManager(self)  # WaveManager
        
        # Sistema de armaswe7
        self.weapons = {
            "pistol": create_weapon("pistol"),
            "shotgun": create_weapon("shotgun"),
            "rifle": create_weapon("rifle"),
        }
        self.current_weapon = self.weapons["pistol"]
        
        # Registrar callbacks para efectos visuales
        register_screen_shake(self._screen_shake)
        register_flash_callback(self._flash_entity)
        
        # Suscribirse a eventos de oleada completada
        event_bus.subscribe(EventType.WAVE_COMPLETED, self._on_wave_completed)
        event_bus.subscribe(EventType.ENEMY_DIED, self._on_enemy_died)
        
        self.running = True
        # inicializar el gamestate dentro de Game
        self.state = GameState.MENU
        self.previous_state = None
        # Entidades
        self.player = None
        self.enemies = []
        self.projectiles = []
        self.barriers = []
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
        # Tiempo que se muestra el mensaje "Fin de la Oleada" entre oleadas (segundos)
        self.WAVE_END_DURATION = 2.5
        self._wave_end_timer = 0.0
        # Screen shake
        self._screen_shake_intensity = 0.0
        self._screen_shake_timer = 0.0
        # Superficie reutilizable para dibujar la escena y aplicar el temblor
        self._scene_surface = pygame.Surface((WIDTH, HEIGHT))
        # Name input
        self.name_input = ""
        # fonts / tipografia
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)
        # spawn_player
        self.spawn_player()
        self.spawn_barriers()
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
            elif self.state == GameState.HIGHSCORES:
                self.handle_events_highscore()
            elif self.state == GameState.WAVE_END:
                self.handle_events_wave_end()
            elif self.state == GameState.GAME_OVER:
                self.handle_events_game_over()
            elif self.state == GameState.NAME_ENTRY:
                self.handle_events_name_entry()

            # Update según estado
            if self.state == GameState.PLAYING:
                self.update(dt)
            elif self.state == GameState.WAVE_END:
                self._update_wave_end(dt)

            # Draw según estado
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_playing()
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            elif self.state == GameState.HIGHSCORES:
                self.draw_highscore_screen()
            elif self.state == GameState.WAVE_END:
                self.draw_wave_end()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.NAME_ENTRY:
                self.draw_name_entry()

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
                        # Verificar si es nuevo highscore
                        if is_new_highscore(self.gold):
                            self.change_state(GameState.NAME_ENTRY)
                        else:
                            add_highscore("Jugador", self.gold)
                            self.change_state(GameState.MENU)
                    else:
                        self.change_state(GameState.MENU)
                    self._game_over_triggered = False
                    self._victory_triggered = False
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(GameState.MENU)
                    self._game_over_triggered = False
                    self._victory_triggered = False

    def handle_events_name_entry(self):
        events = pygame.event.get()
        filtered_events = [
            e for e in events
            if not (e.type == pygame.KEYDOWN and e.key == pygame.K_f)
        ]
        self.handle_global_events(filtered_events)
        if not hasattr(self, 'name_input'):
            self.name_input = ""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(self.name_input) == 3:
                        add_highscore(self.name_input, self.gold)
                        self.name_input = ""
                        self.change_state(GameState.MENU)
                elif event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                else:
                    # Solo letras A-Z
                    if len(self.name_input) < 3 and event.unicode.isalpha():
                        self.name_input += event.unicode.upper()

    def draw_menu(self):
        self.screen.fill(ORANGE)   #funcion contenida dentro de la clase Game
        title = self.big_font.render("LAWANDON", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)
        options = ["JUGAR", "RÉCORDS", "SALIR"]
        for i, opt in enumerate(options):
            color = BLACK if i == 0 else WHITE
            text = self.font.render(opt, True, color)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 40))
            self.screen.blit(text, rect)
            # Crear áreas de botón con margen
            if i == 0:
                self.button_jugar_rect = rect.inflate(40, 20)
            elif i == 1:
                self.button_records_rect = rect.inflate(40, 20)
            else:
                self.button_salir_rect = rect.inflate(40, 20)

        pygame.display.flip()

    def draw_playing(self):
        self._scene_surface.fill(DARK_GREEN)
        
        # Aplicar screen shake
        shake_x = shake_y = 0
        if self._screen_shake_timer > 0:
            import random
            shake_x = random.uniform(-self._screen_shake_intensity, self._screen_shake_intensity)
            shake_y = random.uniform(-self._screen_shake_intensity, self._screen_shake_intensity)
        
        # Proyectiles
        for proj in self.projectiles:
            if isinstance(proj, Projectile):
                proj.draw(self._scene_surface, (0, 0))  # camera offset = 0
            else:
                # Compatibilidad con proyectiles viejos (dicts)
                pygame.draw.circle(self._scene_surface, proj["color"], 
                                (int(proj["x"]), int(proj["y"])), proj["radius"])
        
        # Enemigos
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            pygame.draw.circle(self._scene_surface, enemy.color, 
                            (int(enemy.x), int(enemy.y)), enemy.radius)
            # Barra de vida simple
            if enemy.hp < enemy.max_hp:
                bar_w = 30
                ratio = enemy.hp / enemy.max_hp
                pygame.draw.rect(self._scene_surface, (64, 64, 64), 
                            (enemy.x - bar_w//2, enemy.y - enemy.radius - 8, bar_w, 4))
                pygame.draw.rect(self._scene_surface, (0, 255, 0), 
                               (enemy.x - bar_w//2, enemy.y - enemy.radius - 8, int(bar_w * ratio), 4))
        # Barreras
        for barrier in self.barriers:
            barrier.draw(self._scene_surface)
        # Pickups (solo durante la partida activa, no en pausa)
        if self.state == GameState.PLAYING:
            for powerup in self.powerups:
                powerup.draw(self._scene_surface)
        # Player (cuadrado rojo)
        if self.player:
            player_rect = pygame.Rect(self.player["x"] - 16, self.player["y"] - 16, 32, 32)
            pygame.draw.rect(self._scene_surface, RED, player_rect)

        # Copiar la escena con el temblor; el HUD se dibuja despues, sin temblar
        self.screen.fill(BLACK)
        self.screen.blit(self._scene_surface, (int(shake_x), int(shake_y)))
        if self.player:
            self.hud.draw(
                self.screen,
                self.player,
                self.wave_number,
                len(self.enemies),
                self.gold
            )
        pygame.display.flip()

    def draw_paused(self):
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

    def draw_highscore_screen(self):
        """Dibuja la pantalla de mejores puntuaciones."""
        self.screen.fill(ORANGE)

        title_text = self.big_font.render("EL TOP 5", True, BLACK)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text, title_rect)

        scores = get_highscores()
        if scores:
            for i, entry in enumerate(scores):
                entry_text = self.font.render(
                    f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE
                )
                entry_rect = entry_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 40))
                self.screen.blit(entry_text, entry_rect)
        else:
            no_text = self.font.render("¿Nadie lo ha intentado aún?", True, DARK_GRAY)
            no_rect = no_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(no_text, no_rect)

        back_text = self.font.render("PRESIONA ENTER PARA VOLVER", True, DARK_GRAY)
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
        # Iniciar oleada 1 al entrar a PLAYING desde MENU
        if old_state == GameState.MENU and new_state == GameState.PLAYING:
            self.reset_game()
            self.wave_number = 1
            self.wave_manager.start_wave(1)
        # Siguiente oleada tras el mensaje "Fin de la Oleada"
        elif old_state == GameState.WAVE_END and new_state == GameState.PLAYING:
            self.wave_number += 1
            self.wave_manager.start_wave(self.wave_number)

    def reset_game(self):
        """Reinicia completamente el juego para una nueva partida."""
        # Reset player
        self.spawn_player()
        # Reset game state
        self.enemies.clear()
        self.projectiles.clear()
        self.barriers.clear()
        self.powerups.clear()
        self.gold = STARTING_GOLD
        self.wave_number = 1
        self.enemies_killed = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self._game_over_triggered = False
        self._victory_triggered = False
        self._screen_shake_intensity = 0.0
        self._screen_shake_timer = 0.0
        # Reset name input
        self.name_input = ""
        # Reset barriers
        self.spawn_barriers()
        # Reset weapon to pistol
        self.current_weapon = self.weapons["pistol"]
        self.player["weapon"] = "pistol"

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
                "color": RED
            }
        }
        return stats.get(weapon, stats["pistol"])

    def fire_weapon(self, angle):
        """Dispara el arma actual"""
        weapon = self.current_weapon
        p = self.player
        if weapon.can_fire(pygame.time.get_ticks() / 1000.0):
            projectiles = weapon.fire(
                x=self.player["x"],
                y=self.player["y"],
                angle=angle,
            )
            self.projectiles.extend(projectiles)
            weapon.reset_cooldown(pygame.time.get_ticks() / 1000.0)
            weapon.trigger_muzzle_flash()
            p["cooldown"] = weapon.cooldown * p.get("cooldown_mult", 1.0)
            # Screen shake por disparo
            self._screen_shake(weapon.screen_shake_intensity, 0.05)

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
        if self.mouse_pressed:
            self.fire_weapon(angle)

        # Cambio de arma (teclas 1-3)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.player["weapon"] = "pistol"
            self.current_weapon = self.weapons["pistol"]
        elif keys[pygame.K_2]:
            self.player["weapon"] = "shotgun"
            self.current_weapon = self.weapons["shotgun"]
        elif keys[pygame.K_3]:
            self.player["weapon"] = "rifle"
            self.current_weapon = self.weapons["rifle"]

        # Actualizar arma actual
        current_time = pygame.time.get_ticks() / 1000.0
        self.current_weapon.update(dt, current_time)

        # timers
        if p["invuln_timer"] > 0:
            p["invuln_timer"] -= dt
            
        #timer cooldown
        if p["cooldown"] > 0:
            p["cooldown"] -= dt 
            if p["cooldown"] < 0:
                p["cooldown"] = 0
        
        # Screen shake timer
        if self._screen_shake_timer > 0:
            self._screen_shake_timer -= dt
            self._screen_shake_intensity *= 0.9

    def update_projectiles(self, dt):
        """Actualiza proyectiles"""
        for proj in self.projectiles[:]:
            if isinstance(proj, Projectile):
                proj.update(dt)
                # Verificar si salió de pantalla
                if proj.is_off_screen() or not proj.alive:
                    self.projectiles.remove(proj)
            else:
                #Compatibilidad con proyectiles dicts
                proj["x"] += proj["vx"] * dt
                proj["y"] += proj["vy"] * dt
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
                    bdx = barrier.x - enemy.x
                    bdy = barrier.y - enemy.y
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
            dx = tx - enemy.x
            dy = ty - enemy.y
            dist = math.hypot(dx, dy)

            if dist > 0:
                # Normalizar y mover
                dx /= dist
                dy /= dist
                enemy.x += dx * enemy.speed * dt
                enemy.y += dy * enemy.speed * dt

            # Colisión con barrera (atacar)
            for barrier in self.barriers:
                if barrier.alive:
                    enemy_rect = pygame.Rect(enemy.x - enemy.radius, enemy.y - enemy.radius, enemy.radius * 2, enemy.radius * 2)
                    if barrier.rect.colliderect(enemy_rect):
                        destroyed = barrier.take_damage(enemy.damage)
                        event_bus.publish(EventType.BARRIER_DAMAGED, {"barrier": barrier, "damage": enemy.damage})
                        if destroyed:
                            event_bus.publish(EventType.BARRIER_DESTROYED, {"barrier": barrier})
                        break  # Una barrera por frame

            # Colisión con player (daño) usa sistema de combate
            player_enemy_collisions = check_player_enemy_collision(self.player, [enemy])
            if player_enemy_collisions:
                died = apply_damage(
                    attacker=enemy,
                    target=self.player,
                    amount=enemy.damage,
                    knockback=50.0,
                    knockback_resist=0.0,
                    damage_type="normal"
                )
                if died:
                    self.player_died()

            # Eliminar enemigos muertos (HP <= 0)
            if enemy.hp <= 0:
                self.enemies.remove(enemy)
                self.gold += enemy.gold
                self.enemies_killed += 1
                event_bus.publish(EventType.ENEMY_DIED, {"enemy": enemy, "gold": enemy.gold})

    def update_barriers(self, dt):
        """Actualizar las barreras y que se eliminen las destruidas"""
        for barrier in self.barriers[:]:
            if not barrier.alive:
                self.barriers.remove(barrier)

    def check_projectile_enemy_collisions(self):
        """Usa el nuevo sistema de combate para colisiones proyectil-enemigo."""
        proj_list = [p for p in self.projectiles if isinstance(p, Projectile)]
        if not proj_list or not self.enemies:
            return
            
        collisions = check_projectile_collisions(proj_list, self.enemies)
        
        for proj, enemy in collisions:
            # Aplicar daño
            died = apply_damage(
                attacker=self.player,
                target=enemy,
                amount=proj.damage,
                damage_type="normal"
            )
            
            # Manejar perforación
            if proj.on_hit():
                if proj in self.projectiles:
                    self.projectiles.remove(proj)
            
            # Si el enemigo murió, dar oro
            if died:
                self.gold += enemy.gold
                self.enemies_killed += 1
                # El evento ENEMY_DIED ya se publica en apply_damage

    def damage_player(self, amount):
        """le aplica daño al jugador cuando es golpeado"""
        if not self.player or self.player["invuln_timer"] > 0:
            return
        
        died = apply_damage(
            attacker={"type": "enemy"},
            target=self.player,
            amount=amount,
            knockback=50.0,
            knockback_resist=0.0,
            damage_type="normal"
        )
        
        if died:
            self.player_died()

    #Callbacks para efectos visuales (registrados en __init__)
    
    def _screen_shake(self, intensity: float, duration: float):
        """Callback para screen shake."""
        self._screen_shake_intensity = intensity
        self._screen_shake_timer = duration

    def _flash_entity(self, entity: dict, duration: float):
        """Callback para flash visual al recibir daño."""
        # Por ahora usa invuln_timer como flash visual
        if entity is self.player:
            entity["invuln_timer"] = max(entity.get("invuln_timer", 0), duration)

    def _on_enemy_died(self, data: dict):
        """Suelta un pickup al azar en la posición del enemigo muerto."""
        enemy = data.get("enemy") or data.get("entity")
        if enemy is None or getattr(enemy, "_pickup_dropped", False):
            return
        enemy._pickup_dropped = True
        if random.random() >= PICKUP_DROP_CHANCE:
            return
        pickup_class = random.choice((HealthPickup, SpeedPickup, RepairPickup))
        self.powerups.append(pickup_class(enemy.x, enemy.y))

    def _on_wave_completed(self, data: dict):
        """Handler para evento WAVE_COMPLETED"""
        gold_bonus = data.get("gold_bonus", 0)
        self.gold += gold_bonus
        self._screen_shake(SCREEN_SHAKE_MAX_INTENSITY, 0.4)

    def player_died(self):
        event_bus.publish(EventType.PLAYER_DIED, {})
        self.change_state(GameState.GAME_OVER)

    def update_powerups(self, dt):
        """Actualiza pickups, recoge los tocados y elimina los agotados."""
        if not self.player:
            return
        player_rect = pygame.Rect(self.player["x"] - 16, self.player["y"] - 16, 32, 32)
        for powerup in self.powerups[:]:
            powerup.update(dt)
            if not powerup.alive:
                self.powerups.remove(powerup)
                continue
            if powerup.collides(player_rect):
                powerup.apply(self.player, self.barriers)
                powerup.alive = False
                self.powerups.remove(powerup)

    def update(self, dt):
        self.update_player(dt)
        self.update_projectiles(dt)
        self.update_enemies(dt)
        self.check_projectile_enemy_collisions()
        self.update_barriers(dt)
        self.update_powerups(dt)

        # WaveManager maneja oleadas y spawneo
        self.wave_manager.update(dt)

    def draw_name_entry(self):
        """Dibuja la pantalla para ingresar el nombre del highscore."""
        self.screen.fill(RED)

        # Título
        title = self.big_font.render("ENTRAS EN EL TOP", True, YELLOW)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title, title_rect)

        # Mensaje
        msg = self.font.render(f"Llegaste a la oleada {self.wave_number}", True, WHITE)
        msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 40))
        self.screen.blit(msg, msg_rect)

        # Input de nombre (3 letras)
        # Cursor parpadeante
        cursor_visible = (pygame.time.get_ticks() // 500) % 2 == 0

        # Dibujar 3 cuadros para las letras
        box_size = 50
        spacing = 10
        total_width = 3 * box_size + 2 * spacing
        start_x = WIDTH // 2 - total_width // 2
        y = HEIGHT // 2

        for i in range(3):
            x = start_x + i * (box_size + spacing)
            # Fondo del cuadro
            box_rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(self.screen, DARK_GRAY, box_rect)
            pygame.draw.rect(self.screen, WHITE, box_rect, 3)

            # Letra
            if i < len(self.name_input):
                letter = self.name_input[i]
                letter_surf = self.big_font.render(letter, True, YELLOW)
                letter_rect = letter_surf.get_rect(center=box_rect.center)
                self.screen.blit(letter_surf, letter_rect)
            elif i == len(self.name_input) and cursor_visible:
                # Cursor parpadeante
                cursor_surf = self.big_font.render("_", True, YELLOW)
                cursor_rect = cursor_surf.get_rect(center=box_rect.center)
                self.screen.blit(cursor_surf, cursor_rect)

        # Instrucciones
        instr1 = self.font.render("A-Z: escribir  |  BORRAR: borrar", True, GRAY)
        instr1_rect = instr1.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        self.screen.blit(instr1, instr1_rect)

        instr2 = self.font.render("ENTER para confirmar", True, GRAY)
        instr2_rect = instr2.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(instr2, instr2_rect)

        pygame.display.flip()

    def handle_events_wave_end(self):
        """Maneja eventos durante el mensaje 'Fin de la Oleada'."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False

    def _update_wave_end(self, dt: float):
        """Avanza el temporizador de 'Fin de la Oleada' y pasa a PLAYING al terminar."""
        self._wave_end_timer += dt
        if self._wave_end_timer >= self.WAVE_END_DURATION:
            self._wave_end_timer = 0.0
            self.change_state(GameState.PLAYING)

    def draw_wave_end(self):
        """Dibuja el mensaje 'Fin de la Oleada' entre oleadas."""
        self.screen.fill(BLACK)

        title_text = self.big_font.render("BIEN HECHO, FIN DE LA OLEADA", True, YELLOW)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(title_text, title_rect)

        instr = self.font.render("VIENE LA SIGUIENTE...", True, WHITE)
        instr_rect = instr.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(instr, instr_rect)

        pygame.display.flip()

    def draw_game_over(self):
        """Dibuja la pantalla de game over / victoria."""
        self.screen.fill(RED)

        if self._victory_triggered:
            text = self.big_font.render("¡VICTORIA!", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, rect)

            text = self.font.render(f"Llegaste a la oleada {self.wave_number}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)
        else:
            text = self.big_font.render("FIN DEL JUEGO", True, BLACK)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, rect)

            text = self.font.render(f"Oleada: {self.wave_number}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(text, rect)

            text = self.font.render(f"Oro: {self.gold}", True, WHITE)
            rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            self.screen.blit(text, rect)

        text = self.font.render("PRESIONA ENTER PARA VOLVER AL MENÚ", True, WHITE)
        rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.screen.blit(text, rect)

        pygame.display.flip()