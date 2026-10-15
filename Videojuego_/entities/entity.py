import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, hp):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y) #Donde esta ubicado en el mapa las coordenadas de X y Y
        self.vel = pygame.math.Vector2(0, 0)
        self.hp = hp  #Cuanta vida tiene
        self.max_hp = hp
        self.alive = True   #Si esta vivo (True o muerto False)
        
        #Crea un cuadrado blanco de tamaño 32*32 para que se vea algo en la pantalla
        self.image = pygame.Surface((32,32))
        self.image.fill((255, 255, 255))
        
        #Crea una caja invisible alrededor del cuadrado para chocar con cosas
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def update(self, dt):
        #Si la vida llea a 0, cambia su estado a muerto
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface, camera_offset=(0, 0)):
        #Si sigue vivo, lo dibuja en la pantalla
        if self.alive:
            ox, oy = camera_offset
            surface.blit(self.image, (self.rect.x - ox, self.rect.y - oy))
            
    def take_damage(self,amount):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False
