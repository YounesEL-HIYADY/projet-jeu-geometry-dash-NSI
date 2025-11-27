import pygame
import random

class Platform(pygame.sprite.Sprite):
    """Plateforme avec position monde fixe"""
    
    def __init__(self, world_x, y, tile_size):
        super().__init__()
        
        self.world_x = world_x
        
        block_img = pygame.image.load("assets/block.png").convert_alpha()
        block_img = pygame.transform.scale(block_img, (tile_size, tile_size))
        
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.image.blit(block_img, (0, 0))
        self.rect = self.image.get_rect(topleft=(world_x, y))

class Spike(pygame.sprite.Sprite):
    """Pic avec hitbox équitable"""
    
    def __init__(self, world_x, ground_y):
        super().__init__()
        
        self.world_x = world_x
        
        image = pygame.image.load("assets/spike.png").convert_alpha()
        scale = 0.7 * (75 / image.get_width())
        new_width = int(image.get_width() * scale)
        new_height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (new_width, new_height))
        
        self.rect = self.image.get_rect()
        self.rect.centerx = world_x + 75 // 2
        self.rect.bottom = ground_y
        
        self.hitbox = pygame.Rect(0, 0, new_width * 0.5, new_height)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
    
    def draw(self, screen, camera):
        """Dessine avec l'offset caméra"""
        screen.blit(self.image, camera.apply(self.rect))

# ============================
# ✅ PARTICULES : Classe pour l'effet de poussière à l'atterrissage
class DustParticle(pygame.sprite.Sprite):
    """Particule de poussière qui apparaît quand le joueur atterrit"""
    
    def __init__(self, x, y):
        super().__init__()
        
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        
        # Couleur blanc avec alpha géré directement
        self.base_color = (255, 255, 255)
        self.pos = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.pos)
        
        # Vitesse aléatoire
        self.vel = pygame.Vector2(
            random.uniform(-80, 80),
            random.uniform(-60, -20)
        )
        
        self.gravity = 400.0
        self.life = 0.3
        self.max_life = 0.3
        self.size = 5.0
        
    def update(self, dt):
        """Met à jour la particule"""
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        self.life -= dt
        progress = max(0, self.life / self.max_life)
        
        self.current_size = int(self.size * progress)
        
        # ✅ CORRECTION : Recréer l'image avec alpha directement
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        
        if self.current_size > 0:
            alpha = int(255 * progress)
            color = (*self.base_color, alpha)
            pygame.draw.circle(self.image, color, (4, 4), self.current_size)
    
    def draw(self, screen, camera):
        """Dessine la particule avec offset caméra"""
        screen.blit(self.image, camera.apply(self.rect))
        
    def is_alive(self):
        """Retourne True si la particule est encore visible"""
        return self.life > 0
# ============================