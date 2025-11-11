import pygame

# Taille d'une tuile (sera cohérent avec level.json)
TILE_SIZE = 75

class Platform(pygame.sprite.Sprite):
    """Une plateforme faite de blocs répétitifs"""
    def __init__(self, x, y, width, height):
        super().__init__()
        block_img = pygame.image.load("assets/block.png").convert_alpha()
        block_img = pygame.transform.scale(block_img, (TILE_SIZE, TILE_SIZE))

        # Surface vide où on colle des tuiles de bloc
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(0, width, TILE_SIZE):
            self.image.blit(block_img, (i, 0))

        self.rect = self.image.get_rect(topleft=(x, y))

class Spike(pygame.sprite.Sprite):
    """Un pic dangereux (tue le joueur en cas de collision)"""
    def __init__(self, x, ground_y):
        super().__init__()
        image = pygame.image.load("assets/spike.png").convert_alpha()

        # Redimensionner les pics pour correspondre à la taille des tuiles
        scale = 0.7 * (TILE_SIZE / image.get_width())
        new_width = int(image.get_width() * scale)
        new_height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (new_width, new_height))

        # Positionner le pic
        self.rect = self.image.get_rect()
        self.rect.x = x + (TILE_SIZE - new_width) // 2
        self.rect.bottom = ground_y
