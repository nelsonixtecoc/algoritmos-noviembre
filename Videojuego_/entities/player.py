import pygame

from config import HEIGHT, PLAYER_HP, PLAYER_INVULN_TIME, PLAYER_SPEED, WIDTH
from entities.entity import Entity
from utils.animation import AnimationPlayer


class Player(Entity): #Hereda todo lo de la plantilla base (Entity)
    WEAPON_NAMES = ["pistol", "shotgun", "rifle"]
    WEAPON_COLORS = [(0, 150, 255), (255,165, 0), (0, 255,255)]
    
    def __init__(self, x, y,):
        super().__init__(x,y, PLAYER_HP) # Configura su posicion y 10 de vida inicial
        self.speed = PLAYER_SPEED       # Qué tan rapido camina (200 pixeles por segundo)
        self.direction = pygame.math.Vector2(0,0) # Hacia donde apunta su movimiento
        self.gold = 0
        self.invuln_time = 0.0
        self.weapon_index = 0

        self.animator = AnimationPlayer() # Prepara su álbun de animaciones
        self._setup_animations()

    def _setup_animations(self):
        #Creamos una cajita azul de prueba mientras no tengamos dibujos reales
        base_surface = pygame.Surface((32,32))
        base_surface.fill(self.WEAPON_COLORS[self.weapon_index])
        self.animator.add_animation('idle', [base_surface])
        self.animator.add_animation('walk', [base_surface])

    @property
    def weapon_name(self):
        return self.WEAPON_NAMES[self.weapon_index]
    
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
    
    def handle_weapon_switch(self):
        keys = pygame.key.get_pressed()
        new_index = self.weapon_index
        if keys[pygame.K_1]:
            new_index = 0
        elif keys[pygame.K_2]:
            new_index = 1
        elif keys [pygame.K_3]:
            new_index = 2
        if new_index != self.weapon_index:
            self.weapon_index = new_index
            self._setup_animations()

    def move(self, dt, walls):
        # Mueve al jugador horizontalmente y revisa si choca con una pared
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.check_collision(walls, 'horizontal')
        
    # Mueve al jugador verticalmente y revisa si choca con una pared
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        self.check_collision(walls, 'vertical')
        
        self.clamp_to_screen()
        
    def clamp_to_screen(self):
        half = self.rect.width // 2
        self.pos.x = max(half, min(WIDTH - half, self.pos.x))
        self.pos.y = max(half, min(HEIGHT - half, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

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
                    
    def take_damage(self, amount):
        if self.invuln_time > 0:
            return False
        self.hp = max(0, self.hp - amount)
        self.invuln_time = PLAYER_INVULN_TIME
        if self.hp == 0:
            self.alive = False
        return True

    def update(self, dt, walls=None):
        super().update(dt) #Revisa si sigue con vida
        if not self.alive:
            return
        if walls is None:
            walls = []
        self.get_input() # Lee tus teclas
        self.handle_weapon_switch()
        self.move(dt, walls) # Lo mueve y cuida que no atraviese paredes
        
        if self.invuln_time > 0:
            self.invuln_time -= dt
            
        # Decide si muestra la animacion de caminar o de estar quieto
        if self.direction.length() > 0:
            self.animator.set_state('walk')
        else:
            self.animator.set_state('idle')

            # Actualiza la imagen visible en pantalla segun la animacion
        frame = self.animator.update(dt)
        if frame:
            self.image = frame
            
    def draw(self, surface, camera_offset=(0, 0)):
        if not self.alive:
            return
        if self.invuln_time > 0 and int(self.invuln_time * 10) % 2 == 0:
            return   
        super().draw(surface, camera_offset)