import pygame

from entities.entity import Entity
from utils.animation import AnimationPlayer
from systems.combat import apply_damage, check_sword_hit

class Player(Entity):
    def __init__(self, x, y, hp=10):
        super().__init__(x,y,hp)
        
        self.speed = 200
        self.direction = pygame.math.Vector2(0,0)
        self.facing_direction = pygame.math.Vector2(0, 1)
        
        self.animator = AnimationPlayer()
        self._setup_animations()
        
        self.is_attacking = False
        self.attack_cooldown_timer = 0.0
        self.attack_cooldown_timer = 0.0
        self.attack_damage = 2
        self.knockback_force = 100
        self.attack_hitbox = None
        
        self.is_invulnerable = False
        self.invulnerability_timer = 0.0
        
    def _setup_animations(self):
        base_surface = pygame.Surface((32, 32))
        base_surface.fill((0, 150, 255))
        self.animator.add_animation('idle', [base_surface])
        self.animator.add_animation('walk', [base_surface])
        self.animator.add_animation('attack', [base_surface])
        self.animator.add_animation('hurt', [base_surface])
        self.animator.add_animation('death', [base_surface])
        
    def trigger_invulnerability(self):
        self.is_invulnerable = True
        self.invulnerability_timer = 1.0
        
    def get_input(self):
        if self.is_attacking:
            return
        
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
            self.facing_direction = pygame.math.Vector2(self.direction)
            
        if (keys[pygame.K_SPACE] or keys[pygame.K_j]) and self.attack_cooldown_timer <= 0:
            self.start_attack() 
    
    def start_attack(self):
        self.is_attacking = True
        self.attack_cooldown_timer = 0.4
        self.attack_cooldown_timer = 0.2
        
        offset = 24
        hitbox_center = self.rect.center + (self.facing_direction * offset)
        self.attack_hitbox = pygame.Rect(0, 0, 28, 28)
        self.attack_hitbox.center = (round(hitbox_center.x), round(hitbox_center.y))
    
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
                    
    def update(self, dt, walls=[], targets=[]):
        super().update(dt)
        if not self.alive:
            self.animator.set_state('death')
            return
        
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt
            
        if self.is_attacking:
            self.attack_cooldown_timer -= dt
            check_sword_hit(self, targets)
            if self.attack_duration_timer <= 0:
                self.is_attacking = False
                self.attack_hitbox = None
            
        if self.is_invulnerable:
            self.invulnerability_timer -= dt
            if self.invulnerability_timer <= 0:
                self.is_invulnerable = False
                
        self.get_input()
        self.move(dt, walls)
        
        if self.is_attacking:
            self.animator.set_state('attack')
        elif self.direction.length() > 0:
            self.animator.set_state('walk')
        else:
            self.animator.set_state('idle')
            
            frame = self.animator.update(dt)
            if frame:
                self.image = frame
                
    def draw(self, surface):
        if self.is_invulnerable and int(pygame.time.get_ticks() / 100) % 2 == 0:
            return
        
        super().draw(surface)
        
        if self.is_attacking and self.attack_hitbox:
            pygame.draw.rect(surface, (255, 0, 0), self.attack_hitbox, 1)