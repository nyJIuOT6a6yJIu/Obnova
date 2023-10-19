# TODO:
#  ammo count, weapon drop, weapon pickup
#  - during first game: change tooltips,
#                     revert graphics,
#                     remove gun,
#                     remove animal masks and reduce stats to original
#  - pacifist root - unlocks sralker teaser
#  - nuke animation with poroshenko
#  and WASTED and 'pacan k uspe hoo shol' on consequent plays
#  add transparent tooltips
#  configure first run
#  (?) add game timer
#  - add zebra mask and dodge ability after nuke ending
#  - introduce speed limit (so that game wont crush)

import math
import random

import pygame
from sys import exit

from scripts.color_sine import ColorSine
from scripts.player_sprite import Player, Mask, Weapon
from scripts.enemy_sprites import Fly, Snail

from config.config import SCREEN_RESOLUTION,\
                          DISPLAY_CAPTION,\
                          GRAVITY_ACCELERATION,\
                          GROUND_STIFFNESS,\
                          ENEMY_SPAWN_INTERVAL_MS,\
                          ENEMY_PLACEMENT_RANGE,\
                          SNAIL_SPEED_RANGE,\
                          FLY_SPEED_RANGE

# 48px = 1 meter

class Game(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Game, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_RESOLUTION)

        self.load_images()

        pygame.display.set_caption(DISPLAY_CAPTION)
        pygame.display.set_icon(self.rooster_mask)

        # self.start_time = 0
        self.mouse = pygame.sprite.Sprite()
        self.mouse.image = pygame.Surface((2, 2))
        self.mouse.rect = pygame.Rect(0, 0, 2, 2)

        self.clock = pygame.time.Clock()
        self.pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)
        self.micro_pixel_font = pygame.font.Font('font/Pixeltype.ttf', 30)

        self.game_name_surf = self.pixel_font.render('Hohline Cherkasy', True, 'Red')

        self.sky_color_surf = pygame.Surface((800, 300))
        self.sky_color = ColorSine(phases=[math.pi * 0.5, math.pi * 0.7, 0],
                                   freqs=[1.1, 0.2, 1],
                                   statics=[0.5, 0.7, 0.7],
                                   ampls=[0.5, 0.3, 0.3])

        self.player_menu = pygame.transform.rotozoom(self.player_stand, 0, 3)
        self.player_menu_rect = self.player_menu.get_rect(center=(179, 200))

        self.load_sounds()
        self.current_track = None

        self.gun_sound.set_volume(1.1)
        self.death_sound.set_volume(1.3)
        self.death_sound_2.set_volume(1.3)
        self.death_sound_3.set_volume(5)

        self.bg_music.set_volume(0.3)
        self.menu_music.set_volume(0.2)

        self.enemy_spawn_timer = pygame.USEREVENT + 1

        self.set_up_game('first')  # TODO: cache check
        self.game_loop()

    def load_images(self):

        self.sky_surf      = pygame.image.load('graphics/Sky_miami.png').convert_alpha()
        self.ground_surf   = pygame.image.load('graphics/ground.png').convert()

        self.player_walk_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
        self.player_jump   = pygame.image.load('graphics/Player/jump.png').convert_alpha()

        self.player_stand  = pygame.image.load('graphics/Player/player_stand.png').convert_alpha()

        self.rooster_mask  = pygame.image.load('graphics/Player/rooster.png').convert_alpha()
        self.weapon        = pygame.image.load('graphics/GUN.png').convert_alpha()

        self.fly_1         = pygame.image.load('graphics/fly/Fly1.png').convert_alpha()
        self.fly_2         = pygame.image.load('graphics/fly/Fly2.png').convert_alpha()
        self.fly_mask      = pygame.image.load('graphics/fly/owl.png').convert_alpha()

        self.snail_1       = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
        self.snail_2       = pygame.image.load('graphics/snail/snail2.png').convert_alpha()
        self.snail_mask    = pygame.image.load('graphics/snail/dog.png').convert_alpha()

        self.oob_pointer   = pygame.image.load('graphics/oob_pointer.png').convert_alpha()

    def load_sounds(self):
        self.gun_sound     = pygame.mixer.Sound('audio/gunshot.mp3')
        self.death_sound   = pygame.mixer.Sound('audio/death.mp3')
        self.death_sound_2 = pygame.mixer.Sound('audio/death2.mp3')
        self.death_sound_3 = pygame.mixer.Sound('audio/death3.mp3')

        self.bg_music      = pygame.mixer.Sound('audio/miami.mp3')
        self.menu_music    = pygame.mixer.Sound('audio/menu.mp3')

