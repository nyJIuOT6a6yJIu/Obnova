# TODO:
#  ammo count, weapon drop, weapon pickup
#  during first game: change tooltips,
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
#  add oof deathsound
#  add zebra mask and dodge ability after nuke ending
#  introduce speed limit (so that game wont crush)

import math
import random

import pygame
from sys import exit

from scripts.color_sine import ColorSine
from scripts.player_sprite import Player, Mask, Weapon
from scripts.enemy_sprites import Fly, Snail

# TODO: implement shooting and aiming
# def enemy_shot(point, enemy_list: list):
#     shot = []
#     for i in enemy_list:
#         if i[0].collidepoint(point):
#             shot.append(i)
#     if shot:
#         return shot
#     else:
#         return None
#
# def aim_at_enemy(point, enemy_list: list):
#     for i in enemy_list:
#         if i[0].collidepoint(point):
#             return True
#     else:
#         return False

class Game(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Game, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((800, 400))

        self.load_images()

        pygame.display.set_caption('Obnova v0.0.0.2')
        pygame.display.set_icon(self.rooster_mask)

        # self.start_time = 0

        self.clock = pygame.time.Clock()
        self.pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)

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

        self.bg_music.set_volume(0.3)
        self.menu_music.set_volume(0.2)

        self.enemy_spawn_timer = pygame.USEREVENT + 1

        self.fresh_start = True
        self.set_up_game()
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

        self.snail_1       = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
        self.snail_2       = pygame.image.load('graphics/snail/snail2.png').convert_alpha()

    def load_sounds(self):
        self.gun_sound     = pygame.mixer.Sound('audio/gunshot.mp3')
        self.death_sound   = pygame.mixer.Sound('audio/death.mp3')
        self.death_sound_2 = pygame.mixer.Sound('audio/death2.mp3')

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

    def set_up_game(self):
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

        pygame.time.set_timer(self.enemy_spawn_timer, 1500)

        self.game_active = True
        self.menu_music.play(loops=-1, fade_ms=400)

        # TODO: restart music
        # bg_music.stop()
        # menu_music.stop()
        # bg_music.play(loops=-1, fade_ms=400)
        # TODO: restart game
        # start_time = pygame.time.get_ticks()
        # fresh_start = False

    def game_loop(self):
        while True:
            self.delta_time = (pygame.time.get_ticks() - self.last_time_frame)
            self.last_time_frame = pygame.time.get_ticks()

            self.event_loop()
            if self.game_active:
                self.runtime_frame()
            else:
                self.menu_frame()
            pygame.display.update()
            self.clock.tick(60)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if self.game_active:
                # players controls
                if event.type == pygame.KEYDOWN:
                    self.player_sprite.player_input(event.key, False)
                if event.type == pygame.KEYUP:
                    self.player_sprite.player_input(event.key, True)

                # enemy spawn
                if event.type == self.enemy_spawn_timer:
                    self.add_new_enemy(3, 1)

            if not self.game_active and event.type == pygame.KEYDOWN and event.key == pygame.K_y:
                self.set_up_game()

    def runtime_frame(self):
        # if fresh_start:
        #     gun_surf = pygame.Surface((1, 1))
        #     rooster_surf = pygame.Surface((1, 1))

        self.screen.blit(self.ground_surf, (0, 300))

        self.sky_color_surf.fill(self.sky_color.return_color())
        inc = self.delta_time*60/1000
        self.sky_color.increment(inc)

        self.screen.blit(self.sky_color_surf, (0, 0))
        self.screen.blit(self.sky_surf, (0, 0))

        score_surf = self.pixel_font.render(f'Score: {self.score}', True, (44, 44, 44))
        score_rect = score_surf.get_rect(center=(400, 50))
        self.screen.blit(score_surf, score_rect)

        self.player.update()
        self.player_attachments.update()
        self.player.draw(self.screen)
        self.player_attachments.draw(self.screen)

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        # lasersight
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

        self.game_active = self.enemy_collision()
        self.game_over()

    def menu_frame(self):
        self.screen.fill(self.sky_color.return_color())

        self.screen.blit(self.player_menu, self.player_menu_rect)

        score_line = f'You killed {self.score} enemies.'
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
        if not self.game_active:
            ds = random.choice([self.death_sound, self.death_sound_2])
            ds.play()
            self.sky_color.increment(50)
            self.bg_music.fadeout(1500)

    # def get_current_time(self):
    #     current_time = (pygame.time.get_ticks() - self.start_time)//1000
    #     return current_time

    def add_new_enemy(self, snail_relative_chance: int, fly_relative_chance: int):
        if random.randint(1, snail_relative_chance + fly_relative_chance) <= fly_relative_chance:
            a = Fly(self)
            a.rect.midbottom = (random.randint(810, 1010), 150)
            a.set_speed(v_x=-1 * random.randint(300, 540))
            self.enemy_group.add(a)
            del a
        else:
            a = Snail(self)
            a.rect.midbottom = (random.randint(810, 1010), 300)
            a.set_speed(v_x=-1 * random.randint(240, 480))
            self.enemy_group.add(a)
            del a

    def enemy_collision(self) -> bool:
        collisions = pygame.sprite.spritecollide(self.player_sprite, self.enemy_group, False)
        return not bool(collisions)


# TODO: add masks back
# dog_surf = pygame.transform.scale(pygame.image.load('graphics/snail/dog.png').convert_alpha(), (35, 45))
# dog_rect.bottomleft = (enemy.bottomleft[0] - 5, enemy.bottomleft[1])
# owl_surf = pygame.transform.scale(pygame.image.load('graphics/fly/owl.png').convert_alpha(), (35, 45))
# owl_rect.center = (enemy.center[0] - 5, enemy.center[1])

a = Game()

