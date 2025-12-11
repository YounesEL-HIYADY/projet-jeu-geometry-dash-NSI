import pygame

class Player(pygame.sprite.Sprite):
    """Cube du joueur avec rotation GD-authentique et double saut."""
    
    GRAVITY_PER_SEC = 2500.0
    JUMP_VELOCITY = -800.0
    ROTATION_SPEED_PER_SEC = 720.0
    
    COYOTE_FRAMES = 5
    JUMP_BUFFER_FRAMES = 5

    def __init__(self, world_x, y, image):
        super().__init__()

        # IMAGE & DIMENSIONS
        scale = 0.55
        w = int(image.get_width() * scale)
        h = int(image.get_height() * scale)
        
        self.image_originale = pygame.transform.scale(image, (w, h))
        self.image = self.image_originale.copy()

        # PHYSIQUE & POSITION
        self.pos_y_float = float(y)
        self.hitbox = pygame.Rect(world_x, y, w, h)
        
        # ÉTAT
        self.vel_y = 0.0
        self.is_jumping = False
        self.s_was_on_ground = True
        
        # COYOTE & BUFFER
        self.coyote_timer = 0
        self.jump_buffered = False
        self.jump_buffer_timer = 0
        
        # ROTATION
        self.angle = 0.0
        self.remaining_rotation = 0.0
        
        # DOUBLE SAUT
        self.can_double_jump = False
        self.has_used_double_jump = False

    def _trigger_jump(self):
        """Déclenche le saut et la rotation"""
        self.vel_y = self.JUMP_VELOCITY
        self.remaining_rotation = 180.0
        self.coyote_timer = 0
        self.jump_buffered = False
        self.jump_buffer_timer = 0

    def jump(self):
        """Tente de sauter avec buffer et double saut"""
        # Saut normal (sol ou coyote time)
        if (not self.is_jumping or self.coyote_timer > 0) and self.s_was_on_ground:
            self._trigger_jump()
            return True
        
        # Double saut dans les airs
        elif self.is_jumping and self.can_double_jump and not self.has_used_double_jump:
            self._trigger_jump()
            self.has_used_double_jump = True
            self.can_double_jump = False  # Consume le double saut
            return True
        
        # Buffer si on appuie trop tôt
        elif self.is_jumping and not self.s_was_on_ground:
            self.jump_buffered = True
            self.jump_buffer_timer = self.JUMP_BUFFER_FRAMES
        
        return False

    def update(self, platforms, dt, camera):
        """Mise à jour physique et rotation"""
        
        # Déplacement horizontal (suivi caméra)
        self.hitbox.x += camera.scroll_speed * dt
        
        # Gravité
        self.vel_y += self.GRAVITY_PER_SEC * dt
        self.pos_y_float += self.vel_y * dt
        self.hitbox.y = int(self.pos_y_float)

        # Coyote time
        if self.is_jumping:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        # ROTATION
        if self.remaining_rotation > 0:
            rotation_step = self.ROTATION_SPEED_PER_SEC * dt
            
            if rotation_step >= self.remaining_rotation:
                self.angle -= self.remaining_rotation
                self.remaining_rotation = 0.0
            else:
                self.angle -= rotation_step
                self.remaining_rotation -= rotation_step

        # COLLISIONS VERTICALES ET LATÉRALES
        on_ground = False
        temp_y = self.hitbox.y

        for platform in platforms:
            if self.hitbox.colliderect(platform.rect):
                # Collision par le haut (atterrissage)
                if self.vel_y > 0 and temp_y < platform.rect.top:
                    self.hitbox.bottom = platform.rect.top
                    self.vel_y = 0.0
                    self.pos_y_float = float(self.hitbox.y)
                    on_ground = True
                
                # Collision par le bas (tête en dessous)
                elif self.vel_y < 0 and temp_y > platform.rect.top:
                    self.hitbox.top = platform.rect.bottom
                    self.vel_y = 0.0
                    self.pos_y_float = float(self.hitbox.y)
                
                # Collision latérale (mort)
                elif self.hitbox.centerx < platform.rect.centerx:  # À gauche
                    self.hitbox.right = platform.rect.left
                    return True  # Mort
                elif self.hitbox.centerx > platform.rect.centerx:  # À droite
                    self.hitbox.left = platform.rect.right
                    return True  # Mort

        # Snap rotation à l'atterrissage
        if not self.s_was_on_ground and on_ground and self.remaining_rotation > 0:
            self.angle = round(self.angle / 180.0) * 180.0
            self.remaining_rotation = 0.0

        # Buffer jump
        if self.jump_buffered and on_ground and not self.is_jumping:
            self._trigger_jump()

        # Mise à jour état
        self.s_was_on_ground = on_ground

        # États jumping/coyote
        if on_ground:
            self.is_jumping = False
            self.coyote_timer = 0
            self.has_used_double_jump = False  # Reset double jump au sol
            self.can_double_jump = False
        
        else:
            if self.vel_y < 0 and not self.is_jumping:
                self.coyote_timer = self.COYOTE_FRAMES
            self.is_jumping = True
        
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.jump_buffer_timer == 0:
                self.jump_buffered = False

        return False  # Pas de mort

    def collect_orb(self):
        """Active le double saut"""
        self.can_double_jump = True
        self.has_used_double_jump = False

    def draw(self, screen, camera, is_invincible=False):
        """Dessine le joueur avec rotation et clignotement"""
        rotated_image = pygame.transform.rotate(self.image_originale, self.angle)
        visual_rect = rotated_image.get_rect(center=self.hitbox.center)
        
        # Indicateur double saut disponible
        if self.can_double_jump and not self.has_used_double_jump:
            aura = pygame.Surface((self.hitbox.w + 20, self.hitbox.h + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (0, 200, 255, 100), aura.get_rect())
            screen.blit(aura, camera.apply(aura.get_rect(center=self.hitbox.center)))
        
        # Clignotement invincibilité
        if is_invincible:
            alpha = int(155 + 100 * abs(pygame.time.get_ticks() % 200 - 100) / 100)
            rotated_image.set_alpha(alpha)
        else:
            rotated_image.set_alpha(255)
        
        screen.blit(rotated_image, camera.apply(visual_rect))