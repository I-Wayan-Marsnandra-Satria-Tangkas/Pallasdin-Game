import pygame

class VisualEffect:
    def __init__(self, x, y, frames, speed=0.45):
        self.x = x
        self.y = y
        self.frames = frames
        self.speed = speed
        self.frame_index = 0.0
        self.alive = True

    def update(self):
        self.frame_index += self.speed
        if self.frame_index >= len(self.frames):
            self.alive = False

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        frame = self.frames[int(self.frame_index)]
        rect = frame.get_rect(center=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect, special_flags=pygame.BLEND_ADD)

class HolyOrbProjectile:
    def __init__(self, x, y, facing, frames, speed=11.0, damage=35):
        self.x = float(x)
        self.y = float(y)
        self.facing = facing
        self.vx = speed if facing == "right" else -speed
        self.frames = frames
        self.frame_index = 0.0
        self.damage = damage
        self.alive = True
        self.distance_traveled = 0.0
        self.hitbox = pygame.Rect(0, 0, 50, 50)

    def update(self):
        self.x += self.vx
        self.distance_traveled += abs(self.vx)
        self.frame_index = (self.frame_index + 0.35) % len(self.frames)
        self.hitbox.center = (int(self.x), int(self.y))

        if self.distance_traveled > 900:
            self.alive = False

    def draw(self, surface, camera_x):
        if not self.alive:
            return
        frame = self.frames[int(self.frame_index)]
        rect = frame.get_rect(center=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect, special_flags=pygame.BLEND_ADD)