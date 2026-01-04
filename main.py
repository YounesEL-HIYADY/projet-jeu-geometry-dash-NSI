import pygame
import os
import sys

# INITIALISATION
pygame.init()
pygame.mixer.init()

from config import WIDTH, HEIGHT, COLOR_WHITE, COLOR_BLACK
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Purist")
clock = pygame.time.Clock()

from level import Level
from menu import draw_menu, draw_pause_menu, draw_level_select, get_level_selector, draw_victory_screen

ASSETS_CACHE = {}

class GameState:
    def __init__(self):
        self.state = "MENU"
        self.selected_level = None
        self.running = True
        self.attempts = 0
        self.current_level_index = 0

    def change(self, new):
        self.state = new

GAME_STATE = GameState()

def load_assets():
    assets = {}
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 🎨 Charger le fond du menu principal
    try:
        bg_menu_path = os.path.join(SCRIPT_DIR, "assets", "bg.png")
        assets["menu_bg"] = pygame.image.load(bg_menu_path).convert() if os.path.exists(bg_menu_path) else None
    except:
        assets["menu_bg"] = None
    
    try:
        bg_path = os.path.join(SCRIPT_DIR, "assets", "background.png")
        assets["background"] = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else pygame.Surface((WIDTH, HEIGHT))
        if "background" not in assets or not isinstance(assets["background"], pygame.Surface):
            assets["background"] = pygame.Surface((WIDTH, HEIGHT))
            assets["background"].fill(COLOR_WHITE)
    except:
        assets["background"] = pygame.Surface((WIDTH, HEIGHT))
        assets["background"].fill(COLOR_WHITE)
    
    try:
        player_path = os.path.join(SCRIPT_DIR, "assets", "cube.png")
        assets["player_cube"] = pygame.image.load(player_path).convert_alpha() if os.path.exists(player_path) else pygame.Surface((30, 30))
    except:
        assets["player_cube"] = pygame.Surface((30, 30))
        assets["player_cube"].fill(COLOR_BLACK)
    
    return assets

ASSETS = load_assets()

def get_available_levels():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(SCRIPT_DIR, "levels")
    
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
        default_path = os.path.join(levels_dir, "level1.json")
        with open(default_path, "w") as f:
            f.write('{"tile_size":75,"theme_folder":"default","layout":["========================================"]}')
        return ["level1.json"]
    
    files = [f for f in os.listdir(levels_dir) if f.startswith("level") and f.endswith(".json")]
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    return files if files else []

AVAILABLE_LEVELS = get_available_levels()
DEFAULT_LEVEL = AVAILABLE_LEVELS[0] if AVAILABLE_LEVELS else "level1.json"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
level_path = os.path.join(SCRIPT_DIR, "levels", DEFAULT_LEVEL)
level = Level(level_path, ASSETS["background"], ASSETS_CACHE, WIDTH, HEIGHT)

level_selector = None

# BOUCLE PRINCIPALE
while GAME_STATE.running:
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 0.016)
    
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

    if GAME_STATE.state == "MENU":
        # 🎨 Passer le fond au menu
        btns = draw_menu(screen, mouse_pos, GAME_STATE.state, ASSETS.get("menu_bg"))

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["play"].collidepoint(mouse_pos):
                    GAME_STATE.change("LEVEL_SELECT")
                    level_selector = get_level_selector(screen, AVAILABLE_LEVELS)
                if btns["quit"].collidepoint(mouse_pos):
                    GAME_STATE.running = False

    elif GAME_STATE.state == "LEVEL_SELECT":
        if level_selector is None:
            level_selector = get_level_selector(screen, AVAILABLE_LEVELS)
        
        level_selector.update(mouse_pos, dt)
        level_selector.draw(screen, ASSETS.get("menu_bg"))
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if level_selector.btn_prev.rect.collidepoint(mouse_pos) and level_selector.current_index > 0:
                    level_selector.navigate(-1)
                elif level_selector.btn_next.rect.collidepoint(mouse_pos) and level_selector.current_index < len(AVAILABLE_LEVELS) - 1:
                    level_selector.navigate(1)
                elif level_selector.btn_play.rect.collidepoint(mouse_pos):
                    level_name = level_selector.get_current_level()
                    GAME_STATE.selected_level = level_name
                    level.stop_music()
                    lvl_path = os.path.join(SCRIPT_DIR, "levels", level_name)
                    level = Level(lvl_path, ASSETS["background"], ASSETS_CACHE, WIDTH, HEIGHT)
                    GAME_STATE.attempts = 0
                    GAME_STATE.change("GAME")
                    level_selector = None

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

    elif GAME_STATE.state == "GAME":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            level.player.jump()

        is_dead, is_completed = level.update(dt)
        
        if is_dead:
            GAME_STATE.attempts += 1
            level.reset()
        elif is_completed:
            print(f"✅ Niveau complété en {GAME_STATE.attempts + 1} tentatives!")
            GAME_STATE.change("VICTORY")

        screen.fill(COLOR_WHITE)
        level.draw(screen, WIDTH)

    elif GAME_STATE.state == "VICTORY":
        btns = draw_victory_screen(screen, mouse_pos, GAME_STATE.attempts + 1)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["menu"].collidepoint(mouse_pos):
                    GAME_STATE.change("LEVEL_SELECT")
                    level_selector = None
                if btns["retry"].collidepoint(mouse_pos):
                    level.reset()
                    GAME_STATE.attempts = 0
                    GAME_STATE.change("GAME")

    pygame.display.flip()

pygame.quit()
sys.exit()