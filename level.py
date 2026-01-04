import pygame
import json
import os
import random
from player import Player
from objects import Platform, Spike, Orb, FinishFlag
from config import CULLING_CELL_SIZE

class SpatialHash:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}
    
    def _hash(self, x, y):
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def insert(self, obj, rect):
        cells = self._get_cells(rect)
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(obj)
    
    def _get_cells(self, rect):
        cells = set()
        top_left = self._hash(rect.left, rect.top)
        bottom_right = self._hash(rect.right, rect.bottom)
        
        for x in range(top_left[0], bottom_right[0] + 1):
            for y in range(top_left[1], bottom_right[1] + 1):
                cells.add((x, y))
        return cells
    
    def query(self, rect):
        cells = self._get_cells(rect)
        objects = set()
        for cell in cells:
            if cell in self.grid:
                objects.update(self.grid[cell])
        return list(objects)
    
    def clear(self):
        self.grid.clear()

class Camera:
    def __init__(self, scroll_speed):
        self.scroll_speed = scroll_speed
        self.offset_x = 0.0
        self.is_paused = False
        # Camera shake
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
    
    def update(self, dt):
        if not self.is_paused:
            self.offset_x += self.scroll_speed * dt
        
        # Update shake
        if self.shake_duration > 0:
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_intensity = 0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
    
    def apply(self, rect):
        # Combine scroll offset with shake
        return rect.move(int(-self.offset_x + self.shake_offset_x), int(self.shake_offset_y))
    
    def trigger_shake(self, intensity=5, duration=0.15):
        self.shake_intensity = intensity
        self.shake_duration = duration

