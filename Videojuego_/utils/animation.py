
class AnimationPlayer:
    def __init__(self):
        self.animations = {}        #Una caja donde guardamos listas de fotos
        self.current_state = "idle" #La animacion actual empieza en "quieto" (idle)
        self.frame_index = 0        #El numero de la foto que estamos mostrando
        self.animation_speed = 8    #Que tan rapido cambian las fotos (8 por segundo)

    def add_animation(self, name, frames): 
        #Guarda un grupo de fotos con un nombre (ej: "caminar")
        self.animations[name] = frames

    def set_state(self, new_state):
        #Cambia de animacion (ej: pasar de quieto a caminar)
        if new_state in self.animations and self.current_state != new_state:
            self.current_state = new_state
            self.frame_index = 0 # Vuelve a la primera foto de la animacion

    def update(self, dt):
        frames = self.animations.get(self.current_state, [])
        if not frames:
            return None
        
        # Avanza el tiempo para pasar a la siguiente foto
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(frames):
            self.frame_index = 0 #Si llega al final de las fotos, vuelve a empezar

        # Devuelve la foto exacta que se debe mostrar ahora mismo
        return frames[int(self.frame_index)]
