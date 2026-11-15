import os
import random
import sys
import pygame
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GROUND_Y,
    ASSET_ROOT, PROJECT_ROOT, DEMON_A_CONFIG, BLOOD_MONSTER_CONFIG
)
from src.background import ParallaxMap
from src.fighter import Fighter
from src.enemy import DemonSlimeBoss, Enemy
from src.spritesheet import load_sequence_frames
from src.effects import HolyOrbCharge, HolyOrbImpact, HolyOrbProjectile, VisualEffect

def draw_hud(surface, player, regular_kills, boss_spawned, font, boss=None):
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

    objective = "BOSS FIGHT" if boss_spawned else f"DEMON SLIME: {regular_kills}/13"
    surface.blit(font.render(objective, True, (235, 230, 245)), (40, 90))

    if boss is not None and boss.state != "death":
        bar_width = 460
        bar_height = 22
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        name = font.render("DEMON LORD", True, (255, 225, 180))
        surface.blit(name, name.get_rect(midbottom=(SCREEN_WIDTH // 2, 31)))
        pygame.draw.rect(surface, (20, 12, 18), (bar_x - 3, 35, bar_width + 6, bar_height + 6))
        pygame.draw.rect(surface, (65, 24, 35), (bar_x, 38, bar_width, bar_height))
        hp_width = int(bar_width * (boss.hp / boss.max_hp))
        if hp_width:
            pygame.draw.rect(surface, (220, 45, 55), (bar_x, 38, hp_width, bar_height))
        pygame.draw.rect(surface, (255, 220, 180), (bar_x, 38, bar_width, bar_height), 2)


def show_ending(screen, image, duration_ms=8500):
    image_ratio = image.get_width() / image.get_height()
    screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    if image_ratio > screen_ratio:
            size = (SCREEN_WIDTH, int(SCREEN_WIDTH / image_ratio))
    else:
            size = (int(SCREEN_HEIGHT * image_ratio), SCREEN_HEIGHT)
    image = pygame.transform.smoothscale(image, size)
    image_rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.fill((0, 0, 0))
    screen.blit(image, image_rect)
    pygame.display.flip()

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration_ms:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            clock.tick(FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Paladin Adventurer - Shadow Combat")
    clock = pygame.time.Clock()
    hud_font = pygame.font.Font(None, 24)
    win_image = pygame.image.load(os.path.join(ASSET_ROOT, "win condition.jpeg")).convert()
    lose_image = pygame.image.load(os.path.join(ASSET_ROOT, "lose.jpg")).convert()

    bg_map = ParallaxMap(os.path.join(ASSET_ROOT, "map"))
    player = Fighter(350, GROUND_Y, os.path.join(ASSET_ROOT, "player"))

    # Load efek Parry & Holy Orb
    parry_frames = load_sequence_frames(os.path.join(ASSET_ROOT, "Parry"), count=12, scale=0.65)
    orb_frames = load_sequence_frames(os.path.join(ASSET_ROOT, "effect_holy_orb"), count=12, scale=0.8)
    impact_frames = load_sequence_frames(
        os.path.join(ASSET_ROOT, "after_effect_holly_orb"), count=12, scale=1.0
    )

    # Spawn kedua musuh untuk dites!
    enemies = [
        Enemy(850, GROUND_Y, os.path.join(ASSET_ROOT, "enemy_rawr"), DEMON_A_CONFIG, max_hp=60),
        Enemy(1150, GROUND_Y, os.path.join(ASSET_ROOT, "enemy_yaks"), BLOOD_MONSTER_CONFIG, max_hp=80),
    ]
    enemy_types = [
        ("enemy_rawr", DEMON_A_CONFIG, 60),
        ("enemy_yaks", BLOOD_MONSTER_CONFIG, 80),
    ]

    projectiles = []
    vfx_list = []
    impact_effects = []
    charge_effect = None
    screen_shake = 0
    hitstop_frames = 0
    camera_lock_x = None
    regular_kills = 0
    boss_spawned = False
    boss = None
    ending_image = None
    spawn_timer = FPS * 3
    camera_x = 0.0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if hitstop_frames == 0 and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    player.trigger_attack()
                elif event.key == pygame.K_l and player.energy >= 80 and charge_effect is None:
                    player.energy -= 80
                    charge_effect = HolyOrbCharge(orb_frames)
                    camera_lock_x = camera_x

        if hitstop_frames > 0:
            hitstop_frames -= 1
            pygame.display.flip()
            clock.tick(FPS)
            continue

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        if charge_effect is not None:
            charge_effect.update(camera_x, SCREEN_WIDTH, SCREEN_HEIGHT)
            if charge_effect.complete:
                impact_x = camera_x + SCREEN_WIDTH / 2
                projectiles.append(
                    HolyOrbProjectile(
                        impact_x,
                        -40,
                        orb_frames,
                        GROUND_Y,
                    )
                )
                charge_effect = None

        # Holy Orb ultimate falls to the ground, then deals one area hit.
        for proj in projectiles:
            if proj.update():
                impact = HolyOrbImpact(
                    proj.x,
                    GROUND_Y,
                    impact_frames,
                    damage_radius=SCREEN_WIDTH / 2,
                )
                impact_effects.append(impact)
                screen_shake = 24
                for enemy in enemies:
                    if enemy.state != "death":
                        knockback_dir = 1 if enemy.x >= impact.x else -1
                        damage = 100 if enemy.is_boss else enemy.max_hp * 2
                        enemy.take_damage(damage, knockback_dir=knockback_dir)
                        if enemy.is_boss:
                            hitstop_frames = max(hitstop_frames, 6)
        projectiles = [p for p in projectiles if p.alive]

        for impact in impact_effects:
            impact.update()
        impact_effects = [impact for impact in impact_effects if impact.alive]
        screen_shake = max(0, screen_shake - 1)
        if charge_effect is None and not projectiles and not impact_effects:
            camera_lock_x = None

        # Cek Pedang Player kena Musuh
        p_hitbox = player.get_attack_hitbox()
        if p_hitbox and not player.has_dealt_damage:
            for enemy in enemies:
                if enemy.state != "death" and p_hitbox.colliderect(enemy.hurtbox):
                    dmg = 25 if player.combo_step == 3 else 15
                    kb = 1 if player.facing == "right" else -1
                    enemy.take_damage(dmg, knockback_dir=kb)
                    if enemy.is_boss:
                        hitstop_frames = max(hitstop_frames, 4)
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
                    damage = 25 if enemy.is_boss else 15
                    player.hp = max(0, player.hp - damage)
                    player.set_state("hurt" if player.hp > 0 else "death")

        regular_kills += sum(
            enemy.death_finished and not enemy.is_boss
            for enemy in enemies
        )
        enemies = [enemy for enemy in enemies if not enemy.death_finished]

        if regular_kills >= 13 and not boss_spawned:
            boss_x = max(player.x + 650, camera_x + SCREEN_WIDTH + 100)
            boss = DemonSlimeBoss(
                boss_x,
                GROUND_Y,
                os.path.join(PROJECT_ROOT, "boss_demon_slime"),
                max_hp=500,
            )
            enemies.append(boss)
            boss_spawned = True
            spawn_timer = 0

        spawn_timer -= 1
        living_enemies = sum(enemy.state != "death" for enemy in enemies)
        if not boss_spawned and spawn_timer <= 0 and living_enemies < 4:
            folder, config, max_hp = random.choice(enemy_types)
            spawn_x = max(player.x + 850, camera_x + SCREEN_WIDTH + 100)
            enemies.append(
                Enemy(
                    spawn_x,
                    GROUND_Y,
                    os.path.join(ASSET_ROOT, folder),
                    config,
                    max_hp=max_hp,
                )
            )
            spawn_timer = FPS * 3
        elif not boss_spawned and spawn_timer <= 0:
            spawn_timer = FPS

        for vfx in vfx_list:
            vfx.update()
        vfx_list = [v for v in vfx_list if v.alive]

        if camera_lock_x is not None:
            camera_x = camera_lock_x
        else:
            target_cam_x = player.x - SCREEN_WIDTH * 0.35
            camera_x += (target_cam_x - camera_x) * 0.1

        if player.state == "death" and player.animation_finished:
            ending_image = lose_image
        elif boss is not None and boss.death_finished:
            ending_image = win_image

        # Render Pipeline
        world_surface.fill((12, 16, 28))
        bg_map.draw(world_surface, camera_x, foreground=False)
        for enemy in enemies:
            enemy.draw(world_surface, camera_x)
        player.draw(world_surface, camera_x)
        if charge_effect is not None:
            charge_effect.draw(world_surface, camera_x)
        for proj in projectiles:
            proj.draw(world_surface, camera_x)
        for vfx in vfx_list:
            vfx.draw(world_surface, camera_x)
        for impact in impact_effects:
            impact.draw(world_surface, camera_x)
        bg_map.draw(world_surface, camera_x, foreground=True)

        screen.fill((12, 16, 28))
        if screen_shake:
            shake_x = random.randint(-screen_shake, screen_shake)
            shake_y = random.randint(-screen_shake, screen_shake)
        else:
            shake_x = shake_y = 0
        screen.blit(world_surface, (shake_x, shake_y))
        boss = next((enemy for enemy in enemies if enemy.is_boss), None)
        draw_hud(screen, player, regular_kills, boss_spawned, hud_font, boss)
        pygame.display.flip()
        if ending_image is not None:
            show_ending(screen, ending_image)
            pygame.quit()
            return
        clock.tick(FPS)

if __name__ == "__main__":
    main()