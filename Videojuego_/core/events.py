from collections.abc import Callable
from enum import Enum
from typing import Any


# Estados del juego
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    WAVE_END = "wave_end"
    PAUSED = "paused"
    CONFIG = "config"
    HIGHSCORES = "highscores"
    GAME_OVER = "game_over"
    NAME_ENTRY = "name_entry"


#tipos de eventos
class EventType(Enum):
    #Jugador
    PLAYER_DAMAGED = "player_damaged"
    PLAYER_DIED = "player_died"
    PLAYER_SHOOT = "player_shoot"
    WEAPON_SWITCHED = "weapon_switched"
    #enemigos
    ENEMY_SPAWNED = "enemy_spawned"
    ENEMY_DIED = "enemy_died"
    ENEMY_REACHED_BASE = "enemy_reached_base"
    #las barreras
    BARRIER_DAMAGED = "barrier_damaged"
    BARRIER_DESTROYED = "barrier_destroyed"
    #ordas / oleadas
    WAVE_STARTED = "wave_started"
    WAVE_COMPLETED = "wave_completed"
    #sistema
    GOLD_CHANGED = "gold_changed"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    STATE_CHANGED = "state_changed"

    #el BUS
class EventBus:
    def __init__(self): #EL eventType es la lista de funciones que escuchan
        self._listeners: dict[EventType, list[Callable]] = {} #se inicia la lista vacia por cada tipo
        for event_type in EventType:
            self._listeners[event_type] = []

    def subscribe(self, event_type: EventType, callback: Callable):
        """Un modulo dice: 'avísame cuando pase X'"""
        self._listeners[event_type].append(callback)
    def publish(self, event_type: EventType, data: Any = None):
        """Algo pasa: Pasó X cosa, llama a todos los que escuchan"""
        for callback in self._listeners[event_type]:
            callback(data)

#Esta es la instancia global
event_bus = EventBus()
