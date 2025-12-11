import pygame
import random
import math
from config import WIDTH, HEIGHT

# Couleurs modernes
COLORS = {
    "bg": (10, 10, 30),
    "primary": (0, 220, 255),
    "secondary": (150, 0, 255),
    "accent": (255, 100, 0),
    "white": (255, 255, 255),
    "gray": (100, 100, 120),
    "dark": (20, 20, 40),
    "glow": (255, 255, 100)
}

# Cache
GRADIENT_CACHE = {}
PARTICLE_SYSTEM = None

class Particle:
    """Particule pour l'effet de fond animé"""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(-20, 20)
        self.size = random.randint(2, 6)
        self.life = 1.0
        self.max_life = random.uniform(1.5, 3.0)
        self.color = random.choice([COLORS["primary"], COLORS["secondary"], COLORS["accent"]])
    
    def update(self, dt):
        self.x += self.vx * dt * 30
        self.y += self.vy * dt * 30
        self.life -= dt
        
        # Wrap screen
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(surf, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    """Système de particules de fond"""
    def __init__(self, count=30):
        self.particles = [Particle() for _ in range(count)]
    
    def update(self, dt):
        for p in self.particles:
            p.update(dt)
            if p.life <= 0:
                p.__init__()
    
    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class Button:
    """Bouton avec animations premium"""
    def __init__(self, x, y, w, h, text, icon=None, primary=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon = icon
        self.is_hovered = False
        self.hover_progress = 0.0
        self.primary = primary
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        
        self.gradient = self._create_gradient(w, h, primary)
    
    def _create_gradient(self, w, h, primary):
        """Crée un gradient dynamique"""
        key = f"grad_{w}_{h}_{primary}"
        if key in GRADIENT_CACHE:
            return GRADIENT_CACHE[key]
        
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color1 = COLORS["primary"] if primary else COLORS["secondary"]
        color2 = COLORS["dark"]
        
        for y in range(h):
            ratio = y / h
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
        
        rounded = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(rounded, (255, 255, 255), (0, 0, w, h), border_radius=15)
        surf.blit(rounded, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        GRADIENT_CACHE[key] = surf
        return surf
    
    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        target = 1.0 if self.is_hovered else 0.0
        speed = 0.15
        self.hover_progress += (target - self.hover_progress) * speed
        
        return self.is_hovered and not was_hovered
    
    def draw(self, screen):
        # Position avec hover offset
        offset_y = -5 * self.hover_progress
        draw_rect = self.rect.copy()
        draw_rect.y += int(offset_y)
        
        # Ombre
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=15)
        screen.blit(shadow, draw_rect.move(0, 5))
        
        # Bouton gradient
        screen.blit(self.gradient, draw_rect)
        
        # Glow effect
        if self.hover_progress > 0.1:
            glow = pygame.Surface((draw_rect.w + 10, draw_rect.h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*COLORS["glow"], int(50 * self.hover_progress)), 
                           glow.get_rect(), border_radius=18)
            screen.blit(glow, glow.get_rect(center=draw_rect.center))
        
        # Texte
        text_surf = self.font.render(self.text, True, COLORS["white"])
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_surf, text_rect)
        
        # Icône
        if self.icon:
            icon_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            if self.icon == "play":
                pygame.draw.polygon(icon_surf, COLORS["white"], [(5, 5), (5, 25), (25, 15)])
            elif self.icon == "back":
                pygame.draw.polygon(icon_surf, COLORS["white"], [(25, 5), (5, 15), (25, 25)])
            screen.blit(icon_surf, icon_surf.get_rect(center=(draw_rect.left + 40, draw_rect.centery)))

class MenuManager:
    """Gère tous les menus avec transitions"""
    def __init__(self, screen):
        self.screen = screen
        self.particle_system = ParticleSystem()
        self.fade_alpha = 0
        self.fade_target = 0
        
        # Boutons du menu principal
        self.main_buttons = {
            "play": Button(WIDTH//2 - 125, 250, 250, 60, "PLAY", "play"),
            "quit": Button(WIDTH//2 - 125, 340, 250, 60, "QUIT", "back", primary=False)
        }
        
        # Boutons pause
        self.pause_buttons = {
            "resume": Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "RESUME", "play"),
            "menu": Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "MAIN MENU", "back", primary=False)
        }
    
    def update(self, mouse_pos, dt, game_state):
        """Met à jour tous les éléments du menu"""
        self.particle_system.update(dt)
        
        # Fade transition
        if self.fade_alpha != self.fade_target:
            diff = self.fade_target - self.fade_alpha
            self.fade_alpha += diff * 0.1
        
        # Update boutons selon l'état
        if game_state == "MENU":
            for btn in self.main_buttons.values():
                btn.update(mouse_pos)
        elif game_state == "PAUSE":
            for btn in self.pause_buttons.values():
                btn.update(mouse_pos)
        
        return self.fade_alpha
    
    def draw_main(self, screen, game_state):
        """Dessine le menu principal premium"""
        if game_state != "MENU":
            return {}
        
        # Fond animé
        screen.fill(COLORS["bg"])
        self.particle_system.draw(screen)
        
        # Titre avec glow
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        title_surf = title_font.render("GEOMETRY DASH", True, COLORS["primary"])
        title_rect = title_surf.get_rect(center=(WIDTH//2, 120))
        
        glow = pygame.Surface((title_rect.w + 20, title_rect.h + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*COLORS["glow"], 30), glow.get_rect(), border_radius=10)
        screen.blit(glow, glow.get_rect(center=title_rect.center))
        
        screen.blit(title_surf, title_rect)
        
        # Ligne décorative
        line_y = 180
        for x in range(0, WIDTH, 40):
            pygame.draw.rect(screen, COLORS["primary"], (x, line_y, 20, 3))
            pygame.draw.rect(screen, COLORS["secondary"], (x + 20, line_y, 20, 3))
        
        # Boutons
        for btn in self.main_buttons.values():
            btn.draw(screen)
        
        # Footer
        footer_font = pygame.font.SysFont("Arial", 16)
        footer = footer_font.render("PREMIUM EDITION - Version 1.0", True, COLORS["gray"])
        screen.blit(footer, footer.get_rect(center=(WIDTH//2, HEIGHT - 30)))
        
        # Fade overlay
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(fade, (0, 0))
        
        return {key: btn.rect for key, btn in self.main_buttons.items()}
    
    def draw_pause(self, screen, game_state):
        """Dessine le menu pause premium"""
        if game_state != "PAUSE":
            return {}
        
        # Overlay semi-transparent
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*COLORS["bg"], 200))
        screen.blit(overlay, (0, 0))
        
        # Panneau central
        panel = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 240)
        pygame.draw.rect(screen, COLORS["dark"], panel, border_radius=20)
        
        # Bordure glow
        border = pygame.Surface((panel.w + 6, panel.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(border, (*COLORS["primary"], 100), border.get_rect(), border_radius=23)
        screen.blit(border, border.get_rect(center=panel.center).move(-3, -3))
        
        # Titre
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title = title_font.render("PAUSED", True, COLORS["primary"])
        screen.blit(title, title.get_rect(center=(WIDTH//2, panel.top + 40)))
        
        # Boutons
        for btn in self.pause_buttons.values():
            btn.draw(screen)
        
        # Fade
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(fade, (0, 0))
        
        return {key: btn.rect for key, btn in self.pause_buttons.items()}
    
    def draw_level_select(self, screen, mouse_pos, available_levels, game_state):
        """Dessine la sélection de niveau premium"""
        if game_state != "LEVEL_SELECT":
            return {"back": pygame.Rect(0,0,0,0), "levels": []}
        
        screen.fill(COLORS["bg"])
        self.particle_system.draw(screen)
        
        # Titre
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        title = title_font.render("SELECT LEVEL", True, COLORS["primary"])
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
        
        # Bouton retour
        back_btn = Button(20, 20, 120, 40, "← BACK", "back", primary=False)
        back_btn.update(mouse_pos)
        back_btn.draw(screen)
        
        # Grille des niveaux
        level_buttons = []
        level_width, level_height = 180, 60
        start_x = WIDTH//2 - (level_width * 2 + 40) // 2
        start_y = 150
        
        for i, level_name in enumerate(available_levels):
            row = i // 3
            col = i % 3
            x = start_x + col * (level_width + 20)
            y = start_y + row * (level_height + 20)
            
            btn = Button(x, y, level_width, level_height, 
                        f"Level {i+1}", primary=(i % 2 == 0))
            btn.level_name = level_name
            hovered = btn.update(mouse_pos)
            btn.draw(screen)
            level_buttons.append((btn.rect, level_name))
        
        # Message si pas de niveaux
        if not available_levels:
            msg_font = pygame.font.SysFont("Arial", 24)
            msg1 = msg_font.render("No levels available", True, COLORS["gray"])
            msg2 = msg_font.render("Create levels in the 'levels' folder", True, COLORS["gray"])
            screen.blit(msg1, msg1.get_rect(center=(WIDTH//2, HEIGHT//2)))
            screen.blit(msg2, msg2.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
        
        # Fade
        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(fade, (0, 0))
        
        return {"back": back_btn.rect, "levels": level_buttons}

# Global menu manager
MENU_MANAGER = None

def get_menu_manager(screen):
    global MENU_MANAGER
    if MENU_MANAGER is None:
        MENU_MANAGER = MenuManager(screen)
    return MENU_MANAGER

# Fonctions de compatibilité
def draw_menu(screen, mouse_pos, game_state):
    manager = get_menu_manager(screen)
    manager.update(mouse_pos, 0.016, game_state)
    return manager.draw_main(screen, game_state)

def draw_pause_menu(screen, mouse_pos, game_state):
    manager = get_menu_manager(screen)
    manager.update(mouse_pos, 0.016, game_state)
    return manager.draw_pause(screen, game_state)

def draw_level_select(screen, mouse_pos, available_levels, game_state):
    manager = get_menu_manager(screen)
    manager.update(mouse_pos, 0.016, game_state)
    return manager.draw_level_select(screen, mouse_pos, available_levels, game_state)