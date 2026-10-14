import pygame 

class Entity(pygame.sprite.Sprite): 
    def __init__(self, x, y, hp): 
        super().__init__() 
        self.pos = pygame.math.Vector2(x, y) #Donde esta ubicado en el mapa(coordenadas X y Y)
        self.hp = hp #Cuento de vida tiene
        self.alive = True #Si esta vivo o esta muerto 
        
        #Crea un cuadrado blanco de tamaño 32*32 para que se vea algo en la pantalla
        self.image = pygame.Surface((32,32))
        self.image.fill((255, 255, 255))
        
        #Crea una caja invisible alrededor del cuadrado para chocar con cosas
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
        
        def update(self, dt):
            #Si la vida llega a 0, cambia su estado a muerto
            if self.hp <= 0:
                self.alive = False
            
        def draw(self, surface):
            #Si sigue vivo, lo dibuja en la pantalla
            if self.alive:
                surface.blit(self.image, self.rect)