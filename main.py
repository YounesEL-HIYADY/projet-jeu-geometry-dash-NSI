import pygame
import os
import sys

# INITIALISATION
pygame.init()
pygame.mixer.init()

from config import WIDTH, HEIGHT, COLOR_WHITE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Purist - Seasons")
clock = pygame.time.Clock()

from level import Level
from menu import draw_menu, draw_pause_menu, LevelSelector
from editor import Editor

ASSETS_CACHE = {}

class GameState:
    def __init__(self):
        self.state = "MENU"
        self.selected_level = None
        self.running = True
        self.attempts = 0

    def change(self, new):
        self.state = new
        # Reset transitions si besoin

GAME_STATE = GameState()

# Détection des niveaux
def get_available_levels():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    levels_dir = os.path.join(SCRIPT_DIR, "levels")
    if not os.path.exists(levels_dir):
        os.makedirs(levels_dir)
        # Création niveau par défaut vide
        with open(os.path.join(levels_dir, "level1.json"), "w") as f:
            f.write('{"tile_size":75,"layout":["====================="]}')
    
    files = [f for f in os.listdir(levels_dir) if f.endswith(".json")]
    files.sort()
    return files

AVAILABLE_LEVELS = get_available_levels()
level_selector = None
editor = None
level = None

# Charger un background vide pour level.py (car on utilise le procedural maintenant)
dummy_bg = pygame.Surface((WIDTH, HEIGHT))
dummy_bg.fill((0,0,0))

# BOUCLE PRINCIPALE
while GAME_STATE.running:
    dt = clock.tick(60) / 1000.0
    dt = min(dt, 0.016)
    
    mouse_pos = pygame.mouse.get_pos()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            GAME_STATE.running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if GAME_STATE.state == "GAME":
                    GAME_STATE.change("PAUSE")
                    level.camera.is_paused = True
                elif GAME_STATE.state == "PAUSE":
                    GAME_STATE.change("GAME")
                    level.camera.is_paused = False
                elif GAME_STATE.state == "EDITOR":
                    GAME_STATE.change("MENU")

    # --- ETAT : MENU PRINCIPAL ---
    if GAME_STATE.state == "MENU":
        btns = draw_menu(screen, mouse_pos, dt)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["play"].hovered:
                    GAME_STATE.change("LEVEL_SELECT")
                    level_selector = LevelSelector(get_available_levels(), screen)
                if btns["edit"].hovered:
                    GAME_STATE.change("EDITOR")
                    editor = Editor(screen, "level_new.json")
                if btns["quit"].hovered:
                    GAME_STATE.running = False

    # --- ETAT : SELECTION NIVEAU ---
    elif GAME_STATE.state == "LEVEL_SELECT":
        if level_selector:
            level_selector.update(mouse_pos, dt)
            level_selector.draw(screen)
            
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if level_selector.btn_prev.hovered: level_selector.navigate(-1)
                    elif level_selector.btn_next.hovered: level_selector.navigate(1)
                    elif level_selector.btn_back.hovered: GAME_STATE.change("MENU")
                    elif level_selector.btn_play.hovered:
                        # Lancer le jeu
                        lvl_name = level_selector.get_current_level()
                        path = os.path.join("levels", lvl_name)
                        level = Level(path, dummy_bg, ASSETS_CACHE, WIDTH, HEIGHT)
                        GAME_STATE.change("GAME")

    # --- ETAT : EDITEUR ---
    elif GAME_STATE.state == "EDITOR":
        if editor:
            result = editor.update(dt, events)
            editor.draw()
            if result == "MENU":
                GAME_STATE.change("MENU")
                # Rafraichir la liste des niveaux
                AVAILABLE_LEVELS = get_available_levels()

    # --- ETAT : JEU ---
    elif GAME_STATE.state == "GAME":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            level.player.jump()

        is_dead, is_completed = level.update(dt)
        
        if is_dead:
            level.reset()
            GAME_STATE.attempts += 1
        elif is_completed:
            GAME_STATE.change("LEVEL_SELECT") # Ou écran victoire

        screen.fill(COLOR_WHITE)
        level.draw(screen, WIDTH)

    # --- ETAT : PAUSE ---
    elif GAME_STATE.state == "PAUSE":
        level.draw(screen, WIDTH) # Dessiner le jeu en fond
        btns = draw_pause_menu(screen, mouse_pos)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["resume"].hovered:
                    GAME_STATE.change("GAME")
                    level.camera.is_paused = False
                if btns["menu"].hovered:
                    level.stop_music()
                    GAME_STATE.change("MENU")

    pygame.display.flip()

pygame.quit()
sys.exit()