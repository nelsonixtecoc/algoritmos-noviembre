import pygame

def apply_damage(attacker, target, amount, knockback_force=0):
    if hasattr(target, 'is_invulnerable') and target.is_invulnerable:
        return False
    
    defense = getattr(target, 'defense', 0)
    final_damage = max(1, amount - defense)
    target.hp -= final_damage
    
    if knockback_force > 0 and hasattr(target, 'knockback_vector'):
        direction = target.pos - attacker.pos
        if direction.length() > 0:
            target.knockback_vector = direction.normalize() * knockback_force
        
    if hasattr(target, 'trigger_invulnerability'):
        target.trigger_invulnerability()
        
    return True

def check_sword_hit(player,targets):
    if not player.is_attacking or player.attack_hitbox is None:
        return[]
    
    hits = []
    for target in targets:
        if target != player and target.alive:
            if player.attack_hitbox.colliderect(target.rect):
                if apply_damage(player, target, player.attack_damege, player.knockback_force):
                    hits.append(target)
                    
    return hits
