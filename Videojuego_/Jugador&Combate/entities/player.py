import pygame
from entities.entity import Entity
from utils.animation import AnimationPlayer

class Player(Entity):
    def __init__(self, x, y, hp=10):
        super().__init__(x,y,hp)
        self.speed = 200
        self.direction = pygame.math.Vector2(0,0)
        
        self.animator = AnimationPlayer()
        self._setup_animations()
    
    def _setup_animations(self):
        base_surface = pygame.Surface((32,32))
        base_surface.fill((0, 150, 255))
        self.animator.add_animation('idle', [base_surface])
        self.animator.add_animation('walk', [base_surface])
        
    def get_input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y -= 1
            
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y += 1
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x -= 1
            
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x += 1
            
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
    
    def move(self, dt, walls):
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.check_collision(walls, 'horizontal')
        
    def move(self, dt, walls):
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.check_collision(walls, 'vertical')
        
    def check_collision(self, walls, direction):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.left = wall.rect.left
                    if self.direction.x < 0:
                        self.rect.left = wall.rect.right
                    self.pos.x = self.rect.centerx
                if direction == 'vertical':
                    if self.direction.y > 0:
                        self.rect.bottom = wall.rect.top
                    if self.direction.y < 0: 
                        self.rect.top = wall.rect.bottom
                    self.pos.y = self.rect.centery
                    
    def update(self, dt, walls=[]):
        super().update(dt)
        if self.alive:
            self.get_input()
            self.move(dt, walls)
            
            if self.direction.length() > 0:
                self.animator.set_state('walk')
            else:
                self.animator.set_state('idle')
                
            frame = self.animator.update(dt)
            if frame:
                self.image = frame