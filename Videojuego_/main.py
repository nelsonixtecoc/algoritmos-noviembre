import pygame
import sys

from config import WIDTH, HEIGHT, FPS
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Videojuego")
    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running == False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            screen.fill((0,0,0))
            pygame.display.flip()
    pygame.quit()
    sys.exit()

#esto es importante por si necesitan importar main sin que se ejecute el archivo
if __name__ == "__main__":
    main()