import sys

import pygame

from config import HEIGHT, WIDTH
from core.game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Proyecto")
    game = Game(screen)
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()




