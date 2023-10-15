import pygame
from sys import exit
from scripts.color_sine import ColorSine
import math
import random


def display_current_time():
    current_time = (pygame.time.get_ticks() - start_time)//1000
    return current_time
    # score_surf = pixel_font.render(f'{current_time}', True, (64, 64, 64))
    # score_rect = score_surf.get_rect(center=(400, 50))


def enemy_update(enemy_list):
    for enemy, enemy_speed, enemy_type in enemy_list:
        enemy.left -= enemy_speed
        if enemy_type == 'snail':
            screen.blit(snail_surf, enemy)
            dog_rect = dog_surf.get_rect()
            dog_rect.bottomleft = (enemy.bottomleft[0]-5, enemy.bottomleft[1])
            screen.blit(dog_surf, dog_rect)
        elif enemy_type == 'fly':
            screen.blit(fly_surf, enemy)
            owl_rect = owl_surf.get_rect()
            owl_rect.center = (enemy.center[0]-5, enemy.center[1])
            screen.blit(owl_surf, owl_rect)
    enemy_list = [enemy for enemy in enemy_list if enemy[0].right >= 0]
    return enemy_list


def enemy_collision(player: pygame.Rect, enemy_list: list) -> bool:
    for enemy in enemy_list:
        if player.colliderect(enemy[0]):
            return False
    return True

def player_animation(player, surface, animation, index, speed):
    if player.bottom < 300:
        return animation[2], 0
    elif abs(speed):
        index += 0.15
        if index >= 2:
            index = 0
        return animation[int(index)], index
    else:
        return animation[0], 0

def player_movement(player, speed, jumps, m_jumps):
    gravity_acc = 1
    stiffness = 1

    player.centerx += speed[0]
    player.bottom += speed[1]
    speed[1] += gravity_acc

    if player.bottom > 300:
        player.bottom = 300
        speed[1] = 0
        jumps = m_jumps
    if player.left < 0:
        player.left = 0
    elif player.right > 780:
        player.right = 780
    if speed[0]:
        speed[0] -= (abs(stiffness)) * (speed[0] / (abs(speed[0])))

    return player, speed, jumps


pygame.init()
start_time = 0
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Obnova v0.0.0.1')
clock = pygame.time.Clock()
pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)

colorChange = ColorSine(phases= [math.pi*0.5, math.pi*0.7, 0],
                        freqs = [1.1, 0.2, 1],
                        statics=[0.5, 0.7, 0.7],
                        ampls = [0.5, 0.3, 0.3])



game_name_surf = pixel_font.render('Hohline Cherkasy', True, 'Red')
color_surf = pygame.Surface((800, 300))
sky_surf = pygame.image.load('graphics/Sky_miami.png').convert_alpha()

ground_surf = pygame.image.load('graphics/ground.png').convert()

score = 0
# score_surf = pixel_font.render(f'Score: {score}', True, (64, 64, 64))
# score_rect = score_surf.get_rect(center=(400, 50))

snail_1_surf = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
snail_2_surf = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
snail_anim = [snail_1_surf, snail_2_surf]
snail_anim_index = 0
snail_surf = snail_1_surf

dog_surf = pygame.transform.scale(pygame.image.load('graphics/snail/dog.png').convert_alpha(), (35, 45))

fly_1_surf = pygame.image.load('graphics/fly/Fly1.png').convert_alpha()
fly_2_surf = pygame.image.load('graphics/fly/Fly2.png').convert_alpha()
fly_anim = [fly_1_surf, fly_2_surf]
fly_anim_index = 0
fly_surf = fly_1_surf

owl_surf = pygame.transform.scale(pygame.image.load('graphics/fly/owl.png').convert_alpha(), (35, 45))

enemy_rect_list = []

player_walk_1_surf = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
player_walk_2_surf = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
player_jump_surf = pygame.image.load('graphics/Player/jump.png').convert_alpha()
player_walk_anim = [player_walk_1_surf, player_walk_2_surf, player_jump_surf]
player_anim_index = 0


player_surf = player_walk_1_surf

player_rect = player_surf.get_rect(midbottom=(80, 300))

player_stand_surf = pygame.transform.rotozoom(
    pygame.image.load('graphics/Player/player_stand.png').convert_alpha(), 0, 3)
player_stand_rect = player_stand_surf.get_rect(center=(179, 200))

player_speed = [0, 0]
player_jumps = 2
max_jumps = 1

rooster_surf = pygame.transform.scale(pygame.image.load('graphics/Player/rooster.png').convert_alpha(), (90, 95))
rooster_rect = rooster_surf.get_rect(center=player_rect.midtop)

pygame.display.set_icon(rooster_surf)

gun_surf = pygame.transform.scale(pygame.image.load('graphics/GUN.png').convert_alpha(), (120, 60))
gun_rect = gun_surf.get_rect(midleft=(player_rect.left, player_rect.midleft[1]+15))

after_image = []

gun_sound = pygame.mixer.Sound('audio/gunshot.mp3')
gun_sound.set_volume(1.1)

death_sound = pygame.mixer.Sound('audio/death.mp3')
death_sound.set_volume((1.3))

