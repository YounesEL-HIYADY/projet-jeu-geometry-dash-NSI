import pygame

class Player(pygame.sprite.Sprite):
    GRAVITY_PER_SEC = 2500.0
    JUMP_VELOCITY = -800.0
    ROTATION_SPEED_PER_SEC = 720.0
    COYOTE_FRAMES = 5
    JUMP_BUFFER_FRAMES = 5

    def __init__(self, world_x, y, image):
        super().__init__()
        scale = 0.55
        w = int(image.get_width() * scale)
        h = int(image.get_height() * scale)
        self.image_originale = pygame.transform.scale(image, (w, h))
        self.image = self.image_originale.copy()
        self.pos_y_float = float(y)
        self.hitbox = pygame.Rect(world_x, y, w, h)
        self.vel_y = 0.0
        self.is_jumping = False
        self.s_was_on_ground = True
        self.coyote_timer = 0
        self.jump_buffered = False
        self.jump_buffer_timer = 0
        self.angle = 0.0
        self.remaining_rotation = 0.0
        self.can_double_jump = False
        self.has_used_double_jump = False

    def _trigger_jump(self):
        self.vel_y = self.JUMP_VELOCITY
        self.remaining_rotation = 180.0
        self.coyote_timer = 0
        self.jump_buffered = False
        self.jump_buffer_timer = 0

    def jump(self):
        if (not self.is_jumping or self.coyote_timer > 0) and self.s_was_on_ground:
            self._trigger_jump()
            return True
        elif self.is_jumping and self.can_double_jump and not self.has_used_double_jump:
            self._trigger_jump()
            self.has_used_double_jump = True
            self.can_double_jump = False
            return True
        elif self.is_jumping and not self.s_was_on_ground:
            self.jump_buffered = True
            self.jump_buffer_timer = self.JUMP_BUFFER_FRAMES
        return False

    def update(self, platforms, dt, camera):
        self.hitbox.x += camera.scroll_speed * dt
        self.vel_y += self.GRAVITY_PER_SEC * dt
        self.pos_y_float += self.vel_y * dt
        self.hitbox.y = int(self.pos_y_float)

        if self.is_jumping:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        if self.remaining_rotation > 0:
            rotation_step = self.ROTATION_SPEED_PER_SEC * dt
            if rotation_step >= self.remaining_rotation:
                self.angle -= self.remaining_rotation
                self.remaining_rotation = 0.0
            else:
                self.angle -= rotation_step
                self.remaining_rotation -= rotation_step

        on_ground = False
        temp_y = self.hitbox.y

        for platform in platforms:
            if self.hitbox.colliderect(platform.rect):
                if self.vel_y > 0 and temp_y < platform.rect.top:
                    self.hitbox.bottom = platform.rect.top
                    self.vel_y = 0.0
                    self.pos_y_float = float(self.hitbox.y)
                    on_ground = True
                elif self.vel_y < 0 and temp_y > platform.rect.top:
                    self.hitbox.top = platform.rect.bottom
                    self.vel_y = 0.0
                    self.pos_y_float = float(self.hitbox.y)
                elif self.hitbox.centerx < platform.rect.centerx:
                    self.hitbox.right = platform.rect.left
                    return True
                elif self.hitbox.centerx > platform.rect.centerx:
                    self.hitbox.left = platform.rect.right
                    return True

        if not self.s_was_on_ground and on_ground and self.remaining_rotation > 0:
            self.angle = round(self.angle / 180.0) * 180.0
            self.remaining_rotation = 0.0

        if self.jump_buffered and on_ground and not self.is_jumping:
            self._trigger_jump()

        self.s_was_on_ground = on_ground

        if on_ground:
            self.is_jumping = False
            self.coyote_timer = 0
            self.has_used_double_jump = False
            self.can_double_jump = False
        else:
            if self.vel_y < 0 and not self.is_jumping:
                self.coyote_timer = self.COYOTE_FRAMES
            self.is_jumping = True
        
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1
            if self.jump_buffer_timer == 0:
                self.jump_buffered = False

        return False

    def collect_orb(self):
        self.can_double_jump = True
        self.has_used_double_jump = False

    def draw(self, screen, camera, is_invincible=False):
        rotated_image = pygame.transform.rotate(self.image_originale, self.angle)
        visual_rect = rotated_image.get_rect(center=self.hitbox.center)
        
        if self.can_double_jump and not self.has_used_double_jump:
            aura = pygame.Surface((self.hitbox.w + 20, self.hitbox.h + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (0, 200, 255, 100), aura.get_rect())
            screen.blit(aura, camera.apply(aura.get_rect(center=self.hitbox.center)))
        
        if is_invincible:
            alpha = int(155 + 100 * abs(pygame.time.get_ticks() % 200 - 100) / 100)
            rotated_image.set_alpha(alpha)
        else:
            rotated_image.set_alpha(255)
        
        screen.blit(rotated_image, camera.apply(visual_rect))