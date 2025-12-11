import pygame
import os
import sys
import random

# ============================================
# 1. INITIALISATION PYGAME - DOIT ÊTRE EN PREMIER
# ============================================
pygame.init()
pygame.mixer.init()

# ============================================
# 2. IMPORT DES CONSTANTES
# ============================================
from config import WIDTH, HEIGHT

# ============================================
# 3. CRÉATION DE LA FENÊTRE AVANT TOUT IMPORT
# ============================================
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projet NSI Younes EL HIYADY")
clock = pygame.time.Clock()

# ============================================
# 4. IMPORT DU RESTE (après initialisation pygame)
# ============================================
from level import Level
from menu import draw_menu, draw_pause_menu, draw_level_select

# Cache global d'assets pour optimisation
ASSETS_CACHE = {}

# ============================================
# GAME STATE
# ============================================

class GameState:
    def __init__(self):
        self.state = "MENU"
        self.selected_level = None
        self.running = True
        self.attempts = 0

    def change(self, new):
        self.state = new

GAME_STATE = GameState()

# ============================================
# ÉCRAN DE VICTOIRE PREMIUM
# ============================================

def draw_victory_screen(screen, attempts, tile_size):
    """Écran de victoire avec animations"""
    screen.fill((10, 10, 30))
    
    # Particules de célébration
    for _ in range(30):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(3, 6)
        pygame.draw.circle(screen, (255, 215, 0), (x, y), size)
    
    # Titre principal
    title_font = pygame.font.SysFont("Arial", 72, bold=True)
    title = title_font.render("VICTORY!", True, (255, 215, 0))
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    screen.blit(title, title_rect)
    
    # Statistiques
    stats_font = pygame.font.SysFont("Arial", 36)
    stats = stats_font.render(f"Terminé en {attempts} tentatives", True, (255, 255, 255))
    stats_rect = stats.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(stats, stats_rect)
    
    # Boutons
    btn_font = pygame.font.SysFont("Arial", 28, bold=True)
    menu_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 80, 140, 50)
    retry_btn = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 80, 140, 50)
    
    # Dessiner boutons avec hover
    mouse_pos = pygame.mouse.get_pos()
    for btn, text in [(menu_btn, "MENU"), (retry_btn, "REJOUER")]:
        color = (0, 200, 255) if btn.collidepoint(mouse_pos) else (100, 100, 120)
        pygame.draw.rect(screen, color, btn, border_radius=15)
        txt = btn_font.render(text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=btn.center))
    
    return {"menu": menu_btn, "retry": retry_btn}

# ============================================
# CHARGEMENT ASSETS
# ============================================

def load_assets():
    assets = {}
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
    
    print(f"\n📁 Dossier racine : {SCRIPT_DIR}")
    print(f"📁 Dossier assets : {ASSETS_DIR}")
    
    try:
        # Background de secours
        bg_path = os.path.join(ASSETS_DIR, "background.png")
        if os.path.exists(bg_path):
            assets["background"] = pygame.image.load(bg_path).convert()
            print("✅ background.png")
        else:
            print("❌ background.png manquant")
            
        # Joueur de secours
        player_path = os.path.join(ASSETS_DIR, "cube.png")
        if os.path.exists(player_path):
            assets["player_cube"] = pygame.image.load(player_path).convert_alpha()
            print("✅ cube.png")
        else:
            print("❌ cube.png manquant")
        
        # Assets theme default
        block_path = os.path.join(ASSETS_DIR, "themes", "default", "block.png")
        if os.path.exists(block_path):
            assets["block_default"] = pygame.image.load(block_path).convert_alpha()
            print("✅ themes/default/block.png")
        else:
            print("❌ block.png manquant")
            
        spike_path = os.path.join(ASSETS_DIR, "themes", "default", "spike.png")
        if os.path.exists(spike_path):
            assets["spike_default"] = pygame.image.load(spike_path).convert_alpha()
            print("✅ themes/default/spike.png")
        else:
            print("❌ spike.png manquant")
        
    except Exception as e:
        print(f"⚠ Erreur chargement : {e}")
    
    # Fallbacks si manquant
    if "background" not in assets:
        print("⚠ Utilisation fallback background")
        assets["background"] = pygame.Surface((WIDTH, HEIGHT))
        assets["background"].fill((20, 20, 40))
    
    if "player_cube" not in assets:
        print("⚠ Utilisation fallback player")
        assets["player_cube"] = pygame.Surface((30, 30))
        assets["player_cube"].fill((255, 0, 0))
    
    if "block_default" not in assets:
        print("⚠ Utilisation fallback block")
        assets["block_default"] = pygame.Surface((75, 75))
        assets["block_default"].fill((100, 100, 100))
    
    if "spike_default" not in assets:
        print("⚠ Utilisation fallback spike")
        assets["spike_default"] = pygame.Surface((50, 50))
        assets["spike_default"].fill((200, 0, 0))
    
    return assets