class Level:
    BASE_SCROLL_SPEED = 250.0
    DEATH_ZONE_Y = 1000

    def __init__(self, level_path, bg_image, assets_cache, screen_width, screen_height): 
        self.level_path = level_path 
        self.bg_image = bg_image 
        self.assets_cache = assets_cache
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.camera = Camera(self.BASE_SCROLL_SPEED)
        self.raw_data = self._load_level_data()
        self.spatial_hash = SpatialHash(CULLING_CELL_SIZE)
        self._init_level_content()
        self._load_music()
        
        self.is_completed = False
        self.respawn_invincibility = 0.5
        
        # 🛠️ NEW: Timer pour effets de mort
        self.death_fx_timer = 0.0
    
    def _load_level_data(self):
        try:
            with open(self.level_path) as f:
                return json.load(f)
        except:
            return {"tile_size": 75, "layout": ["========================================"]}
    
    def _load_music(self):
        self.music_path = None
        try:
            level_name = os.path.basename(self.level_path).replace(".json", "")
            music_file = f"assets/music/{level_name}.mp3"
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.7)
                pygame.mixer.music.play(-1)
                self.music_path = music_file
        except Exception as e:
            print(f"⚠ Pas de musique : {e}")
    
    def stop_music(self):
        if self.music_path:
            pygame.mixer.music.stop()
    
    def _init_level_content(self):
        data = self.raw_data
        self.tile_size = data.get("tile_size", 75)
        layout = data["layout"]
        self.theme_folder = data.get("theme_folder", "default")
        self.parallax_speed = data.get("parallax_speed", 0.5)
        
        self._prepare_theme_assets()
        
        self.platforms = pygame.sprite.Group()
        self.spikes = pygame.sprite.Group()
        self.orbs = pygame.sprite.Group()
        self.finish_flags = pygame.sprite.Group()
        
        self.level_end_x = len(layout[0]) * self.tile_size
        self.player_start_x = 100
        
        self.spatial_hash.clear()
        
        for row_index, row in enumerate(layout):
            for col_index, char in enumerate(row):
                world_x = col_index * self.tile_size
                y = row_index * self.tile_size
                
                if char == "=":
                    platform = Platform(world_x, y, self.tile_size, self.block_image)
                    self.platforms.add(platform)
                    self.spatial_hash.insert(platform, platform.rect)
                    
                elif char == "P":
                    platform = Platform(world_x, y, self.tile_size, self.platform_image)
                    self.platforms.add(platform)
                    self.spatial_hash.insert(platform, platform.rect)
                    
                elif char == "S":
                    spike = Spike(world_x, y + self.tile_size, self.tile_size, self.spike_image)
                    self.spikes.add(spike)
                    self.spatial_hash.insert(spike, spike.rect)
                
                elif char == "O":
                    orb = Orb(world_x, y, self.tile_size, self.orb_image)
                    self.orbs.add(orb)
                    self.spatial_hash.insert(orb, orb.rect)
                
                elif char == "F":
                    flag = FinishFlag(world_x, y, self.tile_size)
                    self.finish_flags.add(flag)
                    self.spatial_hash.insert(flag, flag.rect)
        
        self.player = Player(self.player_start_x, 200, self.player_image)
        self.respawn_invincibility = 0.5
    
    def _prepare_theme_assets(self):
        theme_path = f"assets/themes/{self.theme_folder}"
        default_path = "assets/themes/default"
        
        self.block_image = self._load_theme_asset(
            f"{theme_path}/block.png", 
            f"{default_path}/block.png"
        )
        self.block_image = pygame.transform.scale(self.block_image, (self.tile_size, self.tile_size))
        
        platform_img = self._load_theme_asset(
            f"{theme_path}/platform.png",
            f"{default_path}/platform.png"
        )
        if platform_img is None:
            platform_img = self.block_image
        else:
            platform_img = pygame.transform.scale(platform_img, (self.tile_size, self.tile_size))
        self.platform_image = platform_img
        
        spike_img = self._load_theme_asset(
            f"{theme_path}/spike.png",
            f"{default_path}/spike.png"
        )
        spike_scale = 0.7 * (self.tile_size / spike_img.get_width())
        new_width = int(spike_img.get_width() * spike_scale)
        new_height = int(spike_img.get_height() * spike_scale)
        self.spike_image = pygame.transform.scale(spike_img, (new_width, new_height))
        
        player_img = self._load_theme_asset(
            f"{theme_path}/player.png",
            f"{default_path}/player.png"
        )
        self.player_image = player_img
        
        orb_img = self._load_theme_asset(
            f"{theme_path}/orb.png",
            f"{default_path}/orb.png"
        )
        if orb_img is None:
            orb_img = pygame.Surface((int(self.tile_size*0.6), int(self.tile_size*0.6)), pygame.SRCALPHA)
            pygame.draw.circle(orb_img, (255, 200, 0), orb_img.get_rect().center, orb_img.get_width()//2)
        self.orb_image = orb_img
        
        self.parallax_layers = []
        for i in range(1, 3):
            layer_path = f"{theme_path}/bg_layer{i}.png"
            layer_img = self._load_theme_asset(layer_path, None)
            if layer_img:
                layer_img = pygame.transform.scale(layer_img, (self.screen_width, self.screen_height))
                self.parallax_layers.append(layer_img)
    
    def _load_theme_asset(self, primary_path, fallback_path):
        cache_key = f"theme_{self.theme_folder}_{os.path.basename(primary_path)}"
        if cache_key in self.assets_cache:
            return self.assets_cache[cache_key]
        
        img = None
        if os.path.exists(primary_path):
            img = pygame.image.load(primary_path).convert_alpha()
        elif fallback_path and os.path.exists(fallback_path):
            img = pygame.image.load(fallback_path).convert_alpha()
        else:
            img = pygame.Surface((50, 50), pygame.SRCALPHA)
            img.fill((100, 100, 100))
        
        self.assets_cache[cache_key] = img
        return img
    
    def reset(self):
        self.stop_music()
        self.platforms.empty()
        self.spikes.empty()
        self.orbs.empty()
        self.finish_flags.empty()
        
        self.camera.offset_x = 0.0
        self.camera.is_paused = False
        
        self._init_level_content()
        self.is_completed = False
        self.death_fx_timer = 0.0  # 🛠️ Reset
    
    def update(self, dt):
        dt = min(dt, 0.016)
        self.camera.update(dt)
        
        if self.respawn_invincibility > 0:
            self.respawn_invincibility = max(0, self.respawn_invincibility - dt)
        
        # 🛠️ Update death FX timer
        if self.death_fx_timer > 0:
            self.death_fx_timer -= dt
        
        # Zone de culling
        visible_rect = pygame.Rect(
            self.camera.offset_x - 100,
            0,
            self.screen_width + 200,
            self.screen_height
        )
        
        all_visible_objects = self.spatial_hash.query(visible_rect)
        visible_platforms = [obj for obj in all_visible_objects if isinstance(obj, Platform)]
        
        player_died = self.player.update(visible_platforms, dt, self.camera) 
        
        if player_died:
            self.camera.trigger_shake(6, 0.15)
            self.death_fx_timer = 0.3  # 🛠️ 0.3s d'effet
            return (True, False)
        
        if self.player.hitbox.top > self.DEATH_ZONE_Y:
            self.camera.trigger_shake(6, 0.15)
            self.death_fx_timer = 0.3  # 🛠️ 0.3s d'effet
            return (True, False)
        
        # Update orbs
        for orb in self.orbs:
            if visible_rect.colliderect(orb.rect):
                orb.update(dt)
        
        # Collecter orbs
        for orb in self.orbs:
            if not orb.collected and self.player.hitbox.colliderect(orb.hitbox):
                orb.collect()
                self.player.collect_orb()
        
        # Vérifier flag de fin
        for flag in self.finish_flags:
            if self.player.hitbox.colliderect(flag.rect):
                self.is_completed = True
                self.camera.is_paused = True
                self.stop_music()
                return (False, True)
        
        # Vérifier collision spikes
        if self.respawn_invincibility <= 0:
            visible_spikes = [obj for obj in all_visible_objects if isinstance(obj, Spike)]
            for spike in visible_spikes:
                if self.player.hitbox.colliderect(spike.hitbox):
                    self.camera.trigger_shake(6, 0.15)
                    self.death_fx_timer = 0.3  # 🛠️ 0.3s d'effet
                    return (True, False)
        
        return (False, False)
    
    def get_progress_data(self):
        return self.camera.offset_x, self.level_end_x, self.player_start_x
    
    def draw(self, screen, screen_width):
        # 🛠️ Background with shake offset
        bg_scaled = pygame.transform.scale(self.bg_image, screen.get_size())
        bg_pos = (int(self.camera.shake_offset_x), int(self.camera.shake_offset_y))
        screen.blit(bg_scaled, bg_pos)
        
        # Parallax
        self._draw_parallax(screen, screen_width)
        
        # Progress bar
        self._draw_progress_bar(screen)
        
        # Zone de rendu
        visible_left = self.camera.offset_x - 100
        visible_right = self.camera.offset_x + screen_width + 100
        
        query_rect = pygame.Rect(visible_left, -100, visible_right - visible_left + 200, self.screen_height + 200)
        visible_objects = self.spatial_hash.query(query_rect)
        
        # Dessiner objets visibles
        for obj in visible_objects:
            if hasattr(obj, 'draw'):
                obj.draw(screen, self.camera)
            elif hasattr(obj, 'image') and hasattr(obj, 'rect'):
                screen.blit(obj.image, self.camera.apply(obj.rect))
        
        # Dessiner orbs non collectés
        for orb in self.orbs:
            if not orb.collected and query_rect.colliderect(orb.rect):
                orb.draw(screen, self.camera)
        
        # Dessiner joueur
        self.player.draw(screen, self.camera, self.respawn_invincibility > 0)
        
        # 🛠️ Vignettage rouge à la mort
        if self.death_fx_timer > 0:
            self._draw_death_vignette(screen)
    
    def _draw_parallax(self, screen, screen_width):
        for i, layer in enumerate(self.parallax_layers):
            speed = 0.3 * (i + 1)
            offset = int(self.camera.offset_x * speed) % screen_width
            screen.blit(layer, (-offset, 0))
            screen.blit(layer, (-offset + screen_width, 0))
    
    def _draw_progress_bar(self, screen):
        """Barre de progression minimaliste en haut de l'écran"""
        progress = min(1.0, self.camera.offset_x / self.level_end_x) if self.level_end_x > 0 else 0
        
        bar_width = 200
        bar_height = 6
        x = (self.screen_width - bar_width) // 2
        y = 15
        
        # Fond
        pygame.draw.rect(screen, (180, 180, 180), (x, y, bar_width, bar_height))
        # Progress
        pygame.draw.rect(screen, (0, 200, 255), (x, y, bar_width * progress, bar_height))
        # Bordure fine
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 1)
    
    def _draw_death_vignette(self, screen):
        """🛠️ Dessine un vignettage rouge léger quand on meurt"""
        vignette = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        # Alpha décroissant avec le timer (fade out)
        alpha = int(100 * (self.death_fx_timer / 0.3))
        vignette.fill((255, 50, 50, alpha))  # Rouge transparent
        screen.blit(vignette, (0, 0))