WIDTH, HEIGHT = 800, 600
TILE_SIZE = 75
CULLING_CELL_SIZE = 800
MAX_LEVELS_DISPLAYED = 5

# --- PALETTES DE SAISONS (UI) ---
THEMES = {
    "default": {
        "bg_top": (100, 200, 255),    # Bleu ciel
        "bg_bottom": (255, 255, 255),
        "particle": (255, 255, 255, 150),
        "ui_bg": (255, 255, 255, 200),
        "text": (50, 50, 60)
    },
    "summer": {
        "bg_top": (255, 200, 100),    # Orange doux (Coucher de soleil)
        "bg_bottom": (255, 255, 200),
        "particle": (255, 250, 200, 180), # Pollen doré
        "ui_bg": (255, 240, 230, 200),
        "text": (80, 50, 40)
    },
    "winter": {
        "bg_top": (20, 30, 60),       # Bleu nuit profond
        "bg_bottom": (80, 100, 150),
        "particle": (200, 230, 255, 200), # Neige bleutée
        "ui_bg": (20, 40, 60, 200),
        "text": (220, 240, 255)
    }
}

# UI GLOBAL
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_ACCENT = (255, 180, 50) # Orange bouton