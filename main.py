import pygame
import os
from level import Level

# 🟦 Importation de tous les menus
from menu import (
    draw_menu,
    draw_pause_menu,
    draw_level_select,
    WIDTH, HEIGHT
)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone - Enhanced")
clock = pygame.time.Clock()

# ------------------------------------------
# GAME STATE
# ------------------------------------------

class GameState:
    def __init__(self):
        self.state = "MENU"
        self.selected_level = None
        self.running = True

    def change(self, new):
        self.state = new

GAME_STATE = GameState()

# ------------------------------------------
# CHARGEMENT ASSETS
# ------------------------------------------

def load_assets():
    assets = {}
    try:
        assets["background"] = pygame.image.load("assets/background.png").convert()
        assets["player_cube"] = pygame.image.load("assets/cube.png").convert_alpha()
    except:
        print("⚠ Assets manquants → utilisation de blocs.")
        assets["background"] = pygame.Surface((1,1))
        assets["player_cube"] = pygame.Surface((30,30))
        assets["player_cube"].fill((255,0,0))
    return assets

ASSETS = load_assets()

# ------------------------------------------
# LECTURE NIVEAUX
# ------------------------------------------

def get_available_levels():
    if not os.path.exists("levels"):
        os.makedirs("levels")
        return []
    files = [f for f in os.listdir("levels") if f.startswith("level") and f.endswith(".json")]
    files.sort(key=lambda f: int(f.replace("level","").replace(".json","")))
    return files

AVAILABLE_LEVELS = get_available_levels()
DEFAULT_LEVEL = AVAILABLE_LEVELS[0] if AVAILABLE_LEVELS else "level1.json"

# Charger premier niveau
level = Level(f"levels/{DEFAULT_LEVEL}", ASSETS["background"], ASSETS["player_cube"])


# ------------------------------------------
# BOUCLE PRINCIPALE
# ------------------------------------------

while GAME_STATE.running:

    dt = clock.tick(60) / 1000
    mouse_pos = pygame.mouse.get_pos()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            GAME_STATE.running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if GAME_STATE.state == "GAME":
                GAME_STATE.change("PAUSE")
            elif GAME_STATE.state == "PAUSE":
                GAME_STATE.change("GAME")

    # --------------------- MENU PRINCIPAL
    if GAME_STATE.state == "MENU":
        btns = draw_menu(screen, mouse_pos)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["play"].collidepoint(mouse_pos):
                    GAME_STATE.change("LEVEL_SELECT")
                if btns["quit"].collidepoint(mouse_pos):
                    GAME_STATE.running = False

    # --------------------- SELECT NIVEAU
    elif GAME_STATE.state == "LEVEL_SELECT":
        data = draw_level_select(screen, mouse_pos, AVAILABLE_LEVELS)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if data["back"].collidepoint(mouse_pos):
                    GAME_STATE.change("MENU")

                for rect, lvl in data["levels"]:
                    if rect.collidepoint(mouse_pos):
                        GAME_STATE.selected_level = lvl
                        level = Level(f"levels/{lvl}", ASSETS["background"], ASSETS["player_cube"])
                        GAME_STATE.change("GAME")

    # --------------------- PAUSE
    elif GAME_STATE.state == "PAUSE":
        btns = draw_pause_menu(screen, mouse_pos)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if btns["resume"].collidepoint(mouse_pos):
                    GAME_STATE.change("GAME")
                if btns["menu"].collidepoint(mouse_pos):
                    level.reset()
                    GAME_STATE.change("MENU")

    # --------------------- JEU
    elif GAME_STATE.state == "GAME":

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            level.player.jump()

        level.update(dt)

        screen.fill((30,30,30))
        level.draw(screen, WIDTH)

    pygame.display.flip()

pygame.quit()
