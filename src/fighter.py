import os
import pygame
from src.settings import GROUND_Y, PLAYER_ANIMATIONS
from src.spritesheet import load_animation_frames

class Fighter:
    def __init__(self, x, y, asset_dir):
        self.animations = {}
        for state, (filename, count, speed, loop) in PLAYER_ANIMATIONS.items():
            path = os.path.join(asset_dir, filename)
            self.animations[state] = {
                "frames": load_animation_frames(path, count, scale=3.2),
                "speed": speed,
                "loop": loop,
            }

        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 6.5
        self.jump_power = -16.0
        self.gravity = 0.85

        self.max_hp = 200
        self.hp = 200
        self.energy = 100

        self.facing = "right"
        self.state = "idle"
        self.frame_index = 0.0
        self.animation_finished = False
        self.on_ground = True

        self.is_attacking = False
        self.is_blocking = False
        self.block_timer = 0
        self.combo_step = 0
        self.queued_next_attack = False
        self.has_dealt_damage = False
        self.hurtbox = pygame.Rect(0, 0, 48, 80)

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0.0
            self.animation_finished = False
            self.has_dealt_damage = False

    def trigger_attack(self):
        if self.is_blocking or not self.on_ground or self.state in ("hurt", "death"):
            return
        if not self.is_attacking:
            self.is_attacking = True
            self.combo_step = 1
            self.set_state("attack1")
        elif self.combo_step < 3 and self.frame_index >= 3.0:
            self.queued_next_attack = True

    def get_attack_hitbox(self):
        if self.is_attacking and 3 <= int(self.frame_index) <= 5:
            reach = 85 if self.combo_step == 3 else 70
            offset_x = 25 if self.facing == "right" else -(25 + reach)
            return pygame.Rect(int(self.x + offset_x), int(self.y - 80), reach, 70)
        return None

    def handle_input(self, keys):
        if self.state in ("hurt", "death"):
            return

        wants_block = (keys[pygame.K_k] or keys[pygame.K_LSHIFT]) and self.on_ground and not self.is_attacking
        if wants_block:
            if not self.is_blocking:
                self.block_timer = 0
            self.is_blocking = True
            self.block_timer += 1
            self.vx = 0
            self.set_state("block")
            return
        else:
            self.is_blocking = False
            self.block_timer = 0

        if self.is_attacking:
            self.vx = 0
            return

        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.facing = "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.facing = "right"

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False
            self.set_state("jump_start")

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.hurtbox.midbottom = (int(self.x), int(self.y))

        if self.energy < 100:
            self.energy = min(100, self.energy + 0.12)

        if not self.on_ground:
            self.vy += self.gravity
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.vy = 0
                self.on_ground = True

        if not self.on_ground and not self.is_attacking:
            if self.vy < -3:
                self.set_state("jump_start")
            elif -3 <= self.vy <= 3:
                self.set_state("jump_transition")
            else:
                self.set_state("jump_fall")
        elif self.on_ground and not self.is_attacking and not self.is_blocking and self.state not in ("hurt", "death"):
            if abs(self.vx) > 0:
                self.set_state("run")
            else:
                self.set_state("idle")

        anim = self.animations[self.state]
        self.frame_index += anim["speed"]
        frames = anim["frames"][self.facing]

        if self.frame_index >= len(frames):
            if anim["loop"]:
                self.frame_index = 0.0
            else:
                self.frame_index = len(frames) - 1
                if not self.animation_finished:
                    self.animation_finished = True
                    self._on_animation_end()

    def _on_animation_end(self):
        if self.is_attacking:
            if self.queued_next_attack and self.combo_step < 3:
                self.combo_step += 1
                self.queued_next_attack = False
                self.set_state(f"attack{self.combo_step}")
            else:
                self.is_attacking = False
                self.combo_step = 0
                self.queued_next_attack = False
                self.set_state("idle")
        elif self.state == "hurt":
            self.set_state("idle")

    def draw(self, surface, camera_x):
        frames = self.animations[self.state]["frames"][self.facing]
        frame = frames[int(self.frame_index)]
        rect = frame.get_rect(midbottom=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect)