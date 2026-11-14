import os
import pygame

def load_animation_frames(filepath, frame_count, scale=3.2):
    sheet = pygame.image.load(filepath).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    frame_w = sheet_w // frame_count

    # Cari batas piksel terbawah (telapak kaki) dari keseluruhan sheet
    max_foot_y = 0
    for i in range(frame_count):
        rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
        frame = sheet.subsurface(rect)
        bbox = frame.get_bounding_rect()
        if bbox.height > 0 and bbox.bottom > max_foot_y:
            max_foot_y = bbox.bottom

    frames_right, frames_left = [], []
    for i in range(frame_count):
        rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
        # Potong bagian kosong di bawah telapak kaki!
        crop_h = max_foot_y if max_foot_y > 0 else sheet_h
        cropped = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, crop_h))

        new_size = (int(frame_w * scale), int(crop_h * scale))
        scaled = pygame.transform.scale(cropped, new_size)
        frames_right.append(scaled)
        frames_left.append(pygame.transform.flip(scaled, True, False))

    return {"right": frames_right, "left": frames_left}

def load_grid_animations(filepath, rows, cols, anim_map, scale=3.5):
    sheet = pygame.image.load(filepath).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    cell_w = sheet_w // cols
    cell_h = sheet_h // rows

    animations = {}
    for state, (row_idx, count, speed, loop) in anim_map.items():
        # Cari posisi kaki terbawah di baris animasi ini
        max_foot_y = 0
        for col_idx in range(count):
            frame = sheet.subsurface(pygame.Rect(col_idx * cell_w, row_idx * cell_h, cell_w, cell_h))
            bbox = frame.get_bounding_rect()
            if bbox.height > 0 and bbox.bottom > max_foot_y:
                max_foot_y = bbox.bottom

        crop_h = max_foot_y if max_foot_y > 0 else cell_h
        frames_right, frames_left = [], []
        for col_idx in range(count):
            cropped = sheet.subsurface(pygame.Rect(col_idx * cell_w, row_idx * cell_h, cell_w, crop_h))
            new_size = (int(cell_w * scale), int(crop_h * scale))
            scaled = pygame.transform.scale(cropped, new_size)
            frames_right.append(scaled)
            frames_left.append(pygame.transform.flip(scaled, True, False))

        animations[state] = {
            "frames": {"right": frames_right, "left": frames_left},
            "speed": speed,
            "loop": loop,
        }
    return animations

def load_sequence_frames(folder_path, count=12, scale=0.6):
    frames = []
    for i in range(count):
        filename = f"frame{i:04d}.png"
        path = os.path.join(folder_path, filename)
        img = pygame.image.load(path).convert()
        new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
        frames.append(pygame.transform.scale(img, new_size))
    return frames