death_sound_2 = pygame.mixer.Sound('audio/death2.mp3')
death_sound_2.set_volume((1.3))

bg_music = pygame.mixer.Sound('audio/miami.mp3')
bg_music.set_volume(0.3)

menu_music = pygame.mixer.Sound('audio/menu.mp3')
menu_music.set_volume(0.2)
menu_music.play(loops=-1, fade_ms=400)

enemy_spawn_timer = pygame.USEREVENT + 1
pygame.time.set_timer(enemy_spawn_timer, 1500)

snail_anim_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_anim_timer, 300)

fly_anim_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_anim_timer, 200)

game_active = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == pygame.KEYDOWN:
                if player_jumps and (event.key == pygame.K_SPACE or event.key == pygame.K_w):
                    player_speed[1] = -20
                    player_jumps -= 1

            if event.type == enemy_spawn_timer:
                if random.randint(1, 4) == 1:
                    enemy_rect_list.append((fly_surf.get_rect(midbottom=(random.randint(810, 1010), 150)),
                                            random.randint(5, 9), 'fly'))
                else:
                    enemy_rect_list.append((snail_surf.get_rect(midbottom=(random.randint(810, 1010), 300)),
                                        random.randint(4, 8), 'snail'))
            if event.type == snail_anim_timer:
                snail_anim_index = 1 - snail_anim_index
                snail_surf = snail_anim[snail_anim_index]
            if event.type == fly_anim_timer:
                fly_anim_index = 1 - fly_anim_index
                fly_surf = fly_anim[fly_anim_index]

        if not game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_y:
            score = 0
            colorChange = ColorSine(phases=[math.pi * 0.5, math.pi * 0.7, 0],
                                    freqs=[1.1, 0.2, 1],
                                    statics=[0.5, 0.7, 0.7],
                                    ampls=[0.5, 0.3, 0.3])
            player_rect.midbottom = (80, 300)
            player_speed = [0, 0]
            max_jumps = 1
            player_jumps = max_jumps
            enemy_rect_list.clear()
            after_image = []
            bg_music.stop()
            menu_music.stop()
            bg_music.play(loops=-1, fade_ms=400)
            start_time = pygame.time.get_ticks()
            game_active = True

    if not game_active:
        screen.fill(colorChange.return_color())

        screen.blit(player_stand_surf, player_stand_rect)

        score_line = f'You killed {score} zombie snail-dogs.'
        new_game_line = 'Press  Y to continue'
        if score == 0:
            score_line = 'Press Y key to start'
            new_game_line = ''

        final_score_surf = pixel_font.render(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(400, 200))
        new_game_surf = pixel_font.render(new_game_line, True, 'Red')
        new_game_rect = new_game_surf.get_rect(center=(400, 250))
        screen.blit(final_score_surf, final_score_rect)
        screen.blit(new_game_surf, new_game_rect)
        screen.blit(game_name_surf, (200, 40))
        colorChange.increment()

    else:
        if pygame.key.get_pressed()[pygame.K_a]:
            player_speed[0] = -5
        elif pygame.key.get_pressed()[pygame.K_d]:
            player_speed[0] = 5
        screen.blit(ground_surf, (0, 300))

        color = colorChange.return_color()
        color_surf.fill(color)

        screen.blit(color_surf, (0, 0))
        screen.blit(sky_surf, (0, 0))

        score_surf = pixel_font.render(f'Score: {score}', True, (44, 44, 44))
        score_rect = score_surf.get_rect(center=(400, 50))
        screen.blit(score_surf, score_rect)

        player_rect, player_speed, player_jumps = player_movement(player_rect, player_speed, player_jumps, max_jumps)

        player_surf, player_anim_index = player_animation(player_rect, player_surf, player_walk_anim, player_anim_index, player_speed[0])
        screen.blit(player_surf, player_rect)
        rooster_rect.center=(player_rect.midtop[0]+7, player_rect.midtop[1]+23)
        screen.blit(rooster_surf, rooster_rect)
        gun_rect.midleft = (player_rect.left, player_rect.midleft[1] + 15)
        screen.blit(gun_surf, gun_rect)

        # if snail_rect.collidepoint(pygame.mouse.get_pos()):
        #     pygame.draw.line(screen, "Red", (gun_rect.midright[0]-30, gun_rect.midright[1]-3), pygame.mouse.get_pos(),
        #                      width=2)

        for index, i in enumerate(after_image):
            if i[0] > 0:
                pygame.draw.line(screen, (255, 255, 100), (gun_rect.midright[0]-8, gun_rect.midright[1]-4), i[1],
                             width = int(6 * math.sin(i[0]*math.pi/8)))
                i[0] -= 1
            else:
                after_image.pop(index)

        # game_active = enemy_collision(player_rect, enemy_rect_list)

        if not game_active:
            ds = random.choice([death_sound, death_sound_2])
            ds.play()
            colorChange.increment(50)
            bg_music.fadeout(1500)
            continue

        enemy_rect_list = enemy_update(enemy_list=enemy_rect_list)

        colorChange.increment()

    # in the end
    # it doesn't even matter
    pygame.display.update()
    clock.tick(60)
