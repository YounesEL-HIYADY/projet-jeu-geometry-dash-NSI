import pygame
import random
import math

class Platform(pygame.sprite.Sprite):
    """Plateforme avec texture de thème"""
    
    def __init__(self, world_x, y, tile_size, block_image):
        super().__init__()
        
        self.world_x = world_x
        
        # Copie de l'image pour éviter modifications
        self.image = block_image.copy()
        self.rect = self.image.get_rect(topleft=(world_x, y))

class Spike(pygame.sprite.Sprite):
    """Pic avec texture de thème et hitbox équitable"""
    
    def __init__(self, world_x, ground_y, tile_size, spike_image):
        super().__init__()
        
        self.world_x = world_x
        
        # Copie de l'image
        self.image = spike_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = world_x + tile_size // 2
        self.rect.bottom = ground_y
        
        # Hitbox plus petite pour gameplay équitable
        hitbox_width = int(self.rect.width * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, self.rect.height)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
    
    def draw(self, screen, camera):
        """Dessine avec offset caméra"""
        screen.blit(self.image, camera.apply(self.rect))

# ============================
# NOUVEAU : Orb pour double saut
class Orb(pygame.sprite.Sprite):
    """Orb qui permet un double saut"""
    def __init__(self, world_x, y, tile_size, orb_image):
        super().__init__()
        
        self.world_x = world_x
        self.tile_size = tile_size
        
        # Image redimensionnée
        orb_size = int(tile_size * 0.6)
        self.image = pygame.transform.scale(orb_image, (orb_size, orb_size))
        
        # Position
        self.rect = self.image.get_rect()
        self.rect.centerx = world_x + tile_size // 2
        self.rect.centery = y + tile_size // 2
        
        # Hitbox circulaire
        hitbox_size = int(tile_size * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.hitbox.center = self.rect.center
        
        # Animation
        self.base_y = self.rect.y
        self.float_offset = 0
        self.collected = False
    
    def update(self, dt):
        """Animation flottante"""
        if not self.collected:
            self.float_offset += dt * 4
            self.rect.y = self.base_y + math.sin(self.float_offset) * 5
    
    def draw(self, screen, camera):
        """Dessine l'orb avec effet glow"""
        if self.collected:
            return
        
        # Glow effect
        glow = pygame.Surface((self.rect.w + 20, self.rect.h + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 100, 60), 
                          (glow.get_width()//2, glow.get_height()//2), 
                          glow.get_width()//2)
        screen.blit(glow, camera.apply(glow.get_rect(center=self.rect.center)))
        
        # Orb
        screen.blit(self.image, camera.apply(self.rect))
    
    def collect(self):
        """Marque comme collecté"""
        self.collected = True

# ============================
# NOUVEAU : Zone de fin
class FinishFlag(pygame.sprite.Sprite):
    """Zone invisible de fin de niveau"""
    def __init__(self, world_x, y, tile_size):
        super().__init__()
        
        self.world_x = world_x
        
        # Zone de collision (invisible)
        self.rect = pygame.Rect(world_x, y, tile_size, tile_size * 3)
    
    def draw(self, screen, camera):
        """Invisible par défaut - tu peux décommenter pour debug"""
        # debug_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        # debug_surf.fill((0, 255, 0, 50))
        # screen.blit(debug_surf, camera.apply(self.rect))
        pass

# ============================
# PARTICULES : Effet poussière
class DustParticle(pygame.sprite.Sprite):
    """Particule de poussière 16x16 pour éviter overflow"""
    
    def __init__(self, x, y):
        super().__init__()
        
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.pos = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(center=self.pos)
        
        # Propriétés
        self.base_color = (255, 255, 255)
        self.vel = pygame.Vector2(
            random.uniform(-100, 100),
            random.uniform(-80, -30)
        )
        self.gravity = 500.0
        self.life = 0.4
        self.max_life = 0.4
        self.size = 6.0
        
    def update(self, dt):
        """Met à jour la particule"""
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        self.life -= dt
        progress = max(0, self.life / self.max_life)
        
        # Recréation image
        self.image.fill((0, 0, 0, 0))
        
        current_size = int(self.size * progress)
        if current_size > 0:
            alpha = int(255 * progress)
            color = (*self.base_color, alpha)
            pygame.draw.circle(self.image, color, (8, 8), current_size)
    
    def draw(self, screen, camera):
        """Dessine particule avec offset caméra"""
        screen.blit(self.image, camera.apply(self.rect))
        
    def is_alive(self):
        return self.life > 0
# ============================