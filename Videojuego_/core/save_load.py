"""Sistema de guardado/carga de highscores y estadísticas.

Maneja persistencia en JSON: top 5 highscores, estadísticas totales, unlocks.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from config import *

# Archivo de guardado en la misma carpeta que main.py
_SAVE_FILE = Path(__file__).resolve().parents[1] / "save_data.json"

# Estructura por defecto
_DEFAULT_SAVE = {
    "highscores": [],
    "total_stats": {
        "games_played": 0,
        "total_enemies_killed": 0,
        "total_gold_earned": 0,
        "total_waves_cleared": 0,
        "best_wave": 0,
    },
    "unlocks": {},
    "version": 1,
}


def _load_raw() -> dict:
    """Carga el JSON crudo o devuelve estructura por defecto."""
    if _SAVE_FILE.exists():
        try:
            with open(_SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**_DEFAULT_SAVE, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return _DEFAULT_SAVE.copy()


def _save_raw(data: dict) -> None:
    """Guarda el diccionario completo en JSON."""
    try:
        with open(_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass  # Silencioso: si no se puede guardar, el juego sigue funcionando

# HIGHSCORES (Top 5)

def load_highscores() -> List[dict]:
    """Devuelve lista de highscores ordenados (mejor primero)."""
    data = _load_raw()
    return data.get("highscores", [])


def save_highscores(scores: List[dict]) -> None:
    """Guarda la lista completa de highscores."""
    data = _load_raw()
    data["highscores"] = scores
    _save_raw(data)


def add_highscore(name: str, wave: int, gold: int) -> int:
    """
    Añade un highscore y devuelve su posición en el ranking (1-indexed).
    Retorna 0 si no entró en el top 5.
    """
    from datetime import datetime
    
    data = _load_raw()
    scores = data.get("highscores", [])
    
    new_entry = {
        "name": name[:12],           # Máx 12 chars
        "wave": wave,
        "gold": gold,
        "date": datetime.now().strftime("%d/%m/%Y"),
    }
    
    scores.append(new_entry)
    # Ordenar: mayor wave primero, luego mayor gold
    scores.sort(key=lambda s: (s["wave"], s["gold"]), reverse=True)
    # Mantener solo top 5
    scores = scores[:5]
    
    data["highscores"] = scores
    _save_raw(data)
    
    # Devolver posición (1-indexed) o 0 si no entró
    try:
        return scores.index(new_entry) + 1
    except ValueError:
        return 0


def is_new_highscore(wave: int, gold: int) -> bool:
    """Verifica si una puntuación entraría en el top 5."""
    scores = load_highscores()
    if len(scores) < 5:
        return True
    worst = scores[-1]
    return (wave > worst["wave"]) or (wave == worst["wave"] and gold > worst["gold"])


def get_highscores() -> List[dict]:
    """Alias para load_highscores (compatibilidad)."""
    return load_highscores()

# ESTADÍSTICAS TOTALES

def load_total_stats() -> dict:
    """Devuelve estadísticas acumuladas."""
    data = _load_raw()
    return data.get("total_stats", _DEFAULT_SAVE["total_stats"]).copy()


def update_total_stats(
    games_played: int = 0,
    enemies_killed: int = 0,
    gold_earned: int = 0,
    waves_cleared: int = 0,
    best_wave: int = 0,
) -> None:
    """Actualiza estadísticas acumuladas (suma o max)."""
    data = _load_raw()
    stats = data.setdefault("total_stats", _DEFAULT_SAVE["total_stats"].copy())
    
    stats["games_played"] += games_played
    stats["total_enemies_killed"] += enemies_killed
    stats["total_gold_earned"] += gold_earned
    stats["total_waves_cleared"] += waves_cleared
    stats["best_wave"] = max(stats.get("best_wave", 0), best_wave)
    
    _save_raw(data)

# UNLOCKS (Mejoras permanentes entre partidas)

def load_unlocks() -> dict:
    """Devuelve dict de unlocks {id: bool}."""
    data = _load_raw()
    return data.get("unlocks", {}).copy()


def unlock_permanent(unlock_id: str) -> None:
    """Marca un unlock permanente como desbloqueado."""
    data = _load_raw()
    data.setdefault("unlocks", {})[unlock_id] = True
    _save_raw(data)


def is_unlocked(unlock_id: str) -> bool:
    """Verifica si un unlock está desbloqueado."""
    unlocks = load_unlocks()
    return unlocks.get(unlock_id, False)


def reset_all_data() -> None:
    """Borra todo el guardado (para testing o 'New Game+')."""
    if _SAVE_FILE.exists():
        _SAVE_FILE.unlink()

# COMPATIBILIDAD HACIA ADELANTE

def migrate_save_if_needed() -> None:
    """Migra save_data.json de versiones antiguas al formato actual."""
    data = _load_raw()
    current_version = data.get("version", 0)
    
    if current_version < 1:
        # v0 -> v1: asegurar estructura
        if "highscores" not in data:
            data["highscores"] = []
        if "total_stats" not in data:
            data["total_stats"] = _DEFAULT_SAVE["total_stats"]
        if "unlocks" not in data:
            data["unlocks"] = {}
        data["version"] = 1
        _save_raw(data)