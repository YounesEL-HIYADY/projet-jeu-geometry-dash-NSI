import pygame
import json
from player import Player
from objects import Platform, Spike, DustParticle

class Camera:
    """Gère le défilement de la caméra (au lieu de déplacer le monde)"""
    def __init__(self, scroll_speed):
        self.scroll_speed = scroll_speed
        self.offset_x = 0.0
    
    def update(self, dt):
        """Met à jour la position de la caméra"""
        self.offset_x += self.scroll_speed * dt
    
    def apply(self, rect):
        """Applique l'offset de caméra à un rect pour le dessin"""
        return rect.move(int(-self.offset_x), 0)

class Level:
    """
    Classe Level : gère le niveau complet avec caméra.
    """
    
    BASE_SCROLL_SPEED = 250.0 

    def __init__(self, level_path, bg_image, player_image): 
        """
        Initialise le niveau depuis un fichier JSON.
        """
        # Sauvegarde des ressources pour reset
        self.level_path = level_path 
        self.bg_image = bg_image 
        self.player_image = player_image
        
        # Création de la caméra
        self.camera = Camera(self.BASE_SCROLL_SPEED)
        
        # Données brutes pour reset
        self.raw_data = self._load_level_data()
        
        # Initialisation du contenu du niveau
        self._init_level_content()
        
    def _load_level_data(self):
        """Charge les données JSON (extrait pour le reset)"""
        try:
            with open(self.level_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erreur : Fichier de niveau introuvable à {self.level_path}")
            return {"tile_size": 75, "layout": ["========================================"]}
    
    def _init_level_content(self):
        """Initialise les objets du niveau (peut être rappelé)"""
        data = self.raw_data
        
        self.tile_size = data.get("tile_size", 75)
        layout = data["layout"]
        
        # Groupes de sprites
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        # Variables de progression
        self.level_end_x = 0  
        self.player_start_x = 100 
        
        # Génération des objets avec position monde fixe
        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                # Position dans le monde (CONSTANTE, ne bouge JAMAIS)
                world_x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if char == "=" or char == "P":
                    platform = Platform(world_x, y, self.tile_size)
                    self.platforms.add(platform)
                    self.level_end_x = max(self.level_end_x, world_x + self.tile_size)
                    
                elif char == "S":
                    spike = Spike(world_x, y + self.tile_size) 
                    self.spikes.add(spike)
                    self.level_end_x = max(self.level_end_x, spike.rect.right)
        
        # Création du joueur
        self.player = Player(self.player_start_x, 200, self.player_image)
    
    def reset(self):
        """RESET PROPRE : réinitialise le niveau sans appeler __init__"""
        # Vider les groupes de sprites
        self.platforms.empty()
        self.spikes.empty()
        self.particles.empty()
        
        # Réinitialiser la caméra
        self.camera.offset_x = 0.0
        
        # Reconstruire le niveau
        self._init_level_content()
    
    def update(self, dt):
        """
        Met à jour tous les éléments du niveau.
        """
        # 1. Mettre à jour la caméra
        self.camera.update(dt)
        
        # 2. Mise à jour du joueur (physique)
        was_on_ground = not self.player.is_jumping
        self.player.update(self.platforms, dt, self.camera) 
        
        # 3. Particules si atterrissage
        is_now_on_ground = not self.player.is_jumping
        if not was_on_ground and is_now_on_ground:
            for _ in range(8):
                particle = DustParticle(self.player.hitbox.centerx, self.player.hitbox.bottom)
                self.particles.add(particle)
        
        # 4. Mise à jour des particules
        self.particles.update(dt)
        self.particles = pygame.sprite.Group([p for p in self.particles if p.is_alive()])
        
        # 5. Vérifier collisions avec spikes
        for spike in self.spikes:
            if self.player.hitbox.colliderect(spike.hitbox):
                self.reset()
                return True  # Mort détectée
        
        return False
    
    def get_progress_data(self):
        """Retourne les données nécessaires à la barre de progression."""
        # La progression est basée sur la caméra, pas sur un offset de déplacement
        return self.camera.offset_x, self.level_end_x, self.player_start_x
    
    def draw(self, screen, screen_width):  # ✅ screen_width EN PARAMÈTRE
        """Affiche le fond, plateformes, spikes, particules et joueur."""
        # Fond étiré
        bg_scaled = pygame.transform.scale(self.bg_image, screen.get_size())
        screen.blit(bg_scaled, (0, 0))
        
        # Zone visible pour culling
        visible_left = self.camera.offset_x - 100
        visible_right = self.camera.offset_x + screen_width + 100
        
        # Dessiner objets avec offset caméra et culling
        for platform in self.platforms:
            if platform.rect.right > visible_left and platform.rect.left < visible_right:
                screen.blit(platform.image, self.camera.apply(platform.rect))
        
        for spike in self.spikes:
            if spike.rect.right > visible_left and spike.rect.left < visible_right:
                spike.draw(screen, self.camera)
        
        for particle in self.particles:
            if particle.rect.right > visible_left and particle.rect.left < visible_right:
                particle.draw(screen, self.camera)
        
        # Dessiner le joueur (toujours visible)
        self.player.draw(screen, self.camera)