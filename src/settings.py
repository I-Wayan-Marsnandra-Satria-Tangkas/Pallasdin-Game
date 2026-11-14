import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GROUND_Y = 635

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_ROOT = os.path.join(PROJECT_ROOT, "asset palladin game")

# --- PLAYER ---
PLAYER_ANIMATIONS = {
    "idle": ("IDLE.png", 14, 0.22, True),
    "walk": ("WALK.png", 8, 0.22, True),
    "run": ("RUN.png", 8, 0.28, True),
    "attack1": ("ATTACK 1.png", 8, 0.38, False),
    "attack2": ("ATTACK 2.png", 9, 0.38, False),
    "attack3": ("ATTACK 3.png", 11, 0.38, False),
    "block": ("BLOCK.png", 6, 0.25, False),
    "hurt": ("HURT.png", 8, 0.25, False),
    "death": ("DEATH.png", 15, 0.20, False),
    "jump_start": ("JUMP-START.png", 3, 0.30, False),
    "jump_transition": ("JUMP-TRANSITION.png", 3, 0.30, False),
    "jump_fall": ("JUMP-FALL.png", 3, 0.25, True),
}

# --- ENEMY GRID CONFIG (6 baris x 8 kolom) ---
DEMON_A_CONFIG = {
    "file": "Demon_A.png",
    "rows": 6,
    "cols": 8,
    "scale": 3.5,
    "animations": {
        "idle": (0, 6, 0.18, True),
        "walk": (1, 8, 0.22, True),
        "attack1": (2, 7, 0.28, False),
        "attack2": (3, 7, 0.28, False),
        "hurt": (4, 4, 0.22, False),
        "death": (5, 4, 0.15, False),
    },
}

BLOOD_MONSTER_CONFIG = {
    "file": "Blood Monster_A.png",
    "rows": 6,
    "cols": 8,
    "scale": 3.5,
    "animations": {
        "idle": (0, 6, 0.16, True),
        "walk": (1, 8, 0.20, True),
        "attack1": (2, 8, 0.26, False),
        "attack2": (3, 8, 0.26, False),
        "hurt": (4, 4, 0.22, False),
        "death": (5, 4, 0.15, False),
    },
}

# --- MAP 12 LAYERS (Belakang ke Depan) ---
MAP_LAYERS = [
    ("Layer_0011_0.png", 0.00, False),
    ("Layer_0010_1.png", 0.02, False),
    ("Layer_0009_2.png", 0.05, False),
    ("Layer_0008_3.png", 0.12, False),
    ("Layer_0007_Lights.png", 0.18, True),
    ("Layer_0006_4.png", 0.28, False),
    ("Layer_0005_5.png", 0.42, False),
    ("Layer_0004_Lights.png", 0.50, True),
    ("Layer_0003_6.png", 0.65, False),
    ("Layer_0002_7.png", 0.80, False),
    ("Layer_0001_8.png", 1.00, False),
    ("Layer_0000_9.png", 1.25, False),
]
