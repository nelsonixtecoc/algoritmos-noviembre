import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, lifetime, owner):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime
        self.owner = owner
        
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        
    def update (self, dt, walls=[]):
        self.lifertime -= dt
        if self.lifetime <= 0:
            self.kill()
            return
        
        self.pos += self.direction * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.kill()
                break