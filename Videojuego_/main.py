import pygame
import sys

from config import WIDTH, HEIGHT, FPS
from core.game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombies")
    game = Game(screen)
    game.run()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()