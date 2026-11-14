import os
import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_LAYERS

class ParallaxMap:
    def __init__(self, asset_dir):
        self.layers = []
        for filename, speed, is_light in MAP_LAYERS:
            path = os.path.join(asset_dir, filename)
            img = pygame.image.load(path).convert_alpha()
            
            scale_ratio = SCREEN_HEIGHT / img.get_height()
            new_w = int(img.get_width() * scale_ratio)
            img = pygame.transform.scale(img, (new_w, SCREEN_HEIGHT))
            
            if is_light:
                img.set_alpha(110)
                
            self.layers.append({
                "image": img,
                "speed": speed,
                "is_light": is_light,
                "width": new_w,
            })

    def draw(self, surface, camera_x, foreground=False):
        target_layers = [l for l in self.layers if (l["speed"] > 1.0) == foreground]
        
        for layer in target_layers:
            w = layer["width"]
            rel_x = -(camera_x * layer["speed"]) % w
            blend = pygame.BLEND_ADD if layer["is_light"] else 0

            surface.blit(layer["image"], (rel_x - w, 0), special_flags=blend)
            surface.blit(layer["image"], (rel_x, 0), special_flags=blend)
            if rel_x + w < SCREEN_WIDTH:
                surface.blit(layer["image"], (rel_x + w, 0), special_flags=blend)