from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

import pygame

from config import WIDTH, HEIGHT, FPS

if TYPE_CHECKING:
    from core.camera import camera
    from core.events import EventBus

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

Game.init
def __init__(self, screen: pygame.surface):
    self.screen = screen
    self.clock = pygame.time.Clock()
    self.running = True
    self.dt = 0,0
    
    self.state = GameState.MENU
    
    self.event_bus = EventBus()
    self.camera = Camera(0,0) #esto es temporal xddd
    
    self.current_room = None
    self.player = None
    
def run(self):
    while self.running:
        self.dt = self.clock.tick(FPS) / 1000.0
        self._handle_events()
        self._update()
        self._draw()
        
def _handle_events(self):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._handle_escape()

def _handle_escape(self):
    if self.state == GameState.PLAYING:
        self.change_state(GameState.PAUSED)
    elif self.state == GameState.PAUSED:
        self.change_state(GameState.PLAYING)
    elif self.state == GameState.MENU:
        self.running = False
    elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
        self.change_state(GameState.MENU)

def _update(self):
    if self.state == GameState.PLAYING:
        self._update_playing()
    elif self.state == GameState.PAUSED:
        pass
    elif self.state == GameState.MENU:
        self._update_menu()
        
def _update_playing(self):
    if self.player:
        self.player.update(self.dt)
    
    if self.current_room:
        self.current_room.update(self.dt, self.event_bus)
        
    if self.player:
        self.camera.follow(self.player.pos)
        
    self.event_bus.process()
    
def _draw(self):
    self.screen.fill((0,0,0))
    
    if self.state == GameState.PLAYING:
        self._draw_playing()
    elif self.state == GameState.PAUSED:
        self._draw_playing()
        self._draw_pause_overlay()
    #posibles otros estados que quizas se agregen a futuro
    
    pygame.display.flip()
    
def _draw_playing(self):
    if self.current_room:
        self.current_room.draw(self.screen, self.camera)
    
    if self.player:
        self.player.draw(self.screen, self.camera)
    if self.current_room:
        self.current_room.draw_entities(self.screen, self.camera)
    self._draw_hud()
    
def change_state(self, new_state: GameState):
    old_state = self.state 
    self.state = new_state
    
    if new_state == GameState.PLAYING:
        self._on_enter_playing()
    elif old_state == GameState.PLAYING and new_state == GameState.PAUSED:
        self._on_exit_playing()
        
def _on_enter_playing(self):
    #cargar room, spawn, resetear las oleadas
    pass

def _on_exot_playing(self):
    #guardar estado, paudar musica, etc
    pass
