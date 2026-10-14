import math
import random

import pygame  # solo para load_spritesheet


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Limita ``value`` al rango ``[min_val, max_val]``.

    Args:
        value: Valor a limitar.
        min_val: Límite inferior (inclusive).
        max_val: Límite superior (inclusive).

    Returns:
        ``value`` si está en rango, ``min_val`` si es menor, ``max_val`` si es mayor.

    Example:
        >>> clamp(150, 0, 100)
        100
        >>> clamp(-10, 0, 100)
        0
    """
    return max(min_val, min(value, max_val))


def lerp(a: float, b: float, t: float) -> float:
    """Interpola linealmente entre ``a`` y ``b`` por factor ``t``.

    Args:
        a: Valor inicial (t=0).
        b: Valor final (t=1).
        t: Factor de interpolación [0, 1]. Valores fuera extrapolan.

    Returns:
        Valor interpolado: ``a + (b - a) * t``.

    Example:
        >>> lerp(0, 100, 0.5)
        50.0
    """
    return a + (b - a) * t


def angle_to(from_pos: tuple[float, float], to_pos: tuple[float, float]) -> float:
    """Calcula el ángulo en radianes desde ``from_pos`` hacia ``to_pos``.

    Args:
        from_pos: Tupla (x, y) origen.
        to_pos: Tupla (x, y) destino.

    Returns:
        Ángulo en radianes [-pi, pi], 0 = derecha, sentido antihorario.

    Example:
        >>> angle_to((0, 0), (1, 0))
        0.0
        >>> angle_to((0, 0), (0, 1))
        1.5707... # pi/2
    """
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    return math.atan2(dy, dx)


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia euclidiana entre dos puntos 2D.

    Args:
        a: Tupla (x, y).
        b: Tupla (x, y).

    Returns:
        Distancia ``sqrt((ax-bx)^2 + (ay-by)^2)``.

    Example:
        >>> distance((0, 0), (3, 4))
        5.0
    """
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


def load_spritesheet(
    path: str,
    frame_width: int,
    frame_height: int,
    *,
    columns: int = None,
    rows: int = None,
    scale: float = 1.0,
    colorkey: tuple[int, int, int] = None
) -> list[pygame.Surface]:
    """Corta un spritesheet en frames individuales.

    Args:
        path: Ruta al archivo .png del spritesheet.
        frame_width: Ancho de cada frame en píxeles.
        frame_height: Alto de cada frame en píxeles.
        columns: Número de columnas (si None, se calcula por ancho total).
        rows: Número de filas (si None, se calcula por alto total).
        scale: Factor de escalado aplicado a cada frame (default 1.0).
        colorkey: Color a tratar como transparente (RGB), ej. (0, 0, 0).

    Returns:
        Lista de ``pygame.Surface`` en orden de lectura: fila 0 (col 0..n), fila 1, ...

    Raises:
        FileNotFoundError: Si ``path`` no existe.
        ValueError: Si dimensions no dividen exactamente el spritesheet.
    """
    sheet = pygame.image.load(path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()

    if columns is None:
        columns = sheet_w // frame_width
    if rows is None:
        rows = sheet_h // frame_height

    if columns * frame_width != sheet_w or rows * frame_height != sheet_h:
        raise ValueError(
            f"Spritesheet {sheet_w}x{sheet_h} no divisible en "
            f"{columns}x{rows} frames de {frame_width}x{frame_height}"
        )

    frames = []
    for row in range(rows):
        for col in range(columns):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface((x, y, frame_width, frame_height))
            if scale != 1.0:
                new_size = (int(frame_width * scale), int(frame_height * scale))
                frame = pygame.transform.scale(frame, new_size)
            if colorkey:
                frame.set_colorkey(colorkey)
            frames.append(frame)

    return frames


def random_spawn_point(
    screen_width: int,
    screen_height: int,
    margin: int = 50
) -> tuple[float, float]:
    """Genera posición aleatoria en el borde de la pantalla (fuera de vista).

    Útil para spawnear enemigos que entran desde fuera.

    Args:
        screen_width: Ancho de la pantalla (ej. 640).
        screen_height: Alto de la pantalla (ej. 480).
        margin: Píxeles fuera del borde (default 50).

    Returns:
        Tupla (x, y) en uno de los 4 bordes: top, right, bottom, left.

    Example:
        >>> x, y = random_spawn_point(640, 480)
        >>> assert x < -50 or x > 690 or y < -50 or y > 530
    """
    side = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
    if side == 0:  # top
        return (random.uniform(-margin, screen_width + margin), -margin)
    elif side == 1:  # right
        return (screen_width + margin, random.uniform(-margin, screen_height + margin))
    elif side == 2:  # bottom
        return (random.uniform(-margin, screen_width + margin), screen_height + margin)
    else:  # left
        return (-margin, random.uniform(-margin, screen_height + margin))
