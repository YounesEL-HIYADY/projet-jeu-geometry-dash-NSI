import pygame
from config import *
from ui import NiceButton, get_font, SeasonalBackground

class LevelSelector:
    def __init__(self, levels_list, screen):
        self.levels = levels_list
        self.screen = screen
        self.current_index = 0
        self.target_x = 0
        self.current_x = 0
        
        # UI Elements
        self.btn_prev = NiceButton(20, HEIGHT//2 - 25, 50, 50, "<")
        self.btn_next = NiceButton(WIDTH - 70, HEIGHT//2 - 25, 50, 50, ">")
        self.btn_play = NiceButton(WIDTH//2 - 100, HEIGHT - 120, 200, 60, "JOUER", bg_color=COLOR_ACCENT, text_color=COLOR_WHITE)
        self.btn_back = NiceButton(20, 20, 100, 40, "RETOUR")
        
        self.title_font = get_font(50)
        self.bg_manager = SeasonalBackground()
        
    def update(self, mouse_pos, dt):
        # Animation fluide défilement
        diff = self.target_x - self.current_x
        self.current_x += diff * 10 * dt
        
        # Update UI
        self.btn_prev.update(mouse_pos)
        self.btn_next.update(mouse_pos)
        self.btn_play.update(mouse_pos)
        self.btn_back.update(mouse_pos)
        
        # Update fond dynamique selon le niveau sélectionné
        current_lvl = self.get_current_level()
        if current_lvl:
            # On devine le thème par le nom du fichier
            theme = "default"
            if "level1" in current_lvl: theme = "summer"
            elif "level2" in current_lvl: theme = "winter"
            self.bg_manager.set_theme(theme)
            
        self.bg_manager.update(dt)
        
    def navigate(self, direction):
        new_index = self.current_index + direction
        if 0 <= new_index < len(self.levels):
            self.current_index = new_index
            self.target_x = -self.current_index * WIDTH

    def draw(self, screen):
        # 1. Dessiner le fond dynamique
        self.bg_manager.draw(screen)
        
        # 2. Dessiner les cartes de niveaux
        for i, level_name in enumerate(self.levels):
            x_pos = WIDTH // 2 + (i * WIDTH) + int(self.current_x)
            y_pos = HEIGHT // 2
            
            # Ne dessiner que si visible à l'écran
            if -WIDTH < x_pos < WIDTH * 2:
                # Carte style "Verre" / blanc transparent
                card_rect = pygame.Rect(0, 0, 400, 300)
                card_rect.center = (x_pos, y_pos)
                
                # Fond carte
                card_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
                pygame.draw.rect(card_surf, (255, 255, 255, 180), card_surf.get_rect(), border_radius=20)
                pygame.draw.rect(card_surf, (255, 255, 255), card_surf.get_rect(), 3, border_radius=20)
                screen.blit(card_surf, card_rect)
                
                # Nom du niveau
                display_name = f"NIVEAU {i+1}"
                txt = self.title_font.render(display_name, True, (50, 50, 60))
                screen.blit(txt, txt.get_rect(center=(x_pos, y_pos - 30)))
                
                # Sous-titre (Theme)
                theme_txt = "Été" if i == 0 else "Hiver" if i == 1 else "Inconnu"
                sub = get_font(30).render(theme_txt, True, (100, 100, 120))
                screen.blit(sub, sub.get_rect(center=(x_pos, y_pos + 20)))

        # 3. UI Fixe
        if self.current_index > 0:
            self.btn_prev.draw(screen)
        if self.current_index < len(self.levels) - 1:
            self.btn_next.draw(screen)
            
        self.btn_play.draw(screen)
        self.btn_back.draw(screen)

    def get_current_level(self):
        return self.levels[self.current_index] if self.levels else None

# --- MENU PRINCIPAL ---
main_bg = SeasonalBackground() # Fond du menu principal

def draw_menu(screen, mouse_pos, dt):
    main_bg.set_theme("summer") # Thème par défaut du menu
    main_bg.update(dt)
    main_bg.draw(screen)
    
    # Titre
    font_title = get_font(70)
    title = font_title.render("GEOMETRY PURIST", True, COLOR_WHITE)
    shadow = font_title.render("GEOMETRY PURIST", True, (0,0,0,50))
    
    screen.blit(shadow, shadow.get_rect(center=(WIDTH//2+4, HEIGHT//3+4)))
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//3)))
    
    # Boutons
    btn_play = NiceButton(WIDTH//2 - 100, HEIGHT//2, 200, 60, "JOUER")
    
    # 🔒 BOUTON EDITEUR VÉROUILLÉ (disabled=True)
    btn_edit = NiceButton(WIDTH//2 - 100, HEIGHT//2 + 70, 200, 60, "EDITEUR", disabled=True)
    
    btn_quit = NiceButton(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 60, "QUITTER", bg_color=(255, 100, 100, 200))
    
    btn_play.update(mouse_pos)
    btn_edit.update(mouse_pos)
    btn_quit.update(mouse_pos)
    
    btn_play.draw(screen)
    btn_edit.draw(screen)
    btn_quit.draw(screen)
    
    return {"play": btn_play, "edit": btn_edit, "quit": btn_quit}

def draw_pause_menu(screen, mouse_pos):
    # Overlay sombre
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0,0,0,150))
    screen.blit(ov, (0,0))
    
    btn_resume = NiceButton(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 60, "REPRENDRE")
    btn_menu = NiceButton(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 60, "MENU", bg_color=(255, 100, 100, 200))
    
    btn_resume.update(mouse_pos)
    btn_menu.update(mouse_pos)
    
    btn_resume.draw(screen)
    btn_menu.draw(screen)
    
    return {"resume": btn_resume, "menu": btn_menu}