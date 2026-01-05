import pygame
import json
import os
from config import *
from ui import NiceButton, get_font

class Editor:
    def __init__(self, screen, level_name="level_new.json"):
        self.screen = screen
        self.level_name = level_name
        self.camera_x = 0
        self.tile_size = TILE_SIZE
        
        # Outils disponibles (Caractères map)
        self.tools = ['=', 'P', 'S', 'O', 'F']
        self.tool_names = ['Block', 'Platform', 'Spike', 'Orb', 'Flag']
        self.current_tool_idx = 0
        
        # Grille de données (dict {(x,y): char})
        self.grid = {}
        self.load_level()
        
        # UI
        self.font = get_font(20)
        self.btn_save = NiceButton(WIDTH - 120, 10, 100, 40, "SAVE", bg_color=(100, 255, 100, 200))
        self.btn_exit = NiceButton(10, 10, 100, 40, "EXIT", bg_color=(255, 100, 100, 200))

    def load_level(self):
        path = f"levels/{self.level_name}"
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    layout = data.get("layout", [])
                    for y, row in enumerate(layout):
                        for x, char in enumerate(row):
                            if char != ' ':
                                self.grid[(x, y)] = char
            except:
                print("Erreur chargement niveau")

    def save_level(self):
        if not self.grid: return
        
        max_x = max(k[0] for k in self.grid.keys())
        max_y = max(k[1] for k in self.grid.keys())
        
        # Convertir grille en liste de strings
        layout = []
        for y in range(max_y + 1):
            row_str = ""
            for x in range(max_x + 1):
                row_str += self.grid.get((x, y), " ")
            layout.append(row_str)
        
        # Structure JSON
        data = {
            "tile_size": 75,
            "theme_folder": "default", # À modifier manuellement si besoin
            "parallax_speed": 0.5,
            "layout": layout
        }
        
        if not os.path.exists("levels"): os.makedirs("levels")
        with open(f"levels/{self.level_name}", 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Niveau sauvegardé : {self.level_name}")

    def update(self, dt, events):
        keys = pygame.key.get_pressed()
        speed = 500 * dt
        if keys[pygame.K_LEFT]: self.camera_x -= speed
        if keys[pygame.K_RIGHT]: self.camera_x += speed
        self.camera_x = max(0, self.camera_x)
        
        mouse_pos = pygame.mouse.get_pos()
        grid_x = int((mouse_pos[0] + self.camera_x) // self.tile_size)
        grid_y = int(mouse_pos[1] // self.tile_size)
        
        self.btn_save.update(mouse_pos)
        self.btn_exit.update(mouse_pos)
        
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_save.hovered:
                    self.save_level()
                elif self.btn_exit.hovered:
                    return "MENU"
                elif e.button == 1: # Clic Gauche
                    if mouse_pos[1] > 60: # Pas sur l'UI
                        self.grid[(grid_x, grid_y)] = self.tools[self.current_tool_idx]
                elif e.button == 3: # Clic Droit (Gomme)
                    if (grid_x, grid_y) in self.grid:
                        del self.grid[(grid_x, grid_y)]
                elif e.button == 4: # Scroll Up
                    self.current_tool_idx = (self.current_tool_idx + 1) % len(self.tools)
                elif e.button == 5: # Scroll Down
                    self.current_tool_idx = (self.current_tool_idx - 1) % len(self.tools)
        return None

    def draw(self):
        self.screen.fill((30, 30, 40)) # Fond sombre éditeur
        
        # Dessiner la grille (lignes)
        start_col = int(self.camera_x // self.tile_size)
        end_col = start_col + (WIDTH // self.tile_size) + 1
        
        for x in range(start_col, end_col + 1):
            screen_x = x * self.tile_size - self.camera_x
            pygame.draw.line(self.screen, (50, 50, 60), (screen_x, 0), (screen_x, HEIGHT))
        for y in range(0, HEIGHT, self.tile_size):
            pygame.draw.line(self.screen, (50, 50, 60), (0, y), (WIDTH, y))
            
        # Dessiner les blocs
        for (gx, gy), char in self.grid.items():
            screen_x = gx * self.tile_size - self.camera_x
            screen_y = gy * self.tile_size
            if -self.tile_size < screen_x < WIDTH:
                color = (200, 200, 200)
                if char == '=': color = (100, 200, 100) # Sol
                elif char == 'S': color = (255, 50, 50) # Pique
                elif char == 'P': color = (100, 100, 255) # Plateforme
                elif char == 'O': color = (255, 255, 0) # Orbe
                
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0,0,0), rect, 1)
                
                # Lettre pour identifier
                txt = self.font.render(char, True, (0,0,0))
                self.screen.blit(txt, txt.get_rect(center=rect.center))

        # UI Overlay
        pygame.draw.rect(self.screen, (20, 20, 30), (0, 0, WIDTH, 60))
        self.btn_save.draw(self.screen)
        self.btn_exit.draw(self.screen)
        
        # Indicateur outil actuel
        tool_txt = self.font.render(f"Outil: {self.tool_names[self.current_tool_idx]} [{self.tools[self.current_tool_idx]}]", True, (255, 255, 255))
        self.screen.blit(tool_txt, (WIDTH//2 - 100, 20))