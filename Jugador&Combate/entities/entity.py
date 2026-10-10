import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, hp):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.hp = hp
        self.alive = True
        self.image = pygame.Surface((32,32))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        
        def update(self, dt):
            if self.hp <= 0:
                self.alive = False
            
        def draw(self, surface):
            if self.alive:
                surface.blit(self.image, self.rect)
