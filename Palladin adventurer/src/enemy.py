import os
import random
import pygame
from src.spritesheet import load_grid_animations

class Enemy:
    def __init__(self, x, y, folder_path, config, max_hp=120):
        filepath = os.path.join(folder_path, config["file"])
        self.animations = load_grid_animations(
            filepath, config["rows"], config["cols"], config["animations"], config["scale"]
        )
        self.x = float(x)
        self.y = float(y)
        self.facing = "left"
        self.state = "idle"
        self.frame_index = 0.0

        self.max_hp = max_hp
        self.hp = max_hp
        self.speed = 2.8
        self.attack_range = 85
        self.attack_cooldown = 0
        self.has_dealt_damage = False
        self.stun_timer = 0

        self.hurtbox = pygame.Rect(0, 0, 55, 75)

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0
            self.has_dealt_damage = False

    def take_damage(self, amount, knockback_dir=0):
        if self.state == "death":
            return
        self.hp = max(0, self.hp - amount)
        self.x += knockback_dir * 18
        if self.hp == 0:
            self.set_state("death")
        else:
            self.set_state("hurt")

    def get_attack_hitbox(self):
        if self.state in ("attack1", "attack2") and 4 <= int(self.frame_index) <= 5:
            offset_x = 45 if self.facing == "right" else -95
            return pygame.Rect(int(self.x + offset_x), int(self.y - 75), 50, 65)
        return None

    def update(self, player):
        self.hurtbox.midbottom = (int(self.x), int(self.y))

        if self.state == "death":
            self._advance_frame()
            return

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.set_state("hurt")
            self._advance_frame()
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.state not in ("hurt", "attack1", "attack2"):
            dx = player.x - self.x
            self.facing = "right" if dx > 0 else "left"

            if abs(dx) > self.attack_range:
                self.x += self.speed if dx > 0 else -self.speed
                self.set_state("walk")
            elif self.attack_cooldown == 0 and player.state != "death":
                self.set_state(random.choice(["attack1", "attack2"]))
                self.attack_cooldown = 75
            else:
                self.set_state("idle")

        self._advance_frame()

    def _advance_frame(self):
        anim = self.animations[self.state]
        self.frame_index += anim["speed"]
        frames = anim["frames"][self.facing]

        if self.frame_index >= len(frames):
            if anim["loop"]:
                self.frame_index = 0.0
            else:
                self.frame_index = len(frames) - 1
                if self.state in ("attack1", "attack2", "hurt"):
                    self.set_state("idle")

    def draw(self, surface, camera_x):
        frames = self.animations[self.state]["frames"][self.facing]
        frame = frames[int(self.frame_index)]
        rect = frame.get_rect(midbottom=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect)

        if self.state != "death":
            bar_w = 54
            bar_x = int(self.x - camera_x - bar_w // 2)
            bar_y = rect.top + 25
            pygame.draw.rect(surface, (40, 10, 15), (bar_x, bar_y, bar_w, 6))
            hp_w = int(bar_w * (self.hp / self.max_hp))
            pygame.draw.rect(surface, (220, 45, 55), (bar_x, bar_y, hp_w, 6))