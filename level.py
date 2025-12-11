import pygame
import json
import os
from player import Player
from objects import Platform, Spike, DustParticle, Orb, FinishFlag

class Camera:
    """Gère le défilement de la caméra avec support pause"""
    def __init__(self, scroll_speed):
        self.scroll_speed = scroll_speed
        self.offset_x = 0.0
        self.is_paused = False
    
    def update(self, dt):
        """Met à jour la position de la caméra (gelée si pause)"""
        if not self.is_paused:
            self.offset_x += self.scroll_speed * dt
    
    def apply(self, rect):
        """Applique l'offset de caméra à un rect pour le dessin"""
        return rect.move(int(-self.offset_x), 0)

class Level:
    """
    Classe Level : gère le niveau complet avec caméra, parallaxe, sol et plateformes séparés.
    """
    
    BASE_SCROLL_SPEED = 250.0
    DEATH_ZONE_Y = 1000

    def __init__(self, level_path, bg_image, assets_cache, screen_width, screen_height): 
        """
        Initialise le niveau depuis un fichier JSON avec cache d'assets.
        """
        # Sauvegarde des ressources
        self.level_path = level_path 
        self.bg_image = bg_image 
        self.assets_cache = assets_cache
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Création de la caméra
        self.camera = Camera(self.BASE_SCROLL_SPEED)
        
        # Données brutes
        self.raw_data = self._load_level_data()
        
        # Initialisation
        self._init_level_content()
        
        # Musique
        self._load_music()
        
        # État
        self.is_completed = False
        self.respawn_invincibility = 0.0
        
    def _load_level_data(self):
        """Charge les données JSON"""
        try:
            with open(self.level_path) as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erreur : Fichier de niveau introuvable à {self.level_path}")
            return {"tile_size": 75, "layout": ["========================================"]}
    
    def _load_music(self):
        """Charge la musique du niveau si elle existe"""
        self.music_path = None
        try:
            level_name = os.path.basename(self.level_path).replace(".json", "")
            music_file = f"assets/music/{level_name}.mp3"
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
                self.music_path = music_file
                print(f"🎵 Musique chargée : {music_file}")
        except Exception as e:
            print(f"⚠ Pas de musique pour ce niveau : {e}")
    
    def stop_music(self):
        """Arrête la musique"""
        if self.music_path:
            pygame.mixer.music.stop()
    
    def _init_level_content(self):
        """Initialise les objets du niveau"""
        data = self.raw_data
        
        self.tile_size = data.get("tile_size", 75)
        layout = data["layout"]
        
        # Thème du niveau
        self.theme_folder = data.get("theme_folder", "default")
        
        # Parallaxe
        self.parallax_speed = data.get("parallax_speed", 0.5)
        
        # Préparation des assets de thème
        self._prepare_theme_assets()
        
        # Groupes
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()  # NOUVEAU
        self.finish_flags = pygame.sprite.Group()  # NOUVEAU
        
        # Progression
        self.level_end_x = len(layout[0]) * self.tile_size
        self.player_start_x = 100
        
        # Génération des objets
        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                world_x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                # DIFFÉRENCIATION SOL vs PLATEFORME
                if char == "=":
                    platform = Platform(world_x, y, self.tile_size, self.block_image)
                    self.platforms.add(platform)
                    
                elif char == "P":
                    platform = Platform(world_x, y, self.tile_size, self.platform_image)
                    self.platforms.add(platform)
                    
                elif char == "S":
                    spike = Spike(world_x, y + self.tile_size, self.tile_size, self.spike_image)
                    self.spikes.add(spike)
                
                # NOUVEAU : Orb
                elif char == "O":
                    orb = Orb(world_x, y, self.tile_size, self.orb_image)
                    self.orbs.add(orb)
                
                # NOUVEAU : Flag de fin
                elif char == "F":
                    flag = FinishFlag(world_x, y, self.tile_size)
                    self.finish_flags.add(flag)
        
        # Joueur
        self.player = Player(self.player_start_x, 200, self.player_image)
        self.respawn_invincibility = 0.5
    
    def _prepare_theme_assets(self):
        """Charge les images du thème ou fallback sur default"""
        theme_path = f"assets/themes/{self.theme_folder}"
        default_path = "assets/themes/default"
        
        # Block (sol)
        self.block_image = self._load_theme_asset(
            f"{theme_path}/block.png", 
            f"{default_path}/block.png"
        )
        self.block_image = pygame.transform.scale(self.block_image, (self.tile_size, self.tile_size))
        
        # Platform (plateformes en l'air)
        platform_img = self._load_theme_asset(
            f"{theme_path}/platform.png",
            f"{default_path}/platform.png"
        )
        # Fallback sur block.png si platform.png manque
        if platform_img is None:
            print(f"⚠ platform.png manquant pour le thème '{self.theme_folder}', fallback sur block.png")
            platform_img = self.block_image
        else:
            platform_img = pygame.transform.scale(platform_img, (self.tile_size, self.tile_size))
        
        self.platform_image = platform_img
        
        # Spike
        spike_img = self._load_theme_asset(
            f"{theme_path}/spike.png",
            f"{default_path}/spike.png"
        )
        spike_scale = 0.7 * (self.tile_size / spike_img.get_width())
        new_width = int(spike_img.get_width() * spike_scale)
        new_height = int(spike_img.get_height() * spike_scale)
        self.spike_image = pygame.transform.scale(spike_img, (new_width, new_height))
        
        # Player
        player_img = self._load_theme_asset(
            f"{theme_path}/player.png",
            f"{default_path}/player.png"
        )
        self.player_image = player_img
        
        # NOUVEAU : Orb
        orb_img = self._load_theme_asset(
            f"{theme_path}/orb.png",
            f"{default_path}/orb.png"
        )
        if orb_img is None:
            # Fallback : créer un cercle jaune
            orb_img = pygame.Surface((int(self.tile_size*0.6), int(self.tile_size*0.6)), pygame.SRCALPHA)
            pygame.draw.circle(orb_img, (255, 200, 0), orb_img.get_rect().center, orb_img.get_width()//2)
        
        self.orb_image = orb_img
        
        # Background layers parallaxe
        self.parallax_layers = []
        for i in range(1, 3):
            layer_path = f"{theme_path}/bg_layer{i}.png"
            layer_img = self._load_theme_asset(layer_path, None)
            if layer_img:
                layer_img = pygame.transform.scale(layer_img, (self.screen_width, self.screen_height))
                self.parallax_layers.append(layer_img)
    
    def _load_theme_asset(self, primary_path, fallback_path):
        """Charge un asset avec fallback"""
        cache_key = f"theme_{self.theme_folder}_{os.path.basename(primary_path)}"
        if cache_key in self.assets_cache:
            return self.assets_cache[cache_key]
        
        img = None
        if os.path.exists(primary_path):
            img = pygame.image.load(primary_path).convert_alpha()
        elif fallback_path and os.path.exists(fallback_path):
            img = pygame.image.load(fallback_path).convert_alpha()
        else:
            # Fallback ultime
            img = pygame.Surface((50, 50), pygame.SRCALPHA)
            img.fill((100, 100, 100))
        
        self.assets_cache[cache_key] = img
        return img
    
    def reset(self):
        """RESET PROPRE"""
        self.stop_music()
        
        self.platforms.empty()
        self.spikes.empty()
        self.particles.empty()
        self.orbs.empty()  # NOUVEAU
        self.finish_flags.empty()  # NOUVEAU
        
        self.camera.offset_x = 0.0
        self.camera.is_paused = False
        
        self._init_level_content()
        self.is_completed = False
    
    def update(self, dt):
        """Met à jour tous les éléments"""
        dt = min(dt, 0.016)
        
        self.camera.update(dt)
        
        if self.respawn_invincibility > 0:
            self.respawn_invincibility = max(0, self.respawn_invincibility - dt)
        
        # Update joueur
        was_on_ground = not self.player.is_jumping
        player_died = self.player.update(self.platforms, dt, self.camera) 
        
        if player_died:
            return (True, False)
        
        # Mort verticale
        if self.player.hitbox.top > self.DEATH_ZONE_Y:
            return (True, False)
        
        # Particules si atterrissage
        is_now_on_ground = not self.player.is_jumping
        if not was_on_ground and is_now_on_ground:
            for _ in range(8):
                particle = DustParticle(self.player.hitbox.centerx, self.player.hitbox.bottom)
                self.particles.add(particle)
        
        # Update particules
        self.particles.update(dt)
        
        # Update orbs
        for orb in self.orbs:
            orb.update(dt)
        
        # Collisions avec orbs
        for orb in self.orbs:
            if not orb.collected and self.player.hitbox.colliderect(orb.hitbox):
                orb.collect()
                self.player.collect_orb()
                print("✨ Double saut activé!")
        
        # Vérifier flag de fin
        for flag in self.finish_flags:
            if self.player.hitbox.colliderect(flag.rect):
                self.is_completed = True
                self.camera.is_paused = True
                self.stop_music()
                return (False, True)
        
        # Collisions spikes
        if self.respawn_invincibility <= 0:
            for spike in self.spikes:
                if self.player.hitbox.colliderect(spike.hitbox):
                    return (True, False)
        
        return (False, False)
    
    def get_progress_data(self):
        return self.camera.offset_x, self.level_end_x, self.player_start_x
    
    def draw(self, screen, screen_width):
        """Affiche avec parallaxe et culling"""
        # Fond
        bg_scaled = pygame.transform.scale(self.bg_image, screen.get_size())
        screen.blit(bg_scaled, (0, 0))
        
        # Parallaxe
        self._draw_parallax(screen, screen_width)
        
        # Culling zone
        visible_left = self.camera.offset_x - 100
        visible_right = self.camera.offset_x + screen_width + 100
        
        # Dessin objets
        for platform in self.platforms:
            if platform.rect.right > visible_left and platform.rect.left < visible_right:
                screen.blit(platform.image, self.camera.apply(platform.rect))
        
        for spike in self.spikes:
            if spike.rect.right > visible_left and spike.rect.left < visible_right:
                spike.draw(screen, self.camera)
        
        for orb in self.orbs:
            if not orb.collected:
                orb.draw(screen, self.camera)
        
        for particle in self.particles:
            if particle.rect.right > visible_left and platform.rect.left < visible_right:
                particle.draw(screen, self.camera)
        
        # Joueur
        self.player.draw(screen, self.camera, self.respawn_invincibility > 0)
    
    def _draw_parallax(self, screen, screen_width):
        """Dessine les layers de parallaxe"""
        for i, layer in enumerate(self.parallax_layers):
            speed = 0.3 * (i + 1)
            offset = int(self.camera.offset_x * speed)
            
            # Tiling infini
            screen.blit(layer, (-offset % screen_width - screen_width, 0))
            screen.blit(layer, (-offset % screen_width, 0))