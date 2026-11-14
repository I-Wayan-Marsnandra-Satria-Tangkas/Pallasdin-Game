import os
import sys
import pygame
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GROUND_Y,
    ASSET_ROOT, DEMON_A_CONFIG, BLOOD_MONSTER_CONFIG
)
from src.background import ParallaxMap
from src.fighter import Fighter
from src.enemy import Enemy
from src.spritesheet import load_sequence_frames
from src.effects import HolyOrbProjectile, VisualEffect

def draw_hud(surface, player):
    # HP Bar
    pygame.draw.rect(surface, (30, 15, 20), (40, 35, 300, 22))
    hp_w = int(300 * (player.hp / player.max_hp))
    pygame.draw.rect(surface, (220, 50, 60), (40, 35, hp_w, 22))
    pygame.draw.rect(surface, (230, 230, 240), (40, 35, 300, 22), 2)

    # Energy Bar (untuk Holy Orb)
    pygame.draw.rect(surface, (20, 25, 45), (40, 64, 220, 14))
    en_w = int(220 * (player.energy / 100))
    pygame.draw.rect(surface, (245, 200, 65), (40, 64, en_w, 14))
    pygame.draw.rect(surface, (230, 230, 240), (40, 64, 220, 14), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Paladin Adventurer - Shadow Combat")
    clock = pygame.time.Clock()

    bg_map = ParallaxMap(os.path.join(ASSET_ROOT, "map"))
    player = Fighter(350, GROUND_Y, os.path.join(ASSET_ROOT, "player"))

    # Load efek Parry & Holy Orb
    parry_frames = load_sequence_frames(os.path.join(ASSET_ROOT, "Parry"), count=12, scale=0.65)
    orb_frames = load_sequence_frames(os.path.join(ASSET_ROOT, "effect_holy_orb"), count=12, scale=0.55)

    # Spawn kedua musuh untuk dites!
    enemies = [
        Enemy(850, GROUND_Y, os.path.join(ASSET_ROOT, "enemy_rawr"), DEMON_A_CONFIG, max_hp=120),
        Enemy(1150, GROUND_Y, os.path.join(ASSET_ROOT, "enemy_yaks"), BLOOD_MONSTER_CONFIG, max_hp=160),
    ]

    projectiles = []
    vfx_list = []
    camera_x = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    player.trigger_attack()
                elif event.key == pygame.K_l and player.energy >= 40:
                    # Skill L: Tembak Holy Orb!
                    player.energy -= 40
                    spawn_x = player.x + (55 if player.facing == "right" else -55)
                    projectiles.append(HolyOrbProjectile(spawn_x, player.y - 45, player.facing, orb_frames))

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Update & Cek Collision Proyektil Holy Orb
        for proj in projectiles:
            proj.update()
            for enemy in enemies:
                if proj.alive and enemy.state != "death" and proj.hitbox.colliderect(enemy.hurtbox):
                    kb = 1 if proj.vx > 0 else -1
                    enemy.take_damage(proj.damage, knockback_dir=kb)
                    vfx_list.append(VisualEffect(proj.x, proj.y, parry_frames))
                    proj.alive = False
        projectiles = [p for p in projectiles if p.alive]

        # Cek Pedang Player kena Musuh
        p_hitbox = player.get_attack_hitbox()
        if p_hitbox and not player.has_dealt_damage:
            for enemy in enemies:
                if enemy.state != "death" and p_hitbox.colliderect(enemy.hurtbox):
                    dmg = 25 if player.combo_step == 3 else 15
                    kb = 1 if player.facing == "right" else -1
                    enemy.take_damage(dmg, knockback_dir=kb)
                    player.has_dealt_damage = True
                    player.energy = min(100, player.energy + 12)

        # Update Musuh & Cek Serangan Musuh ke Player
        for enemy in enemies:
            enemy.update(player)
            e_hitbox = enemy.get_attack_hitbox()
            if e_hitbox and not enemy.has_dealt_damage and e_hitbox.colliderect(player.hurtbox):
                enemy.has_dealt_damage = True
                if player.is_blocking and player.block_timer <= 15:
                    # PERFECT PARRY!
                    enemy.stun_timer = 70
                    player.energy = min(100, player.energy + 30)
                    shield_x = player.x + (35 if player.facing == "right" else -35)
                    vfx_list.append(VisualEffect(shield_x, player.y - 45, parry_frames))
                elif player.is_blocking:
                    # Normal Block (damage berkurang drastis)
                    player.hp = max(0, player.hp - 3)
                else:
                    player.hp = max(0, player.hp - 15)
                    player.set_state("hurt" if player.hp > 0 else "death")

        for vfx in vfx_list:
            vfx.update()
        vfx_list = [v for v in vfx_list if v.alive]

        target_cam_x = player.x - SCREEN_WIDTH * 0.35
        camera_x += (target_cam_x - camera_x) * 0.1

        # Render Pipeline
        screen.fill((12, 16, 28))
        bg_map.draw(screen, camera_x, foreground=False)
        for enemy in enemies:
            enemy.draw(screen, camera_x)
        player.draw(screen, camera_x)
        for proj in projectiles:
            proj.draw(screen, camera_x)
        for vfx in vfx_list:
            vfx.draw(screen, camera_x)
        bg_map.draw(screen, camera_x, foreground=True)

        draw_hud(screen, player)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()