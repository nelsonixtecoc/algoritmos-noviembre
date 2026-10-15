import pygame

from entities.entity import Entity
from utils.animation import AnimationPlayer


class Player(Entity): #Hereda todo lo de la plantilla base (Entity)
    def __init__(self, x, y, hp=10):
        super().__init__(x,y,hp) # Configura su posicion y 10 de vida inicial
        self.speed = 200         # Qué tan rapido camina (200 pixeles por segundo)
        self.direction = pygame.math.Vector2(0,0) # Hacia donde apunta su movimiento

        self.animator = AnimationPlayer() # Prepara su álbun de animaciones
        self._setup_animations()

    def _setup_animations(self):
        # Crea una cajita azul de prueba mientras no tengamos dibujos reales
        base_surface = pygame.Surface((32,32))
        base_surface.fill((0, 150, 255))
        self.animator.add_animation('idle', [base_surface])
        self.animator.add_animation('walk', [base_surface])

    def get_input(self):
        # Mira qué teclas estás presionando en el teclado en este preciso instante
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0
        
        # Si presionas W o flecha arriba -> se mueve hacia arriba
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y -= 1
        # Si presiona S o fecha abajo -> se mueve hacia abajo
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y += 1
        # Si presiona A o fecha izquierda -> se mueve a la izquierda
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x -= 1
        # Si presiona D o flecha derecha -> se mueve a la derecha
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x += 1

        # Arregla el movimiento en diagonal para que no camine mas rapido de lo normal
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

    def move(self, dt, walls):
        # Mueve al jugador horizontalmente y revisa si choca con una pared
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.check_collision(walls, 'horizontal')
        
    # Mueve al jugador verticalmente y revisa si choca con una pared
    def move(self, dt, walls):
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.check_collision(walls, 'vertical')

    def check_collision(self, walls, direction):
        #Revisa cada pared del juego para ver si tu caja invisible lo esta tocando
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: # Si iba a la derecha, lo frena pegandolo a la pared
                        self.rect.left = wall.rect.left
                    if self.direction.x < 0: # Si iba a la izquierda, lo frena
                        self.rect.left = wall.rect.right
                    self.pos.x = self.rect.centerx
                if direction == 'vertical':
                    if self.direction.y > 0: # Si iba hacia abajo, lo frena
                        self.rect.bottom = wall.rect.top
                    if self.direction.y < 0: # Si iba hacia arriba, lo frena
                        self.rect.top = wall.rect.bottom
                    self.pos.y = self.rect.centery

    def update(self, dt, walls=[]):
        super().update(dt) #Revisa si sigue con vida
        if self.alive:
            self.get_input() # Lee tus teclas
            self.move(dt, walls) # Lo mueve y cuida que no atraviese paredes
            
            # Decide si muestra la animacion de caminar o de estar quieto
            if self.direction.length() > 0:
                self.animator.set_state('walk')
            else:
                self.animator.set_state('idle')

            # Actualiza la imagen visible en pantalla segun la animacion
            frame = self.animator.update(dt)
            if frame:
                self.image = frame
