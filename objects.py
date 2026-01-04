import pygame
import math  # 🛠️ AJOUTÉ - nécessaire pour sin()

class Platform(pygame.sprite.Sprite):
    def __init__(self, world_x, y, tile_size, block_image):
        super().__init__()
        self.world_x = world_x
        self.image = block_image.copy()
        self.rect = self.image.get_rect(topleft=(world_x, y))

class Spike(pygame.sprite.Sprite):
    def __init__(self, world_x, ground_y, tile_size, spike_image):
        super().__init__()
        self.world_x = world_x
        self.image = spike_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = world_x + tile_size // 2
        self.rect.bottom = ground_y
        
        hitbox_width = int(self.rect.width * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_width, self.rect.height)
        self.hitbox.centerx = self.rect.centerx
        self.hitbox.bottom = self.rect.bottom
    
    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))

class Orb(pygame.sprite.Sprite):
    def __init__(self, world_x, y, tile_size, orb_image):
        super().__init__()
        self.world_x = world_x
        self.tile_size = tile_size
        orb_size = int(tile_size * 0.6)
        self.image = pygame.transform.scale(orb_image, (orb_size, orb_size))
        self.rect = self.image.get_rect()
        self.rect.centerx = world_x + tile_size // 2
        self.rect.centery = y + tile_size // 2
        
        hitbox_size = int(tile_size * 0.5)
        self.hitbox = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.hitbox.center = self.rect.center
        
        self.base_y = self.rect.y
        self.float_offset = 0
        self.collected = False
    
    def update(self, dt):
        if not self.collected:
            self.float_offset += dt * 4
            self.rect.y = self.base_y + math.sin(self.float_offset) * 5  # 🛠️ CORRIGÉ
    
    def draw(self, screen, camera):
        if self.collected:
            return
        
        glow = pygame.Surface((self.rect.w + 20, self.rect.h + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 100, 60), 
                          (glow.get_width()//2, glow.get_height()//2), 
                          glow.get_width()//2)
        screen.blit(glow, camera.apply(glow.get_rect(center=self.rect.center)))
        screen.blit(self.image, camera.apply(self.rect))
    
    def collect(self):
        self.collected = True

class FinishFlag(pygame.sprite.Sprite):
    def __init__(self, world_x, y, tile_size):
        super().__init__()
        self.world_x = world_x
        self.rect = pygame.Rect(world_x, y, tile_size, tile_size * 3)
    
    def draw(self, screen, camera):
        pass