ASSETS = load_assets()

# ============================================
# LECTURE NIVEAUX
# ============================================

def get_available_levels():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(SCRIPT_DIR, "levels")
    
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
        # Créer niveau par défaut
        default_path = os.path.join(levels_dir, "level1.json")
        with open(default_path, "w") as f:
            f.write('{"tile_size":75,"theme_folder":"default","layout":["========================================"]}')
        return ["level1.json"]
    
    files = [f for f in os.listdir(levels_dir) if f.startswith("level") and f.endswith(".json")]
    files.sort(key=lambda f: int(f.replace("level","").replace(".json","")))
    return files if files else []

AVAILABLE_LEVELS = get_available_levels()
DEFAULT_LEVEL = AVAILABLE_LEVELS[0] if AVAILABLE_LEVELS else "level1.json"

# Charger premier niveau
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
level_path = os.path.join(SCRIPT_DIR, "levels", DEFAULT_LEVEL)
level = Level(level_path, ASSETS["background"], ASSETS_CACHE, WIDTH, HEIGHT)

# ============================================
# BOUCLE PRINCIPALE
# ============================================

while GAME_STATE.running:
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 0.016)  # Clamp delta time
    
    mouse_pos = pygame.mouse.get_pos()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            GAME_STATE.running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if GAME_STATE.state == "GAME":
                GAME_STATE.change("PAUSE")
                level.camera.is_paused = True
            elif GAME_STATE.state == "PAUSE":
                GAME_STATE.change("GAME")
                level.camera.is_paused = False

    # --------------------- MENU PRINCIPAL
    if GAME_STATE.state == "MENU":
        btns = draw_menu(screen, mouse_pos, GAME_STATE.state)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["play"].collidepoint(mouse_pos):
                    GAME_STATE.change("LEVEL_SELECT")
                if btns["quit"].collidepoint(mouse_pos):
                    GAME_STATE.running = False

    # --------------------- SELECT NIVEAU
    elif GAME_STATE.state == "LEVEL_SELECT":
        data = draw_level_select(screen, mouse_pos, AVAILABLE_LEVELS, GAME_STATE.state)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if data["back"].collidepoint(mouse_pos):
                    GAME_STATE.change("MENU")

                for rect, lvl in data["levels"]:
                    if rect.collidepoint(mouse_pos):
                        GAME_STATE.selected_level = lvl
                        level.stop_music()
                        lvl_path = os.path.join(SCRIPT_DIR, "levels", lvl)
                        level = Level(lvl_path, ASSETS["background"], ASSETS_CACHE, WIDTH, HEIGHT)
                        GAME_STATE.attempts = 0
                        GAME_STATE.change("GAME")

    # --------------------- PAUSE
    elif GAME_STATE.state == "PAUSE":
        btns = draw_pause_menu(screen, mouse_pos, GAME_STATE.state)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["resume"].collidepoint(mouse_pos):
                    GAME_STATE.change("GAME")
                    level.camera.is_paused = False
                if btns["menu"].collidepoint(mouse_pos):
                    level.stop_music()
                    level.reset()
                    GAME_STATE.change("MENU")

    # --------------------- JEU
    elif GAME_STATE.state == "GAME":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            level.player.jump()

        # Update
        is_dead, is_completed = level.update(dt)
        
        if is_dead:
            GAME_STATE.attempts += 1
            level.reset()
        elif is_completed:
            print(f"✅ Niveau complété en {GAME_STATE.attempts + 1} tentatives!")
            GAME_STATE.change("VICTORY")

        # Render
        screen.fill((30,30,30))
        level.draw(screen, WIDTH)

    # --------------------- VICTOIRE
    elif GAME_STATE.state == "VICTORY":
        btns = draw_victory_screen(screen, GAME_STATE.attempts + 1, level.tile_size)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["menu"].collidepoint(mouse_pos):
                    GAME_STATE.change("LEVEL_SELECT")
                if btns["retry"].collidepoint(mouse_pos):
                    level.reset()
                    GAME_STATE.attempts = 0
                    GAME_STATE.change("GAME")

    pygame.display.flip()

pygame.quit()
sys.exit()