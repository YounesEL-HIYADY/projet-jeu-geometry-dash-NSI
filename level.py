import pygame
import json
from player import Player
from objects import Platform, Spike

class Level:
    """
    Classe Level : gère le niveau complet.
    Nouveau système : niveau ASCII très simple à éditer pour créer des niveaux cohérents.
    """

    def __init__(self, level_path):
        """
        Initialise le niveau depuis un fichier JSON.
        level_path : chemin vers le fichier JSON du niveau
        """
        # --- Charger le fichier JSON ---
        with open(level_path) as f:
            data = json.load(f)

        # Taille d'une tuile (pour toutes les plateformes et spikes)
        self.tile_size = data.get("tile_size", 75)

        # Récupérer la "carte ASCII" du niveau
        layout = data["layout"]

        # --- Groupes de sprites ---
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()

        # --- Génération automatique des plateformes et pics ---
        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                x = col_index * self.tile_size
                y = row_index * self.tile_size

                if char == "=" or char == "P":
                    # "=" = sol continu, "P" = plateforme flottante
                    self.platforms.add(Platform(x, y, self.tile_size, self.tile_size))
                elif char == "S":
                    # "S" = pic
                    # Positionner le pic en bas de la tuile (ground_y)
                    self.spikes.add(Spike(x, y + self.tile_size))

        # --- Joueur ---
        # Position de départ du joueur (à gauche du niveau)
        self.player = Player(100, 200)

        # Vitesse de défilement du niveau (scroll)
        self.scroll_speed = 5

        # --- Fond ---
        self.bg_image = pygame.image.load("assets/background.png").convert_alpha()
        # Plus besoin de scale ici, on le fera à l'affichage pour toujours remplir la fenêtre

    def update(self):
        """
        Met à jour tous les éléments du niveau :
        - Scroll horizontal
        - Gravité et collisions du joueur
        - Collision avec les spikes (reset niveau)
        """
        # Scroll horizontal : déplacer toutes les plateformes et spikes vers la gauche
        for platform in self.platforms:
            platform.rect.x -= self.scroll_speed
        for spike in self.spikes:
            spike.rect.x -= self.scroll_speed

        # Mise à jour du joueur (gravité + collisions)
        self.player.update(self.platforms)

        # Collision avec les spikes → réinitialiser le niveau
        for spike in self.spikes:
            if self.player.rect.colliderect(spike.rect):
                self.__init__("levels/level1.json")

    def draw(self, screen):
        """
        Affiche le fond, plateformes, spikes et joueur
        Le fond est étiré automatiquement pour remplir toute la fenêtre
        """
        # --- Fond étiré ---
        bg_scaled = pygame.transform.scale(self.bg_image, screen.get_size())
        screen.blit(bg_scaled, (0, 0))

        # --- Dessiner plateformes et spikes ---
        self.platforms.draw(screen)
        self.spikes.draw(screen)

        # --- Dessiner le joueur ---
        screen.blit(self.player.image, self.player.rect)
