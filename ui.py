import pygame
import random
import math
from config import WIDTH, HEIGHT, THEMES, COLOR_WHITE

# Gestionnaire de police global
def get_font(size):
    try:
        return pygame.font.Font("assets/fonts/pixel.ttf", size)
    except:
        return pygame.font.SysFont("Verdana", size, bold=True)

class SeasonalBackground:
    def __init__(self):
        self.particles = []
        self.current_theme = "default"
        # Initialisation sécurisée des couleurs (copie de la liste)
        self.target_color_top = list(THEMES["default"]["bg_top"])
        self.current_color_top = list(self.target_color_top)
        self.timer = 0
        
        # Créer des particules initiales
        for _ in range(50):
            self.particles.append(self._create_particle())

    def set_theme(self, theme_name):
        # Si le thème n'existe pas, on cherche un mot clé
        found = "default"
        if theme_name in THEMES:
            found = theme_name
        else:
            for key in THEMES:
                if key in theme_name.lower():
                    found = key
                    break
        
        self.current_theme = found
        self.target_color_top = list(THEMES[found]["bg_top"])

    def _create_particle(self):
        return {
            'x': random.randint(0, WIDTH),
            'y': random.randint(0, HEIGHT),
            'radius': random.randint(2, 5),
            'speed_y': random.uniform(0.5, 2.0),
            'speed_x': random.uniform(-0.5, 0.5),
            'phase': random.uniform(0, 6.28)
        }

    def update(self, dt):
        self.timer += dt
        
        # Transition fluide de couleur de fond (Lerp)
        for i in range(3):
            self.current_color_top[i] += (self.target_color_top[i] - self.current_color_top[i]) * 5 * dt

        # Mise à jour des particules
        for p in self.particles:
            p['y'] += p['speed_y']
            p['x'] += math.sin(self.timer + p['phase']) * 0.5 # Mouvement organique
            
            if p['y'] > HEIGHT:
                p['y'] = -10
                p['x'] = random.randint(0, WIDTH)

    def draw(self, screen):
        # Dessiner le fond uni (couleur interpolée)
        bg_col = tuple(map(int, self.current_color_top))
        screen.fill(bg_col)
        
        # Dessiner les particules
        theme_data = THEMES[self.current_theme]
        p_col = theme_data["particle"]
        
        for p in self.particles:
            # Surface transparente pour la particule
            surf = pygame.Surface((p['radius']*2, p['radius']*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, p_col, (p['radius'], p['radius']), p['radius'])
            screen.blit(surf, (int(p['x']), int(p['y'])))

class NiceButton:
    def __init__(self, x, y, w, h, text, icon_char=None, bg_color=(255,255,255,200), text_color=(50,50,50), disabled=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon = icon_char
        self.bg_color = bg_color
        self.text_color = text_color
        self.hovered = False
        self.font = get_font(24)
        self.y_offset = 0 # Pour l'animation
        self.disabled = disabled # État désactivé
        
    def update(self, mouse_pos):
        if self.disabled:
            self.hovered = False
            self.y_offset = 0
            return False

        self.hovered = self.rect.collidepoint(mouse_pos)
        # Animation petite levée
        target_y = -6 if self.hovered else 0
        self.y_offset += (target_y - self.y_offset) * 0.2
        return self.hovered

    def draw(self, screen):
        # Ombre
        shadow_rect = self.rect.copy()
        if not self.disabled:
            shadow_rect.y += 5
        else:
            shadow_rect.y += 2 # Ombre plus petite si lock
            
        pygame.draw.rect(screen, (0,0,0,50), shadow_rect, border_radius=12)
        
        # Bouton (avec décalage animation)
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.y_offset)
        
        # Surface transparente pour le bouton
        btn_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        
        # --- GESTION DES COULEURS ---
        if self.disabled:
            # Couleur Grise pour le verrouillage
            col = [150, 150, 150, 200] 
            current_text_col = (100, 100, 100)
            border_col = (180, 180, 180)
        else:
            # Couleur normale
            col = list(self.bg_color)
            if len(col) == 3: col.append(255) # Ajoute alpha si absent
            
            # ✨ EFFET HOVER RENFORCÉ (+50 au lieu de +20)
            if self.hovered: 
                col = [min(c + 50, 255) for c in col[:3]] + [col[3]]
            
            current_text_col = self.text_color
            border_col = (255, 255, 255)
        
        pygame.draw.rect(btn_surf, col, btn_surf.get_rect(), border_radius=12)
        pygame.draw.rect(btn_surf, border_col, btn_surf.get_rect(), 2, border_radius=12) # Bord
        
        screen.blit(btn_surf, draw_rect)
        
        # Texte
        content = self.icon if self.icon else self.text
        # Ajout du cadenas visuel si pas d'icône
        if self.disabled and not self.icon:
            content += " [X]" 
            
        txt_surf = self.font.render(content, True, current_text_col)
        txt_rect = txt_surf.get_rect(center=draw_rect.center)
        screen.blit(txt_surf, txt_rect)