import pygame
import os

# Dimensions de l'écran
WIDTH, HEIGHT = 800, 600

# Couleurs
BACKGROUND_COLOR = (15, 15, 25)
ACCENT_COLOR = (0, 200, 255)
TEXT_COLOR = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 215, 0)

# Chargement des assets UI
def load_ui_assets():
    assets = {}
    ui_path = "assets/ui/"
    
    try:
        # Boutons principaux
        if os.path.exists(os.path.join(ui_path, "button_round_depth_line.png")):
            assets["btn_round"] = pygame.image.load(os.path.join(ui_path, "button_round_depth_line.png")).convert_alpha()
        if os.path.exists(os.path.join(ui_path, "button_rectangle_depth_line.png")):
            assets["btn_rectangle"] = pygame.image.load(os.path.join(ui_path, "button_rectangle_depth_line.png")).convert_alpha()
        
        # Icônes
        if os.path.exists(os.path.join(ui_path, "icon_play_light.png")):
            assets["icon_play"] = pygame.image.load(os.path.join(ui_path, "icon_play_light.png")).convert_alpha()
        if os.path.exists(os.path.join(ui_path, "icon_repeat_light.png")):
            assets["icon_repeat"] = pygame.image.load(os.path.join(ui_path, "icon_repeat_light.png")).convert_alpha()
        if os.path.exists(os.path.join(ui_path, "icon_arrow_down_light.png")):
            assets["icon_arrow_down"] = pygame.image.load(os.path.join(ui_path, "icon_arrow_down_light.png")).convert_alpha()
        
        # Séparateurs - essaie différents noms possibles
        divider_paths = ["divider.png", "divider_edges.png"]
        for path in divider_paths:
            if os.path.exists(os.path.join(ui_path, path)):
                assets["divider"] = pygame.image.load(os.path.join(ui_path, path)).convert_alpha()
                break
        
        # Inputs
        if os.path.exists(os.path.join(ui_path, "input_outline_rectangle.png")):
            assets["input_rectangle"] = pygame.image.load(os.path.join(ui_path, "input_outline_rectangle.png")).convert_alpha()
        
    except Exception as e:
        print(f"⚠ Erreur chargement assets UI: {e}")
    
    return assets

def create_fallback_assets():
    assets = {}
    
    # Bouton round fallback
    btn_round = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(btn_round, ACCENT_COLOR, (50, 50), 45, 4)
    assets["btn_round"] = btn_round
    
    # Bouton rectangle fallback
    btn_rect = pygame.Surface((200, 60), pygame.SRCALPHA)
    pygame.draw.rect(btn_rect, ACCENT_COLOR, (0, 0, 200, 60), 4, border_radius=10)
    assets["btn_rectangle"] = btn_rect
    
    # Divider fallback
    divider = pygame.Surface((400, 4), pygame.SRCALPHA)
    pygame.draw.rect(divider, ACCENT_COLOR, (0, 0, 400, 2))
    assets["divider"] = divider
    
    # Input rectangle fallback
    input_rect = pygame.Surface((200, 50), pygame.SRCALPHA)
    pygame.draw.rect(input_rect, ACCENT_COLOR, (0, 0, 200, 50), 3, border_radius=5)
    assets["input_rectangle"] = input_rect
    
    # Icônes fallback
    icon_play = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.polygon(icon_play, TEXT_COLOR, [(10, 8), (10, 32), (30, 20)])
    assets["icon_play"] = icon_play
    
    icon_repeat = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.arc(icon_repeat, TEXT_COLOR, (5, 5, 30, 30), 0, 3.14, 3)
    pygame.draw.polygon(icon_repeat, TEXT_COLOR, [(35, 10), (25, 5), (25, 15)])
    assets["icon_repeat"] = icon_repeat
    
    return assets

# Chargement des assets
UI_ASSETS = load_ui_assets()

# Compléter avec les fallbacks pour les assets manquants
fallback_assets = create_fallback_assets()
for key, value in fallback_assets.items():
    if key not in UI_ASSETS:
        UI_ASSETS[key] = value
        print(f"⚠ Utilisation fallback pour: {key}")

# Police
def get_font(size):
    try:
        return pygame.font.Font("assets/fonts/arial.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size)

# Fonctions d'affichage
def draw_text(surface, text, size, x, y, color=TEXT_COLOR, centered=True):
    font = get_font(size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if centered:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_button(surface, rect, text, icon=None, hovered=False):
    # Utiliser le bouton rectangle ou fallback
    if "btn_rectangle" in UI_ASSETS:
        btn_scaled = pygame.transform.scale(UI_ASSETS["btn_rectangle"], (rect.width, rect.height))
    else:
        # Fallback direct
        btn_scaled = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_scaled, ACCENT_COLOR, (0, 0, rect.width, rect.height), 4, border_radius=10)
    
    # Effet de surbrillance
    if hovered:
        highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 30))
        btn_scaled.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    surface.blit(btn_scaled, rect)
    
    # Texte
    text_color = HIGHLIGHT_COLOR if hovered else TEXT_COLOR
    text_rect = draw_text(surface, text, 24, rect.centerx, rect.centery, text_color)
    
    # Icône si fournie
    if icon and icon in UI_ASSETS:
        icon_scaled = pygame.transform.scale(UI_ASSETS[icon], (30, 30))
        icon_rect = icon_scaled.get_rect(center=(rect.left + 30, rect.centery))
        surface.blit(icon_scaled, icon_rect)
    
    return rect

