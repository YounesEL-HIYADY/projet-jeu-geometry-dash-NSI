import pygame

class Player(pygame.sprite.Sprite):
    """Cube du joueur avec rotation 180° parfaite et orientation persistante."""
    def __init__(self, x, y):
        super().__init__()

        # ----- IMAGE -----
        image = pygame.image.load("assets/cube.png").convert_alpha()
        scale = 0.55
        w = int(image.get_width() * scale)
        h = int(image.get_height() * scale)
        self.image_originale = pygame.transform.scale(image, (w, h))
        self.image = self.image_originale.copy()

        self.rect = self.image.get_rect(topleft=(x, y))

        # ----- PHYSIQUE -----
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_force = -15
        self.is_jumping = False

        # ----- ROTATION -----
        self.angle = 0                   # orientation actuelle (-180 / 0 / +180 / +360 etc.)
        self.target_angle = 0            # angle à atteindre pendant la rotation
        self.rotation_speed = 6
        self.rotation_in_progress = False

    def jump(self):
        """Déclenche le saut si le joueur est au sol."""
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True

            # Nouvelle rotation = angle actuel + 180
            self.target_angle = self.angle - 180
            self.rotation_in_progress = True

    def update(self, platforms):
        """Gestion physique + rotation + collisions."""

        # ----- GRAVITÉ -----
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # ----- ROTATION -----
        if self.rotation_in_progress:
            # Avance vers l'objectif
            self.angle -= self.rotation_speed

            # Si on dépasse l'angle cible → on fixe proprement
            if (self.angle <= self.target_angle):
                self.angle = self.target_angle
                self.rotation_in_progress = False

        # ----- COLLISIONS -----
        on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                on_ground = True

        self.is_jumping = not on_ground

        # ----- ROTATION VISUELLE -----
        rotated_image = pygame.transform.rotate(self.image_originale, self.angle)
        center = self.rect.center
        self.image = rotated_image
        self.rect = self.image.get_rect(center=center)
