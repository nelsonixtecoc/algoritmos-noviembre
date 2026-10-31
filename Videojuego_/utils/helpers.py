import random


def random_spawn_point(
    screen_width: int,
    screen_height: int,
    margin: int = 50
) -> tuple[float, float]:

    side = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left
    if side == 0:  # top
        return (random.uniform(-margin, screen_width + margin), -margin)
    elif side == 1:  # right
        return (screen_width + margin, random.uniform(-margin, screen_height + margin))
    elif side == 2:  # bottom
        return (random.uniform(-margin, screen_width + margin), screen_height + margin)
    else:  # left
        return (-margin, random.uniform(-margin, screen_height + margin))
