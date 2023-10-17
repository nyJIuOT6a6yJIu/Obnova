# TODO:
#  ammo count, weapon drop, weapon pickup
#  during first game: change tooltios,
#                     revert graphics,
#                     remove lasersight & shooting,
#                     remove animal masks and reduce stats to original
#  pacifist root - unlocks sralker teaser
#  nuke animation with poroshenko
#  and WASTED and 'pacan k uspehoo shol' on consequent plays
#  add transparent tooltips
#  add score and game timer
#  add more features for kills
#  add scaling if killrun

import math
import random

import pygame
from sys import exit

from scripts.color_sine import ColorSine

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.jumps = 1
        self.max_jumps = 1
        self.speed = [0, 0]
        self.a_pressed = False
        self.d_pressed = False  # Ну я ))))))

        self.walk_anim = [pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha(),
                          pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha(),
                          pygame.image.load('graphics/Player/jump.png').convert_alpha()]
        self.anim_index = 0

        self.rooster_mask = pygame.transform.scale(pygame.image.load('graphics/Player/rooster.png').convert_alpha(), (90, 95))
        self.rooster_rect = self.rooster_mask.get_rect()

        self.gun_ak = pygame.transform.scale(pygame.image.load('graphics/GUN.png').convert_alpha(), (120, 60))
        self.gun_ak_rect = self.gun_ak.get_rect()

        self.image = self.walk_anim[self.anim_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))

    def player_input(self, key_pressed, released=False):
        if self.jumps and (key_pressed == pygame.K_SPACE or key_pressed == pygame.K_w) and not released:
            self.speed[1] = -20
            self.jumps -= 1
        if key_pressed == pygame.K_a and not released:
            self.a_pressed = True
        elif key_pressed == pygame.K_a and released:
            self.a_pressed = False
        if key_pressed == pygame.K_d and not released:
            self.d_pressed = True
        if key_pressed == pygame.K_d and released:
            self.d_pressed = False
        if self.a_pressed or self.d_pressed:
            self.speed[0] = 5*bool(self.d_pressed) - 5*bool(self.a_pressed)

    def player_movement(self):
        gravity_acc = 1
        stiffness = 1

        self.rect.centerx += self.speed[0]
        self.rect.bottom += self.speed[1]
        self.speed[1] += gravity_acc

        if self.rect.bottom > 300:
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 780:
            self.rect.right = 780
        if self.speed[0]:
            if not (self.a_pressed or self.d_pressed):
                self.speed[0] -= (abs(stiffness)) * (self.speed[0] / (abs(self.speed[0])))

    def draw_attachments(self, mode=None):
        """
        mode = {'normal', 'no mask', 'no gun'}
        :param mode:
        :return:
        """

        if mode is None or 'normal' in mode:
            self.rooster_rect.center = (self.rect.midtop[0] + 7, self.rect.midtop[1] + 23)
            screen.blit(self.rooster_mask, self.rooster_rect)

            self.gun_ak_rect.midleft = (self.rect.left, self.rect.midleft[1] + 15)
            screen.blit(self.gun_ak, self.gun_ak_rect)

            return

        if 'no mask' in mode:
            pass
        else:
            self.rooster_rect.center = (self.rect.midtop[0] + 7, self.rect.midtop[1] + 23)
            screen.blit(self.rooster_mask, self.rooster_rect)
        if 'no gun' in mode:
            pass
        else:
            self.gun_ak_rect.midleft = (self.rect.left, self.rect.midleft[1] + 15)
            screen.blit(self.gun_ak, self.gun_ak_rect)

    def player_animate(self):
        if self.rect.bottom < 300:
            self.image = self.walk_anim[2]
        elif abs(self.speed[0]):
            self.anim_index += 0.15
            if self.anim_index >= 2:
                self.anim_index = 0
            self.image = self.walk_anim[int(self.anim_index)]
        else:
            self.anim_index = 0
            self.image = self.walk_anim[self.anim_index]

    def update(self):
        self.player_movement()
        self.draw_attachments()
        self.player_animate()


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

