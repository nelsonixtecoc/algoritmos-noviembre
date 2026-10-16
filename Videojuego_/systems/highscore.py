"""Sistema de highscores (mejores puntuaciones).

Almacena y carga las mejores puntuaciones en un archivo local.
Soporta hasta 5 récords y maneja archivos inexistentes o dañados.

Asegura que el directorio de datos exista antes de leer/escribir archivos.
"""

import json
from pathlib import Path

_HIGHSCORES_FILE = Path(__file__).resolve().parents[2] / "data" / "highscores.json"
_MAX_SCORES = 5


def _ensure_data_dir() -> None:
    """Crear el directorio data si no existe."""
    data_dir = _HIGHSCORES_FILE.parent
    data_dir.mkdir(parents=True, exist_ok=True)


def _load_highscores() -> list[dict]:
    """Cargar highscores desde el archivo, o retornar lista vacía."""
    _ensure_data_dir()
    try:
        with open(_HIGHSCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Validar estructura
            if isinstance(data, list) and len(data) > 0:
                # Asegurar que cada entrada tenga nombre y puntuación
                validated = []
                for entry in data:
                    if isinstance(entry, dict) and "name" in entry and "score" in entry:
                        validated.append({
                            "name": str(entry["name"]),
                            "score": int(entry["score"]),
                        })
                return validated if validated else []
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        pass
    return []


def _save_highscores(scores: list[dict]) -> bool:
    """Guardar highscores en el archivo."""
    _ensure_data_dir()
    try:
        with open(_HIGHSCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"No se pudieron guardar los highscores: {e}")
        return False


def get_highscores() -> list[dict]:
    """Obtener la lista de highscores (ordenada de mayor a menor)."""
    scores = _load_highscores()
    # Ordenar por puntuación de mayor a menor
    scores.sort(key=lambda x: x["score"], reverse=True)
    # Limitar a máximo 5
    return scores[:_MAX_SCORES]


def add_highscore(name: str, score: int) -> list[dict]:
    """Añadir una nueva puntuación y devolver la lista actualizada."""
    if not name or score < 0:
        return get_highscores()

    scores = _load_highscores()
    scores.append({"name": name[:20], "score": int(score)})  # Limitar nombre a 20 chars
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)
    scores = scores[:_MAX_SCORES]  # Mantener solo los 5 mejores

    if _save_highscores(scores):
        return scores
    return get_highscores()  # Return current even if save failed


def is_new_highscore(score: int) -> bool:
    """Verificar si una puntuación entra en el top 5."""
    scores = get_highscores()
    if len(scores) < _MAX_SCORES:
        return True
    return score > scores[-1]["score"] if scores else True