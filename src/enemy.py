import os
import random
import pygame
from src.spritesheet import load_grid_animations


class Enemy:
    def __init__(self, x, y, folder_path=None, config=None, max_hp=120, animations=None, is_boss=False):
        if animations is None:
            filepath = os.path.join(folder_path, config["file"])
            animations = load_grid_animations(
                filepath, config["rows"], config["cols"], config["animations"], config["scale"]
            )
        self.x = float(x)
        self.y = float(y)
        self.facing = "left"
        self.state = "idle"
        self.frame_index = 0.0

        self.max_hp = max_hp
        self.hp = max_hp
        self.is_boss = is_boss
        self.cc_resistance = 0.8 if is_boss else 0.0
        self.animations = animations
        self.speed = 2.5 if is_boss else 2.8
        self.attack_range = 150 if is_boss else 85
        self.attack_cooldown = 60 if is_boss else 0
        self.has_dealt_damage = False
        self.stun_timer = 0
        self.death_finished = False

        self.hurtbox = pygame.Rect(0, 0, 110 if is_boss else 55, 140 if is_boss else 75)

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0
            self.has_dealt_damage = False

    def take_damage(self, amount, knockback_dir=0):
        if self.state == "death":
            return
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.set_state("death")
        elif not self.is_boss or random.random() >= self.cc_resistance:
            self.x += knockback_dir * (18 if not self.is_boss else 28)
            self.set_state("hurt")

    def get_attack_hitbox(self):
        if self.is_boss:
            if self.state == "attack1" and 8 <= int(self.frame_index) <= 11:
                if self.facing == "right":
                    return pygame.Rect(int(self.x + 25), int(self.y - 125), 150, 110)
                return pygame.Rect(int(self.x - 175), int(self.y - 125), 150, 110)
            return None

        if self.state in ("attack1", "attack2") and 4 <= int(self.frame_index) <= 5:
            offset_x = 45 if self.facing == "right" else -95
            return pygame.Rect(int(self.x + offset_x), int(self.y - 75), 50, 65)
        return None

    def update(self, player):
        self.hurtbox.midbottom = (int(self.x), int(self.y))

        if self.state == "death":
            self._advance_frame()
            return

        dx = player.x - self.x
        self.facing = "right" if dx > 0 else "left"

        if self.stun_timer > 0:
            self.stun_timer -= 1
            self.set_state("hurt")
            self._advance_frame()
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.state not in ("hurt", "attack1", "attack2"):
            if abs(dx) > self.attack_range:
                self.x += self.speed if dx > 0 else -self.speed
                self.set_state("walk")
            elif self.attack_cooldown == 0 and player.state != "death":
                attack = "attack1" if self.is_boss else random.choice(["attack1", "attack2"])
                self.set_state(attack)
                self.attack_cooldown = 100 if self.is_boss else 75
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
                elif self.state == "death":
                    self.death_finished = True

    def draw(self, surface, camera_x):
        frames = self.animations[self.state]["frames"][self.facing]
        frame = frames[int(self.frame_index)]
        rect = frame.get_rect(midbottom=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect)

        if not self.is_boss and self.state != "death":
            bar_w = 54
            bar_x = int(self.x - camera_x - bar_w // 2)
            bar_y = rect.top + 25
            bar_h = 6
            pygame.draw.rect(surface, (40, 10, 15), (bar_x, bar_y, bar_w, bar_h))
            hp_w = int(bar_w * (self.hp / self.max_hp))
            pygame.draw.rect(surface, (220, 45, 55), (bar_x, bar_y, hp_w, bar_h))


class DemonSlimeBoss(Enemy):
    def __init__(self, x, y, asset_root, max_hp=500):
        animation_root = os.path.join(asset_root, "individual sprites")
        animation_specs = {
            "idle": ("01_demon_idle", "demon_idle", 0.16, True),
            "walk": ("02_demon_walk", "demon_walk", 0.34, True),
            "attack1": ("03_demon_cleave", "demon_cleave", 0.38, False),
            "hurt": ("04_demon_take_hit", "demon_take_hit", 0.3, False),
            "death": ("05_demon_death", "demon_death", 0.22, False),
        }
        animations = {}
        for state, (folder, prefix, speed, loop) in animation_specs.items():
            path = os.path.join(animation_root, folder)
            filenames = [
                filename for filename in os.listdir(path)
                if filename.lower().endswith(".png") and filename.startswith(f"{prefix}_")
            ]
            filenames.sort(key=lambda name: int(os.path.splitext(name)[0].rsplit("_", 1)[1]))
            frames_right = []
            frames_left = []
            for filename in filenames:
                image = pygame.image.load(os.path.join(path, filename)).convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * 2.4), int(image.get_height() * 2.4)))
                frames_right.append(image)
                frames_left.append(pygame.transform.flip(image, True, False))
            animations[state] = {
                "frames": {"right": frames_right, "left": frames_left},
                "speed": speed,
                "loop": loop,
            }

        animations["attack2"] = animations["attack1"]
        super().__init__(x, y, max_hp=max_hp, animations=animations, is_boss=True)