def draw_level_button(surface, rect, level_name, hovered=False):
    # Utilisation du style input pour les niveaux
    if "input_rectangle" in UI_ASSETS:
        btn_scaled = pygame.transform.scale(UI_ASSETS["input_rectangle"], (rect.width, rect.height))
    else:
        # Fallback direct
        btn_scaled = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_scaled, ACCENT_COLOR, (0, 0, rect.width, rect.height), 3, border_radius=5)
    
    if hovered:
        highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        btn_scaled.blit(highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    
    surface.blit(btn_scaled, rect)
    
    # Nom du niveau
    level_display = level_name.replace(".json", "").replace("level", "Level ")
    text_color = HIGHLIGHT_COLOR if hovered else ACCENT_COLOR
    draw_text(surface, level_display, 20, rect.centerx, rect.centery, text_color)
    
    return rect

def draw_divider(surface, x, y, width, height=20):
    """Dessine un séparateur avec gestion des assets manquants"""
    if "divider" in UI_ASSETS:
        divider_scaled = pygame.transform.scale(UI_ASSETS["divider"], (width, height))
        surface.blit(divider_scaled, (x, y))
    else:
        # Fallback pour le divider
        divider = pygame.Surface((width, 4), pygame.SRCALPHA)
        pygame.draw.rect(divider, ACCENT_COLOR, (0, 0, width, 2))
        pygame.draw.rect(divider, (100, 100, 100), (0, 2, width, 2))
        surface.blit(divider, (x, y + height//2 - 2))

# Menus
def draw_menu(screen, mouse_pos):
    screen.fill(BACKGROUND_COLOR)
    
    # Titre
    draw_text(screen, "GEOMETRY DASH", 48, WIDTH//2, 100, ACCENT_COLOR)
    
    # Séparateur
    draw_divider(screen, WIDTH//2 - 200, 200, 400)
    
    # Boutons
    button_width, button_height = 250, 60
    button_x = WIDTH//2 - button_width//2
    
    play_rect = pygame.Rect(button_x, 250, button_width, button_height)
    quit_rect = pygame.Rect(button_x, 330, button_width, button_height)
    
    play_hover = play_rect.collidepoint(mouse_pos)
    quit_hover = quit_rect.collidepoint(mouse_pos)
    
    draw_button(screen, play_rect, "PLAY", "icon_play", play_hover)
    draw_button(screen, quit_rect, "QUIT", None, quit_hover)
    
    # Footer
    draw_text(screen, "V1 - Younes EL HIYADY", 16, WIDTH//2, HEIGHT - 30, (150, 150, 150))
    
    return {
        "play": play_rect,
        "quit": quit_rect
    }

def draw_pause_menu(screen, mouse_pos):
    # Overlay semi-transparent
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # Panneau de pause
    panel_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 240)
    pygame.draw.rect(screen, (30, 30, 45), panel_rect, border_radius=15)
    pygame.draw.rect(screen, ACCENT_COLOR, panel_rect, 3, border_radius=15)
    
    # Titre
    draw_text(screen, "PAUSED", 36, WIDTH//2, panel_rect.top + 40, ACCENT_COLOR)
    
    # Séparateur
    draw_divider(screen, WIDTH//2 - 125, panel_rect.top + 70, 250, 15)
    
    # Boutons
    button_width, button_height = 200, 50
    button_x = WIDTH//2 - button_width//2
    
    resume_rect = pygame.Rect(button_x, panel_rect.top + 100, button_width, button_height)
    menu_rect = pygame.Rect(button_x, panel_rect.top + 160, button_width, button_height)
    
    resume_hover = resume_rect.collidepoint(mouse_pos)
    menu_hover = menu_rect.collidepoint(mouse_pos)
    
    draw_button(screen, resume_rect, "RESUME", "icon_play", resume_hover)
    draw_button(screen, menu_rect, "MAIN MENU", None, menu_hover)
    
    return {
        "resume": resume_rect,
        "menu": menu_rect
    }

def draw_level_select(screen, mouse_pos, available_levels):
    screen.fill(BACKGROUND_COLOR)
    
    # Titre
    draw_text(screen, "SELECT LEVEL", 36, WIDTH//2, 60, ACCENT_COLOR)
    
    # Séparateur
    draw_divider(screen, WIDTH//2 - 200, 100, 400)
    
    # Bouton retour
    back_rect = pygame.Rect(20, 20, 120, 40)
    back_hover = back_rect.collidepoint(mouse_pos)
    draw_button(screen, back_rect, "BACK", None, back_hover)
    
    # Grille des niveaux
    level_buttons = []
    level_width, level_height = 180, 60
    start_x = WIDTH//2 - (level_width * 2 + 40) // 2
    start_y = 150
    
    for i, level in enumerate(available_levels):
        row = i // 3
        col = i % 3
        x = start_x + col * (level_width + 20)
        y = start_y + row * (level_height + 20)
        
        level_rect = pygame.Rect(x, y, level_width, level_height)
        level_hover = level_rect.collidepoint(mouse_pos)
        
        draw_level_button(screen, level_rect, level, level_hover)
        level_buttons.append((level_rect, level))
    
    # Message si pas de niveaux
    if not available_levels:
        draw_text(screen, "No levels available", 24, WIDTH//2, HEIGHT//2, TEXT_COLOR)
        draw_text(screen, "Create levels in the 'levels' folder", 18, WIDTH//2, HEIGHT//2 + 40, (150, 150, 150))
    
    return {
        "back": back_rect,
        "levels": level_buttons
    }