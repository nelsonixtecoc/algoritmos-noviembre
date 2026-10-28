import random


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
