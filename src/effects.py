import pygame


class HolyOrbCharge:
    def __init__(self, frames, duration=52):
        self.frames = frames
        self.duration = duration
        self.timer = 0
        self.x = 0.0
        self.y = 0.0
        self.max_scale = 4.5

    @property
    def complete(self):
        return self.timer >= self.duration

    def update(self, camera_x, screen_width, screen_height):
        self.x = camera_x + screen_width / 2
        self.y = screen_height / 2
        self.timer = min(self.duration, self.timer + 1)

    def _scale(self):
        grow_frames = 24
        hold_frames = 8
        shrink_frames = self.duration - grow_frames - hold_frames

        if self.timer <= grow_frames:
            progress = self.timer / grow_frames
            eased_progress = progress * progress * (3 - 2 * progress)
            return 0.5 + (self.max_scale - 0.5) * eased_progress
        if self.timer <= grow_frames + hold_frames:
            return self.max_scale

        progress = (self.timer - grow_frames - hold_frames) / shrink_frames
        eased_progress = progress * progress * (3 - 2 * progress)
        return self.max_scale * (1 - eased_progress)

    def draw(self, surface, camera_x):
        scale = self._scale()
        if scale <= 0.01:
            return
        frame = self.frames[int(self.timer / 4) % len(self.frames)]
        size = max(1, int(frame.get_width() * scale))
        frame = pygame.transform.scale(frame, (size, size))
        rect = frame.get_rect(center=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect, special_flags=pygame.BLEND_ADD)


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
    def __init__(self, x, y, frames, ground_y, fall_speed=8.0, gravity=0.85):
        self.x = float(x)
        self.y = float(y)
        self.frames = frames
        self.frame_index = 0.0
        self.ground_y = ground_y
        self.vy = fall_speed
        self.gravity = gravity
        self.alive = True

    def update(self):
        self.y += self.vy
        self.vy += self.gravity
        self.frame_index = (self.frame_index + 0.5) % len(self.frames)
        if self.y >= self.ground_y - 30:
            self.y = self.ground_y - 30
            self.alive = False
            return True
        return False

    def draw(self, surface, camera_x):
        if not self.alive:
            return

        frame = self.frames[int(self.frame_index)]
        rect = frame.get_rect(center=(int(self.x - camera_x), int(self.y)))
        surface.blit(frame, rect, special_flags=pygame.BLEND_ADD)


class HolyOrbImpact:
    def __init__(self, x, ground_y, frames, damage_radius=250, frame_speed=0.7):
        self.x = float(x)
        self.ground_y = ground_y
        self.frames = frames
        self.damage_radius = damage_radius
        self.frame_speed = frame_speed
        self.frame_index = 0.0
        self.alive = True

    def update(self):
        self.frame_index += self.frame_speed
        if self.frame_index >= len(self.frames):
            self.alive = False

    def draw(self, surface, camera_x):
        if not self.alive:
            return

        frame = pygame.transform.scale(self.frames[int(self.frame_index)], (512, 512))
        rect = frame.get_rect(midbottom=(int(self.x - camera_x), int(self.ground_y)))
        surface.blit(frame, rect, special_flags=pygame.BLEND_ADD)

        ring_progress = min(1.0, self.frame_index / 5)
        ring_radius = max(1, int(self.damage_radius * ring_progress))
        ring_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(
            ring_surface,
            (155, 225, 255, 180),
            (
                int(self.x - camera_x - ring_radius),
                int(self.ground_y - 30 - ring_radius * 0.22),
                ring_radius * 2,
                max(12, int(ring_radius * 0.44)),
            ),
            width=5,
        )
        surface.blit(ring_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        if self.frame_index < 2:
            flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash.fill((180, 230, 255, 45 - int(self.frame_index * 20)))
            surface.blit(flash, (0, 0))