def enemy_shot(point, enemy_list: list):
    shot = []
    for i in enemy_list:
        if i[0].collidepoint(point):
            shot.append(i)
    if shot:
        return shot
    else:
        return None


def aim_at_enemy(point, enemy_list: list):
    for i in enemy_list:
        if i[0].collidepoint(point):
            return True
    else:
        return False


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

player = pygame.sprite.GroupSingle()
player_sprite = Player()
player.add(player_sprite)

game_name_surf = pixel_font.render('Hohline Cherkasy', True, 'Red')
color_surf = pygame.Surface((800, 300))
sky_surf = pygame.image.load('graphics/Sky_miami.png').convert_alpha()

ground_surf = pygame.image.load('graphics/ground.png').convert()

score = 0



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

player_stand_surf = pygame.transform.rotozoom(
    pygame.image.load('graphics/Player/player_stand.png').convert_alpha(), 0, 3)
player_stand_rect = player_stand_surf.get_rect(center=(179, 200))

player_speed = [0, 0]
player_jumps = 2
max_jumps = 1

# pygame.display.set_icon(_rooster_surf)  # TODO: add app icon

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
fresh_start = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == pygame.KEYDOWN:
                player_sprite.player_input(event.key, False)
            if event.type == pygame.KEYUP:
                player_sprite.player_input(event.key, True)

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
            # player_rect.midbottom = (80, 300)
            player_speed = [0, 0]
            max_jumps = 1
            player_jumps = max_jumps
            enemy_rect_list.clear()
            after_image = []
            bg_music.stop()
            menu_music.stop()
            bg_music.play(loops=-1, fade_ms=400)
            start_time = pygame.time.get_ticks()
            fresh_start = False
            game_active = True

    if not game_active:
        screen.fill(colorChange.return_color())

        screen.blit(player_stand_surf, player_stand_rect)

        score_line = f'You killed {score} enemies.'
        new_game_line = 'Press  Y to continue'
        if score == 0:
            score_line = ''
            new_game_line = 'Press Y key to start'

        final_score_surf = pixel_font.render(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(400, 200))
        new_game_surf = pixel_font.render(new_game_line, True, 'Red')
        new_game_rect = new_game_surf.get_rect(midleft=(400, 250))
        screen.blit(final_score_surf, final_score_rect)
        screen.blit(new_game_surf, new_game_rect)
        screen.blit(game_name_surf, (200, 40))
        colorChange.increment()

    else:
        # if fresh_start:
        #     gun_surf = pygame.Surface((1, 1))
        #     rooster_surf = pygame.Surface((1, 1))

        screen.blit(ground_surf, (0, 300))

        color = colorChange.return_color()
        color_surf.fill(color)

        screen.blit(color_surf, (0, 0))
        screen.blit(sky_surf, (0, 0))

        score_surf = pixel_font.render(f'Score: {score}', True, (44, 44, 44))
        score_rect = score_surf.get_rect(center=(400, 50))
        screen.blit(score_surf, score_rect)

        # player_rect, player_speed, player_jumps = player_movement(player_rect, player_speed, player_jumps, max_jumps)

        # player_surf, player_anim_index = player_animation(player_rect, player_surf, player_walk_anim, player_anim_index, player_speed[0])
        # screen.blit(player_surf, player_rect)
        player.draw(screen)
        player.update()

        # if not fresh_start and aim_at_enemy(pygame.mouse.get_pos(), enemy_rect_list):
        #     pygame.draw.line(screen, "Red", (gun_rect.midright[0]-30, gun_rect.midright[1]-3), pygame.mouse.get_pos(),
        #                      width=2)

        # for index, i in enumerate(after_image):
        #     if i[0] > 0:
        #         pygame.draw.line(screen, (255, 255, 100), (gun_rect.midright[0]-8, gun_rect.midright[1]-4), i[1],
        #                      width = int(6 * math.sin(i[0]*math.pi/8)))
        #         i[0] -= 1
        #     else:
        #         after_image.pop(index)

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
