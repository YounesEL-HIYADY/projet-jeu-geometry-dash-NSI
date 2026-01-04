import pygame
from config import WIDTH, HEIGHT, COLOR_WHITE, COLOR_BLACK
import os

# 🛠️ FONCTION ESSENTIELLE - DOIT ÊTRE DÉFINIE EN PREMIER
def get_pixel_font(size):
    """
    Charge une police pixel ou retourne une police système de secours.
    """
    try:
        # Essayer la police pixel personnalisée
        font_path = "assets/fonts/pixel.ttf"
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            # Police système moderne
            return pygame.font.SysFont("Consolas", size, bold=True)
    except Exception as e:
        print(f"⚠️ Erreur chargement police: {e}")
        # Ultime recours
        return pygame.font.SysFont("Arial", size, bold=True)

# 🎨 CLASSE BOUTON MODERNE
class MinimalButton:
    def __init__(self, x, y, w, h, text, callback=None, bg_color=(0,0,0,180), text_color=COLOR_WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.bg_color = bg_color
        self.text_color = text_color
        
        # Utiliser la fonction globale
        self.font = get_pixel_font(24)
        
        self.text_surf = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered
    
    def draw(self, screen):
        # Surface temporaire pour la transparence
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Couleur de fond avec transparence
        bg_alpha = self.bg_color[3] if len(self.bg_color) == 4 else 255
        current_alpha = min(255, bg_alpha + 50) if self.hovered else bg_alpha
        
        pygame.draw.rect(button_surface, (*self.bg_color[:3], current_alpha), button_surface.get_rect())
        
        # Bordure subtile
        border_alpha = 150 if self.hovered else 100
        border_color = (255, 255, 255, border_alpha)
        pygame.draw.rect(button_surface, border_color, button_surface.get_rect(), width=2)
        
        # Texte
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        button_surface.blit(text_surface, text_rect)
        
        # Dessiner sur l'écran principal
        screen.blit(button_surface, self.rect)

# 🎨 SELECTEUR DE NIVEAU
class LevelSelector:
    def __init__(self, levels_list, screen):
        self.levels = levels_list
        self.screen = screen
        self.current_index = 0
        self.target_x = 0
        self.current_x = 0
        self.animation_speed = 15
        
        btn_y = HEIGHT // 2
        # Boutons noirs transparents
        self.btn_prev = MinimalButton(50, btn_y, 60, 60, "<")
        self.btn_next = MinimalButton(WIDTH - 110, btn_y, 60, 60, ">")
        self.btn_play = MinimalButton(WIDTH//2 - 100, HEIGHT - 150, 200, 60, "PLAY")
        
        self.title_font = get_pixel_font(64)
        
    def navigate(self, direction):
        new_index = self.current_index + direction
        if 0 <= new_index < len(self.levels):
            self.current_index = new_index
            self.target_x = -self.current_index * WIDTH
    
    def update(self, mouse_pos, dt):
        diff = self.target_x - self.current_x
        self.current_x += diff * self.animation_speed * dt
        
        self.btn_prev.update(mouse_pos)
        self.btn_next.update(mouse_pos)
        self.btn_play.update(mouse_pos)
        
        self.btn_prev.hovered = self.current_index > 0 and self.btn_prev.hovered
        self.btn_next.hovered = self.current_index < len(self.levels) - 1 and self.btn_next.hovered
    
    def draw(self, screen, bg_image=None):
        # Dessiner le fond
        if bg_image:
            bg_scaled = pygame.transform.scale(bg_image, screen.get_size())
            screen.blit(bg_scaled, (0, 0))
        else:
            screen.fill(COLOR_WHITE)
        
        # Texte des niveaux en blanc avec ombre
        for i in range(len(self.levels)):
            x_pos = WIDTH // 2 + (i * WIDTH) + int(self.current_x)
            y_pos = HEIGHT // 2 - 30
            
            if -WIDTH < x_pos < WIDTH * 2:
                # Ombre
                shadow = self.title_font.render(f"LEVEL {i+1}", True, (0, 0, 0, 150))
                shadow_rect = shadow.get_rect(center=(x_pos + 2, y_pos + 2))
                screen.blit(shadow, shadow_rect)
                
                # Texte principal
                title_text = self.title_font.render(f"LEVEL {i+1}", True, COLOR_WHITE)
                text_rect = title_text.get_rect(center=(x_pos, y_pos))
                screen.blit(title_text, text_rect)
        
        self.btn_prev.draw(screen)
        self.btn_next.draw(screen)
        self.btn_play.draw(screen)
    
    def get_current_level(self):
        return self.levels[self.current_index] if self.levels else None

# 🎨 ÉCRAN DE VICTOIRE
def draw_victory_screen(screen, mouse_pos, attempts):
    """Écran de victoire minimaliste avec style cohérent"""
    # Fond semi-transparent noir
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Police pixel
    title_font = get_pixel_font(48)
    stats_font = get_pixel_font(24)
    
    # Titre
    title = title_font.render("VICTORY!", True, COLOR_WHITE)
    title_shadow = title_font.render("VICTORY!", True, (0, 0, 0, 150))
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
    shadow_rect = title_shadow.get_rect(center=(WIDTH//2 + 2, HEIGHT//3 + 2))
    
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title, title_rect)
    
    # Statistiques
    stats = stats_font.render(f"Attempts: {attempts}", True, COLOR_WHITE)
    stats_rect = stats.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(stats, stats_rect)
    
    # Boutons
    btn_menu = MinimalButton(WIDTH//2 - 150, HEIGHT - 200, 140, 50, "MENU")
    btn_retry = MinimalButton(WIDTH//2 + 10, HEIGHT - 200, 140, 50, "RETRY")
    
    btn_menu.update(mouse_pos)
    btn_retry.update(mouse_pos)
    btn_menu.draw(screen)
    btn_retry.draw(screen)
    
    return {"menu": btn_menu.rect, "retry": btn_retry.rect}

# 🛠️ Instance globale
level_selector_instance = None

def get_level_selector(screen, levels):
    global level_selector_instance
    if level_selector_instance is None:
        level_selector_instance = LevelSelector(levels, screen)
    return level_selector_instance

# 🎨 MENU PRINCIPAL
def draw_menu(screen, mouse_pos, game_state, bg_image=None):
    if game_state != "MENU":
        return {}
    
    # Dessiner le fond
    if bg_image:
        bg_scaled = pygame.transform.scale(bg_image, screen.get_size())
        screen.blit(bg_scaled, (0, 0))
    else:
        screen.fill(COLOR_WHITE)
    
    # Police pixel
    title_font = get_pixel_font(64)
    
    # Titre avec ombre
    title = title_font.render("GEOMETRY DASH", True, COLOR_WHITE)
    title_shadow = title_font.render("GEOMETRY DASH", True, (0, 0, 0, 150))
    
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//3))
    shadow_rect = title_shadow.get_rect(center=(WIDTH//2 + 3, HEIGHT//3 + 3))
    
    screen.blit(title_shadow, shadow_rect)
    screen.blit(title, title_rect)
    
    # Boutons noirs transparents
    btn_play = MinimalButton(WIDTH//2 - 100, HEIGHT//2, 200, 60, "PLAY")
    btn_quit = MinimalButton(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60, "QUIT")
    
    btn_play.update(mouse_pos)
    btn_quit.update(mouse_pos)
    btn_play.draw(screen)
    btn_quit.draw(screen)
    
    return {"play": btn_play.rect, "quit": btn_quit.rect}

# 🎨 MENU PAUSE MINIMALISTE
def draw_pause_menu(screen, mouse_pos, game_state):
    if game_state != "PAUSE":
        return {}
    
    # Pas de fond, juste les boutons centrés
    btn_resume = MinimalButton(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 60, "RESUME")
    btn_menu = MinimalButton(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60, "MENU")
    
    btn_resume.update(mouse_pos)
    btn_menu.update(mouse_pos)
    btn_resume.draw(screen)
    btn_menu.draw(screen)
    
    return {"resume": btn_resume.rect, "menu": btn_menu.rect}

# 🎨 MENU SÉLECTION (placeholder)
def draw_level_select(screen, mouse_pos, available_levels, game_state):
    return {"back": pygame.Rect(0,0,0,0), "prev": pygame.Rect(0,0,0,0), 
            "next": pygame.Rect(0,0,0,0), "play": pygame.Rect(0,0,0,0), "levels": []}