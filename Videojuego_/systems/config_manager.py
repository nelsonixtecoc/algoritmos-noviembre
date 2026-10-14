"""Sistema de configuración persistente para el videojuego.

Maneja las preferencias del jugador como volumen y modo de pantalla.
Guarda y carga la configuración en un archivo JSON local.

Asegura que el directorio de datos exista antes de leer/escribir archivos.
"""

import json
import os
from pathlib import Path

_PREFS_FILE = Path(__file__).resolve().parents[2] / "data" / "prefs.json"

# Valores predeterminados seguros
DEFAULT_PREFS = {
    "volume_music": 0.5,
    "volume_sfx": 0.8,
    "fullscreen": False,
    "resolution": "640x480",
}

_prefs_loaded = False
_prefs = {}


def _ensure_data_dir() -> None:
    """Crear el directorio data si no existe."""
    data_dir = _PREFS_FILE.parent
    data_dir.mkdir(parents=True, exist_ok=True)


def load_prefs() -> dict:
    """Cargar preferencias desde el archivo, o retornar valores predeterminados."""
    global _prefs, _prefs_loaded
    
    if _prefs_loaded:
        return _prefs
    
    _ensure_data_dir()
    
    try:
        if os.path.exists(_PREFS_FILE):
            with open(_PREFS_FILE, "r", encoding="utf-8") as f:
                _prefs = json.load(f)
                # Asegurar que todas las claves existan
                for key, default in DEFAULT_PREFS.items():
                    if key not in _prefs:
                        _prefs[key] = default
        else:
            _prefs = dict(DEFAULT_PREFS)
            save_prefs()  # Crear el archivo con valores por defecto
    except (json.JSONDecodeError, IOError, OSError) as e:
        print(f"Error al cargar preferencias: {e}")
        _prefs = dict(DEFAULT_PREFS)
    
    _prefs_loaded = True
    return _prefs


def save_prefs() -> bool:
    """Guardar preferencias en el archivo."""
    _ensure_data_dir()
    try:
        with open(_PREFS_FILE, "w", encoding="utf-8") as f:
            json.dump(_prefs, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"Error al guardar preferencias: {e}")
        return False


def get(key: str, default=None):
    """Obtener un valor de preferencia."""
    prefs = load_prefs()
    return prefs.get(key, default if default is not None else DEFAULT_PREFS.get(key))


def set(key: str, value) -> bool:
    """Establecer un valor de preferencia y guardar."""
    global _prefs
    prefs = load_prefs()
    prefs[key] = value
    _prefs = prefs
    return save_prefs()


def toggle_fullscreen() -> bool:
    """Alternar entre modo ventana y pantalla completa, guardando la preferencia."""
    current = get("fullscreen", False)
    new_state = not current
    if set("fullscreen", new_state):
        return new_state
    return current  # Fallback si falla el guardado