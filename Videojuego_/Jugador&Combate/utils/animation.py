import gygame

class AnimationPlayer:
    def __init__(self):
        self.animations = {}
        self.current_state = "idle"
        self.frame_index = 0
        self.animation_speed = 8
        
    def add_animation(self, name, frames):
        self.animations[name] = frames
    
    def set_state(self, new_state):
        if new_state in self.animations and self.current_state != new_state:
            self.current_state = new_state
            self.frame_index = 0
            
    def update(self, dt):
        frames = self.animations.get(self.current_state, [])
        if not frames:
            return None
        
        self.frame_index += self.animations_speed * dt
        if self.frame_index >= len(frames):
            self.frame_index = 0 
            
        return frames[int(self.frame_index)]
