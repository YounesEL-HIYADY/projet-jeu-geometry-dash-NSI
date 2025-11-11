import pygame

class Player(pygame.sprite.Sprite):
    """Le cube du joueur : saute, subit la gravité, et rebondit sur les plateformes."""
    def __init__(self, x, y):
        super().__init__()

        # Charger et redimensionner l'image du cube
        image = pygame.image.load("assets/cube.png").convert_alpha()
        scale = 0.55
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (width, height))

        # Rectangle de collision
        self.rect = self.image.get_rect(topleft=(x, y))

        # Physique
        self.vel_y = 0
        self.is_jumping = False
        self.gravity = 0.8
        self.jump_force = -15

    def jump(self):
        """Permet au joueur de sauter (si au sol uniquement)"""
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True

    def update(self, platforms):
        """Applique la gravité et gère les collisions avec le sol/plateformes"""
        # Gravité
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Gestion des collisions
        self.is_jumping = True
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.is_jumping = False