# TODO: add music handler (maybe new class?)
    def music_play(self, new_music):
        if self.current_track:
            self.current_track.stop()
        self.current_track = new_music
        self.current_track.play(loops=-1, fade_ms=400)

    def music_stop(self):
        if self.current_track:
            self.current_track.stop()
        self.current_track = None

    def set_up_game(self, mode='default'):
        self.player = pygame.sprite.GroupSingle()
        self.player_sprite = Player(self)
        self.player.add(self.player_sprite)

        self.player_attachments = pygame.sprite.LayeredUpdates()

        self.mask_sprite = Mask(self.player_sprite)
        self.player_attachments.add(self.mask_sprite)

        self.gun_sprite = Weapon(self.player_sprite)
        self.player_attachments.add(self.gun_sprite)

        # player_attachments.change_layer(mask_sprite, 0)
        # player_attachments.change_layer(gun_sprite, 1)

        self.enemy_group = pygame.sprite.LayeredUpdates()
        self.enemy_attachments = pygame.sprite.LayeredUpdates()

        self.score = 0

        self.after_image = []

        self.delta_time = 0
        self.last_time_frame = pygame.time.get_ticks()
        self.last_rescale_score = None

        self.gravity_acceleration = GRAVITY_ACCELERATION
        self.ground_stiffness = GROUND_STIFFNESS

        self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS

        pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)

        self.enemy_placement_range = ENEMY_PLACEMENT_RANGE
        self.snail_speed_range = SNAIL_SPEED_RANGE
        self.fly_speed_range =  FLY_SPEED_RANGE

        self.game_state = 1  # -1 first time; -2 first menu; 0 - menu; 1 default game
        self.kill_run = False
        if mode == 'first':
            self.music_play(self.menu_music)
        elif mode == 'default':
            self.music_play(self.bg_music)

    def game_loop(self):
        while True:
            self.delta_time = (pygame.time.get_ticks() - self.last_time_frame)
            self.last_time_frame = pygame.time.get_ticks()

            self.event_loop()
            match self.game_state:
                case 1:
                    self.runtime_frame()
                case 0:
                    self.menu_frame()
            pygame.display.update()
            self.clock.tick(60)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if self.game_state in [-1, 1]:
                # players controls
                if event.type == pygame.KEYDOWN:
                    self.player_sprite.player_input(event.key, False)
                if event.type == pygame.KEYUP:
                    self.player_sprite.player_input(event.key, True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player_sprite.player_input(event.button, False)


                # enemy spawn
                if event.type == self.enemy_spawn_timer:
                    self.add_new_enemy(3, 1)
                    pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)


            if self.game_state in [-2, 0] and event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                self.set_up_game()

    def runtime_frame(self):
        # if fresh_start:
        #     gun_surf = pygame.Surface((1, 1))
        #     rooster_surf = pygame.Surface((1, 1))

        self.screen.blit(self.ground_surf, (0, 300))

        self.sky_color_surf.fill(self.sky_color.return_color())
        self.sky_color.increment(self.delta_time*60/1000)

        self.screen.blit(self.sky_color_surf, (0, 0))
        self.screen.blit(self.sky_surf, (0, 0))

        score_surf = self.pixel_font.render(f'Score: {min(self.score, 137)}', True, (44+200*bool(self.kill_run), 44, 44))
        score_rect = score_surf.get_rect(center=(400, 80))
        self.screen.blit(score_surf, score_rect)

        self.player.update()
        self.player_attachments.update()
        self.player.draw(self.screen)
        self.player_attachments.draw(self.screen)



        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        self.enemy_attachments.update()
        self.enemy_attachments.draw(self.screen)

        self.draw_laser_sight()
        self.draw_shot_after_image()
        self.draw_out_of_bounds_marker()

        self.difficulty_scaling()

        if self.enemy_collision():
            self.game_state = 0
        self.game_over()

    def menu_frame(self):
        self.screen.fill(self.sky_color.return_color())

        self.screen.blit(self.player_menu, self.player_menu_rect)

        score_line = f'Your score is {self.score}'
        new_game_line = 'Press  Y to continue'
        if self.score == 0:
            score_line = ''
            new_game_line = 'Press Y key to start'

        final_score_surf = self.pixel_font.render(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(400, 200))
        new_game_surf = self.pixel_font.render(new_game_line, True, 'Red')
        new_game_rect = new_game_surf.get_rect(midleft=(400, 250))
        self.screen.blit(final_score_surf, final_score_rect)
        self.screen.blit(new_game_surf, new_game_rect)
        self.screen.blit(self.game_name_surf, (200, 40))

        inc = self.delta_time*60/1000
        self.sky_color.increment(inc)

    def game_over(self):
        if self.game_state in [-2, 0]:
            ds = random.choice([self.death_sound, self.death_sound_2, self.death_sound_3])
            ds.play()
            self.sky_color.increment(50)
            self.bg_music.fadeout(1500)
            # print(self.player_sprite.rect.top - self.player_sprite.rect.bottom)

    def add_new_enemy(self, snail_relative_chance: int, fly_relative_chance: int):
        if random.randint(1, snail_relative_chance + fly_relative_chance) <= fly_relative_chance:
            a = Fly(self)
            a.rect.bottomleft = (random.randint(self.enemy_placement_range[0], self.enemy_placement_range[1]), 150)
            a.set_speed(v_x=-1 * random.randint(self.fly_speed_range[0], self.fly_speed_range[1]))
            self.enemy_group.add(a)
            del a
        else:
            a = Snail(self)
            a.rect.bottomleft = (random.randint(self.enemy_placement_range[0], self.enemy_placement_range[1]), 300)
            a.set_speed(v_x=-1 * random.randint(self.snail_speed_range[0], self.snail_speed_range[1]))
            self.enemy_group.add(a)
            del a

    def enemy_collision(self) -> bool:
        collisions = pygame.sprite.spritecollide(self.player_sprite, self.enemy_group, False)
        return bool(collisions)

    def aim_at_enemy(self):
        self.mouse.rect.center = pygame.mouse.get_pos()
        if pygame.sprite.spritecollide(self.mouse, self.enemy_group, False):
            return self.mouse.rect.center

    def draw_laser_sight(self):
        if self.player_sprite.weapon:
            enemy_pos = self.aim_at_enemy()
            if enemy_pos:
                start_pos = (self.gun_sprite.rect.right - 40, self.gun_sprite.rect.centery - 2)
                pygame.draw.line(self.screen, (240, 0, 0), start_pos, enemy_pos, 2)

    def shoot_at_enemy(self):
        self.mouse.rect.center = pygame.mouse.get_pos()
        return pygame.sprite.spritecollide(self.mouse, self.enemy_group, False)

    def draw_shot_after_image(self):
        for index, i in enumerate(self.after_image):
            if i[1] > 0.0:
                pygame.draw.line(self.screen, (255, 255, 100), (self.gun_sprite.rect.midright[0]-8, self.gun_sprite.rect.midright[1]-4), i[0],
                             width= int(6 * math.sin(i[1]*math.pi/100.0)))
                i[1] -= self.delta_time
            else:
                self.after_image.pop(index)

    def draw_out_of_bounds_marker(self):
        if self.player_sprite.rect.bottom < -10:
            oob_marker_surf = pygame.transform.scale(self.oob_pointer, (40, 20))
            oob_marker_rect = oob_marker_surf.get_rect(midtop=(self.player_sprite.rect.centerx, 5))

            oob_text_surf = self.micro_pixel_font.render(f'{-(self.player_sprite.rect.bottom - 10)//48}m', True, (237, 28, 36))
            oob_text_rect = oob_text_surf.get_rect(midtop=[oob_marker_rect.centerx, oob_marker_rect.bottom + 3])

            self.screen.blit(oob_marker_surf, oob_marker_rect)
            self.screen.blit(oob_text_surf, oob_text_rect)

    # def draw_tool_tips(self):

    def difficulty_scaling(self):  # TODO: ammo capacity, weapon spawn etc
        if self.kill_run and self.score != self.last_rescale_score:
            self.ground_stiffness = GROUND_STIFFNESS * (131 - self.score)/137

            self.player_sprite.max_jumps = 1 + self.score//30

            self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 7 * self.score
            self.enemy_placement_range = [ENEMY_PLACEMENT_RANGE[0], ENEMY_PLACEMENT_RANGE[1] - self.score]
            self.snail_speed_range = [SNAIL_SPEED_RANGE[0] + 50 + self.score, SNAIL_SPEED_RANGE[1] + 2*self.score]
            self.fly_speed_range = [FLY_SPEED_RANGE[0] + 50 + self.score, FLY_SPEED_RANGE[1] + 2*self.score]

            self.last_rescale_score = self.score

a = Game()

