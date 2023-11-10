# TODO:
#  .
#  - nuke animation with poroshenko (pacifist ending)
#  - add post nuke credits
#  .
#  - (?) add more patterns for enemies (enter the sand man): frogs (snail) are slower but jump/lunge discard weapon on contact)
#  .
#  - (?) add enviromental hazards (enter the sand man)
#  - (?) freeze pickup (розібратись з мікшером, щоб ставити музику на паузу)
#  .
#  - add zebra mask and dodge ability after nuke ending (fun&games)
#  - add tiger mask and kick/throw ability after pacifist run (new wave hookers)
#  - add white-black bad apple after tiger run
#  - add frog mask (all masks effects, but only on Wednesdays)
#  - add sralker after bad apple run
#  .
#  - introduce speed limit (so that game wont crush)

import math
import random
from enum import Enum, auto

import pygame

from src.scripts.color_sine import ColorSine
from src.scripts.abs_color import ColorAbs

from src.scripts.player_sprite import Player, Mask, Weapon
from src.scripts.fly_sprite import Fly, Bat
from src.scripts.snail_sprite import Snail, Cham

from src.config.config import DISPLAY_CAPTION,\
                              GRAVITY_ACCELERATION,\
                              GROUND_STIFFNESS,\
                              ENEMY_SPAWN_INTERVAL_MS,\
                              ENEMY_PLACEMENT_RANGE,\
                              FLY_Y_RANGE,\
                              SNAIL_SPEED_RANGE,\
                              FLY_SPEED_RANGE,\
                              MAX_AMMO_CAPACITY,\
                              PICKUP_DROP_RATE


class MusicHandler:

    def __init__(self):
        self.current_track = None
        self.IsPaused = False

    def music_play(self, new_music):
        # pygame.mixer_music.unload()
        # pygame.mixer_music.load(new_music)
        # pygame.mixer_music.play(-1, fade_ms=400)
        if self.current_track:
            self.current_track.stop()
        self.current_track = new_music
        self.current_track.play(loops=-1, fade_ms=400)

    def music_stop(self, fadeout=None):
        if self.current_track:

            if fadeout is None:
                self.current_track.stop()
                # pygame.mixer_music.stop()
            else:
                # pygame.mixer_music.fadeout(fadeout)
                self.current_track.fadeout(fadeout)

            # pygame.mixer_music.unload()

            self.current_track = None

    # def music_toggle(self):
    #     if self.current_track is None:
    #         return
    #     if self.IsPaused:
    #         # self.current_track.unpause()
    #         pygame.mixer_music.unpause()
    #         self.IsPaused = False
    #     else:
    #         # self.current_track.pause()
    #         pygame.mixer_music.pause()
    #         self.IsPaused = True


class HMGame(object):
    # 48px = 1 meter

    class GameState(Enum):
        EXIT         = auto()

        FIRST_GAME   = auto()
        FIRST_MENU   = auto()

        DEFAULT_GAME = auto()
        BEAR_GAME    = auto()
        ZEBRA_GAME   = auto()

        DEFAULT_MENU = auto()

        NUKE_START   = auto()
        NUKE_CREDITS = auto()
        NUKE_MENU    = auto()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(HMGame, cls).__new__(cls)
        return cls.instance

    def __init__(self, screen, progress=None):

        if progress is None:
            progress = dict()
        self.progress = progress

        self.screen = screen

        pygame.init()

    def start_game(self):

        self.load_images()

        pygame.display.set_caption(DISPLAY_CAPTION)
        pygame.display.set_icon(self.rooster_mask)

        # self.start_time = 0
        self.mouse = pygame.sprite.Sprite()
        self.mouse.image = pygame.Surface((2, 2))
        self.mouse.rect = pygame.Rect(0, 0, 2, 2)

        self.clock = pygame.time.Clock()
        self.main_font = 'src/font/Pixeltype.ttf'
        # self.pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)
        # self.micro_pixel_font = pygame.font.Font('font/Pixeltype.ttf', 30)

        self.game_name_surf = self.text_to_surface_mf('Hohline Cherkasy', True, 'Red')

        self.sky_color_surf = pygame.Surface((800, 250))
        self.sky_color_foreground = pygame.Surface((800, 400))
        self.sky_color = ColorSine(phases= [math.pi * 0.5, math.pi * 0.7, 0.0],
                                   freqs=  [1.1,           0.2,           1.0],
                                   statics=[0.5,           0.7,           0.7],
                                   ampls=  [0.5,           0.3,           0.3])

        self.player_menu = pygame.transform.rotozoom(self.player_stand, 0, 3)
        self.player_menu_rect = self.player_menu.get_rect(center=(179, 200))
        self.wasted_surf = self.text_to_surface_mf('[REDACTED]', True, 'White', 'Black', 48)
        self.wasted_rect = self.wasted_surf.get_rect(center=(179, 181))

        self.screen.blit(pygame.image.load('src/graphics/loading_2.png'), (0, 0))
        pygame.display.update()

        self.load_sounds()

        self.music_handler = MusicHandler()

        self.gun_sound.set_volume(1.1)
        self.empty_gun_sound.set_volume(1.1)
        self.gun_pickup_sound.set_volume(0.8)

        self.kill_run_init_sound.set_volume(1.5)
        self.death_sound.set_volume(1.3)
        self.death_sound_2.set_volume(1.3)
        self.death_sound_3.set_volume(6)
        self.death_sound_4.set_volume(1.3)

        self.run_music_1.set_volume(0.3)
        self.bear_music.set_volume(0.4)
        self.zebra_music.set_volume(0.4)
        self.menu_music.set_volume(0.2)
        self.enter_the_sandman_music.set_volume(0.8)
        self.nuke_music.set_volume(1.0)
        self.post_nuke_music.set_volume(0.6)

        self.enemy_spawn_timer = pygame.USEREVENT + 1

        self.score = -1
        self.delta_time = 1

        if not self.progress:
            self.set_up_game('first')
        else:
            self.game_state = self.GameState.DEFAULT_MENU
            self.music_handler.music_play(self.menu_music)

        return self.game_loop()

    def load_images(self):

        self.normal_sky_surf = pygame.image.load('src/graphics/Sky.png').convert_alpha()

        self.sky_surf        = pygame.image.load('src/graphics/Sky_miami.png').convert_alpha()
        self.ground_surf     = pygame.image.load('src/graphics/ground.png').convert()
        self.wojaks          = pygame.image.load('src/graphics/wojaks.png').convert_alpha()
        self.nuke_menu_palms = pygame.image.load('src/graphics/palms_bg.png').convert_alpha()

        self.player_walk_1 = pygame.image.load('src/graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('src/graphics/Player/player_walk_2.png').convert_alpha()
        self.player_jump   = pygame.image.load('src/graphics/Player/jump.png').convert_alpha()

        self.player_stand = pygame.image.load('src/graphics/Player/player_stand.png').convert_alpha()

        self.rooster_mask = pygame.image.load('src/graphics/Player/rooster.png').convert_alpha()

        self.bear_mask   = pygame.image.load('src/graphics/Player/bear.png').convert_alpha()
        self.bear_banner = pygame.image.load('src/graphics/do_you_know_this_man.png').convert()

        self.zebra_mask = pygame.image.load('src/graphics/Player/zebra.png').convert_alpha()

        self.weapon   = pygame.image.load('src/graphics/GUN.png').convert_alpha()
        self.ammo     = pygame.transform.scale(pygame.image.load('src/graphics/ammo.png').convert_alpha(), (50, 50))
        self.jump_on  = pygame.transform.scale(pygame.image.load('src/graphics/jump_on.png').convert_alpha(), (50, 50))
        self.jump_off = pygame.transform.scale(pygame.image.load('src/graphics/jump_off.png').convert_alpha(), (50, 50))

        self.fly_1    = pygame.image.load('src/graphics/fly/Fly1.png').convert_alpha()
        self.fly_2    = pygame.image.load('src/graphics/fly/Fly2.png').convert_alpha()
        self.fly_mask = pygame.image.load('src/graphics/fly/owl.png').convert_alpha()
        self.bat_mask = pygame.image.load('src/graphics/fly/bat.png').convert_alpha()

        self.snail_1    = pygame.image.load('src/graphics/snail/snail1.png').convert_alpha()
        self.snail_2    = pygame.image.load('src/graphics/snail/snail2.png').convert_alpha()
        self.snail_mask = pygame.image.load('src/graphics/snail/dog.png').convert_alpha()
        self.cham_1     = pygame.image.load('src/graphics/snail/cham1.png').convert_alpha()
        self.cham_2     = pygame.image.load('src/graphics/snail/cham2.png').convert_alpha()
        self.cham_mask  = pygame.image.load('src/graphics/snail/cham.png').convert_alpha()

        self.oob_pointer = pygame.image.load('src/graphics/oob_pointer.png').convert_alpha()

    def load_sounds(self):
        self.death_sound     = pygame.mixer.Sound('src/audio/death sounds/death.mp3')
        self.death_sound_2   = pygame.mixer.Sound('src/audio/death sounds/death2.mp3')
        self.death_sound_3   = pygame.mixer.Sound('src/audio/death sounds/death3.mp3')
        self.death_sound_4   = pygame.mixer.Sound('src/audio/death sounds/death4.mp3')

        self.menu_music      = pygame.mixer.Sound('src/audio/menu music/menu.mp3')
        self.post_nuke_music = pygame.mixer.Sound('src/audio/menu music/post_nuke_menu.mp3')

        self.screen.blit(pygame.image.load('src/graphics/loading_3.png'), (0, 0))
        pygame.display.update()

        self.run_music_1 = pygame.mixer.Sound('src/audio/run music/run_music1.mp3')
        self.bear_music  = pygame.mixer.Sound('src/audio/run music/bear_run_music.mp3')
        self.zebra_music = pygame.mixer.Sound('src/audio/run music/zebra_run_music.mp3')

        self.enter_the_sandman_music = pygame.mixer.Sound('src/audio/boss music/enter_the_sandman.mp3')

        self.nuke_music      = pygame.mixer.Sound('src/audio/misc music/nuke.mp3')

        self.gun_sound           = pygame.mixer.Sound('src/audio/misc sounds/gunshot.mp3')
        self.empty_gun_sound     = pygame.mixer.Sound('src/audio/misc sounds/empty_gun.mp3')
        self.gun_pickup_sound    = pygame.mixer.Sound('src/audio/misc sounds/gun_pickup.mp3')
        self.kill_run_init_sound = pygame.mixer.Sound('src/audio/misc sounds/kill_run_init.mp3')

    def set_up_game(self, mode='rooster'):
        self.max_ammo = MAX_AMMO_CAPACITY
        self.pickup_rate = PICKUP_DROP_RATE  # percentage chance
        self.pickups = pygame.sprite.LayeredUpdates()

        self.player = pygame.sprite.GroupSingle()
        self.player_sprite = Player(self)
        self.player.add(self.player_sprite)

        self.player_attachments = pygame.sprite.LayeredUpdates()

        self.mask_sprite = Mask(self.player_sprite, mode)
        self.player_attachments.add(self.mask_sprite)

        if mode == 'first':
            self.enemy_spawn = [None, None, 'snail', 'snail', 'fly', 'snail', None]
            self.player_sprite.set_attachments(False)

        else:#if mode == 'rooster':
            self.enemy_spawn = []
            self.player_sprite.pick_up_weapon(Weapon(self))

        # player_attachments.change_layer(mask_sprite, 0)

        self.enemy_group = pygame.sprite.LayeredUpdates()
        self.enemy_attachments = pygame.sprite.LayeredUpdates()

        self.score = 0

        self.gunshot_afterimage = []

        if mode in ['rooster', 'bear', 'zebra']:
            self.jump_tip = self.text_to_surface_mf('SPACE/W to Jump', True, '#5d5d5d', size=32)
            self.move_tip = self.text_to_surface_mf('A/D to Move', True, '#5d5d5d', size=32)
            self.shoot_tup = self.text_to_surface_mf('LMB to Shoot', True, '#5d5d5d', size=32)
            self.pickup_tip = self.text_to_surface_mf('RMB to Drop', True, '#5d5d5d', size=32)
            self.dash_tip = self.text_to_surface_mf('SHIFT to Dash', True, '#5d5d5d', size=32)
        elif mode == 'first':
            self.jump_tip = self.text_to_surface_mf('SPACE to Jump', True, '#4d4d4d', size=35)
            self.move_tip = self.text_to_surface_mf('', True, '#5d5d5d', size=32)
            self.shoot_tup = self.text_to_surface_mf('', True, '#5d5d5d', size=32)
            self.pickup_tip = self.text_to_surface_mf('', True, '#5d5d5d', size=32)

        self.delta_time = 0
        self.last_time_frame = pygame.time.get_ticks()
        self.last_rescale_score = None

        self.gravity_acceleration = GRAVITY_ACCELERATION
        self.ground_stiffness = GROUND_STIFFNESS

        self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS

        pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)

        self.enemy_placement_range = ENEMY_PLACEMENT_RANGE
        self.fly_y_range = FLY_Y_RANGE
        self.snail_speed_range = SNAIL_SPEED_RANGE
        self.fly_speed_range =  FLY_SPEED_RANGE

        self.game_state = {'first': self.GameState.FIRST_GAME,
                           'rooster': self.GameState.DEFAULT_GAME,
                           'bear': self.GameState.BEAR_GAME,
                           'zebra': self.GameState.ZEBRA_GAME}[mode]
        self.advanced_enemies = False
        self.sky_is_over = False  # Even though we can't afford
        self.sky_color_surf.set_alpha(255)
        self.ground_surf.set_alpha(255)
        self.sky_color_foreground.set_alpha(0)
        self.kill_run = False

        if mode == 'first':
            self.music_handler.music_play(self.menu_music)
        elif mode == 'rooster':
            self.music_handler.music_play(self.run_music_1)
        elif mode == 'bear':
            self.music_handler.music_play(self.bear_music)
        elif mode == 'zebra':
            self.music_handler.music_play(self.zebra_music)

    def game_loop(self):
        while self.game_state != self.GameState.EXIT:
            self.last_time_frame = pygame.time.get_ticks()
            self.event_loop()
            match self.game_state:
                case self.GameState.NUKE_START:
                    self.nuke_animation()
                case self.GameState.NUKE_CREDITS:
                    self.post_nuke_credits()
                case self.GameState.NUKE_MENU:
                    self.menu_frame_nuke()
                case self.GameState.DEFAULT_GAME | self.GameState.BEAR_GAME | self.GameState.ZEBRA_GAME:
                    self.runtime_frame()
                case self.GameState.DEFAULT_MENU:
                    self.menu_frame()
                case self.GameState.FIRST_GAME:
                    self.runtime_frame('first')
                case self.GameState.FIRST_MENU:
                    self.menu_frame_first()
            if self.game_state != self.GameState.EXIT:
                pygame.display.update()
                self.clock.tick(60)
                self.delta_time = (pygame.time.get_ticks() - self.last_time_frame)
        return self.progress

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.game_state = self.GameState.EXIT
                # exit()
            if self.game_state in [self.GameState.FIRST_GAME,
                                   self.GameState.DEFAULT_GAME,
                                   self.GameState.BEAR_GAME,
                                   self.GameState.ZEBRA_GAME]:
                # players controls

                if event.type == pygame.KEYDOWN:
                    self.player_sprite.player_input(event.key, False)
                if event.type == pygame.KEYUP:
                    self.player_sprite.player_input(event.key, True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player_sprite.player_input(event.button, False)


                # enemy spawn
                if event.type == self.enemy_spawn_timer:
                    if self.enemy_spawn:
                        next_enemy = self.enemy_spawn.pop(0)
                        if next_enemy == 'snail':
                            self.add_new_enemy(1, 0)
                        elif next_enemy == 'fly':
                            self.add_new_enemy(0, 1)
                    else:
                        self.add_new_enemy(3, 1)
                    pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)


            elif self.game_state in [self.GameState.FIRST_MENU, self.GameState.DEFAULT_MENU, self.GameState.NUKE_MENU] \
                    and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    self.set_up_game()
                elif self.progress.get('bear', False) and event.key == pygame.K_b:
                    self.set_up_game('bear')
                elif self.progress.get('zebra', True) and event.key == pygame.K_z:  # TODO: swap True for False
                    self.set_up_game('zebra')

            elif self.game_state == self.GameState.NUKE_CREDITS and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                self.game_state = self.GameState.NUKE_MENU
                _color = self.sky_color.return_color()
                _color = (pygame.math.clamp(_color[0], 179, 229),
                          pygame.math.clamp(_color[1], 77, 229),
                          pygame.math.clamp(_color[2], 0, 204))
                self.sky_color = ColorSine(phases=[0.0, math.pi * 0.4, math.pi * 0.5],
                                           freqs=[0.1, 0.6, 0.7],
                                           statics=[0.8, 0.6, 0.4],
                                           ampls=[0.1, 0.3, 0.4])
                self.sky_color.convert_from_abs(_color)
                self.music_handler.music_play(self.post_nuke_music)

    def runtime_frame(self, mode='rooster'):
        sky_color = self.sky_color.return_color()
        inc = self.delta_time * 60 / 1000
        if not self.sky_is_over:
            self.sky_color_surf.fill(sky_color)
        else:
            self.sky_color_foreground.fill(sky_color)
            inc = inc * 2
        self.sky_color.increment(inc)
        self.screen.blit(self.ground_surf, (0, 300))

        if mode == 'first':
            self.screen.blit(self.normal_sky_surf, (0, 0))
        else: #if mode == 'rooster':
            if not self.sky_is_over:
                self.screen.blit(self.sky_color_surf, (0, 0))
                self.screen.blit(self.sky_surf, (0, 0))

        score_surf = self.text_to_surface_mf(f'Score: {int(min(self.score, 137))}', True, (44+200*bool(self.kill_run or int(self.score) >= 110),
                                                                                      44+200*bool(not self.kill_run and int(self.score) >= 110),
                                                                                      44))
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

        self.pickups.update()
        self.pickups.draw(self.screen)

        self.draw_laser_sight()
        self.draw_shot_after_image()
        self.draw_out_of_bounds_marker()
        self.draw_tool_tips()
        self.draw_ammo_count()
        self.draw_jumps_count()
        self.draw_spec_abilities()

        self.difficulty_scaling()
        self.enter_the_sandman()

        if self.score >= 137:
            self.game_state = self.GameState.NUKE_START
            self.music_handler.music_stop(1050)
            _color = self.sky_color.return_color()
            self.sky_color = ColorAbs(_color)
            self.screen.blit(self.ground_surf, (0, 300))
            self.animation_time = pygame.time.get_ticks()

            return

        if self.enemy_collision():
            if self.mask_sprite.deflect:
                self.mask_sprite.deflect = False
                self.mask_sprite.deflect_ability()
            else:
                if self.game_state in [self.GameState.DEFAULT_GAME, self.GameState.BEAR_GAME, self.GameState.ZEBRA_GAME]:
                    self.game_state = self.GameState.DEFAULT_MENU
                elif self.game_state == self.GameState.FIRST_GAME:
                    self.game_state = self.GameState.FIRST_MENU
        self.game_over()

        if self.sky_is_over:
            self.sky_color_foreground.set_alpha(int(self.score)-50)
            self.ground_surf.set_alpha(max(365 - 3*int(self.score), 50))
            self.screen.blit(self.sky_color_foreground, (0, 0))

    def menu_frame(self):
        self.screen.fill(self.sky_color.return_color())

        self.screen.blit(self.player_menu, self.player_menu_rect)
        self.screen.blit(self.wasted_surf, self.wasted_rect)

        score_line = f'Your score is {int(self.score)}'
        rooster_game_line = 'Press Y to continue'
        bear_game_line = ''  # TODO: add zebra
        if int(self.score) <= 0:
            score_line = ''
            rooster_game_line = 'Press Y key to start'
        elif int(self.score) >= 110 and int(self.score) < 137:
            rooster_game_line = 'Pacan k uspehoo shol (Y)'
        if self.progress.get('bear', False):
            bear_game_line = 'Press B to bear the unbearable'

        final_score_surf = self.text_to_surface_mf(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(380, 100))
        rooster_game_surf = self.text_to_surface_mf(rooster_game_line, True, 'Red')
        rooster_game_rect = rooster_game_surf.get_rect(midleft=(410, 250))
        bear_game_surf = self.text_to_surface_mf(bear_game_line, True, 'Red')
        bear_game_surf.set_alpha(120)
        self.screen.blit(final_score_surf, final_score_rect)
        self.screen.blit(rooster_game_surf, rooster_game_rect)
        self.screen.blit(bear_game_surf, (50, 350))
        self.screen.blit(self.game_name_surf, (200, 40))

        inc = self.delta_time * 60 / 1000
        self.sky_color.increment(inc)

    def menu_frame_first(self):
        self.screen.fill((125, 130, 230))
        self.screen.blit(self.player_menu, self.player_menu_rect)

        score_line = f'Your score is {int(self.score)}'
        new_game_line = 'Press Y to kill the bastards'
        if int(self.score) == 0:
            score_line = ''
            new_game_line = 'Press Y key to start'

        elif int(self.score) >= 110 and int(self.score) < 137:
            new_game_line = 'Pacan k uspehoo shol (Y)'

        final_score_surf = self.text_to_surface_mf(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(400, 200))
        new_game_surf = self.text_to_surface_mf(new_game_line, True, 'Red')
        new_game_rect = new_game_surf.get_rect(midleft=(380, 250))
        self.screen.blit(final_score_surf, final_score_rect)
        self.screen.blit(new_game_surf, new_game_rect)
        self.screen.blit(self.game_name_surf, (200, 40))

    def menu_frame_nuke(self):
        _color = self.sky_color.return_color()
        _alpha = max(_color[0] - 170, 5)
        self.nuke_menu_palms.set_alpha(_alpha)

        self.screen.fill(_color)
        self.screen.blit(self.nuke_menu_palms, (0, 0))

        new_game_line = 'Press Y to start again'
        new_game_surf = self.text_to_surface_mf(new_game_line, True, 'Red')
        new_game_rect = new_game_surf.get_rect(midleft=(400, 250))

        self.screen.blit(new_game_surf, new_game_rect)
        self.screen.blit(self.game_name_surf, (200, 40))

        inc = self.delta_time * 60 / 2000
        self.sky_color.increment(inc)

    def nuke_animation(self):
        time_pass_ms = pygame.time.get_ticks() - self.animation_time
        if time_pass_ms < 2000:
            a = self.sky_color.settle_for((117, 194, 246), 2, time_pass_ms)
        else:
            a = True
        sky_color = self.sky_color.return_color()
        self.sky_color_surf.fill(sky_color)
        self.screen.blit(self.sky_color_surf, (0, 0))

        if a is True and self.advanced_enemies: # this will happen only once
            self.advanced_enemies = False
            self.sky_color_foreground.fill('White')
            self.music_handler.music_play(self.nuke_music)

        if a is True:
            if time_pass_ms > 5700:
                radius = -20 + 145 * round(math.log(time_pass_ms/1000 - 4.7, 10.3), 2)
            else:
                radius = 0
            pygame.draw.circle(self.screen, 'White', (365, 170), radius, draw_top_right=True, draw_top_left=True, draw_bottom_left=True)
            self.screen.blit(self.ground_surf, (0, 300))
        self.screen.blit(self.sky_surf, (0, 0))

        score_surf = self.text_to_surface_mf(f'Score: {int(min(self.score, 137))}', True,
                                             (44 + 200 * bool(self.kill_run or int(self.score) >= 110),
                                              44 + 200 * bool(not self.kill_run and int(self.score) >= 110),
                                              44))
        if time_pass_ms < 2000:
            score_alpha = 255 - 255 * time_pass_ms // 2000
            score_surf.set_alpha(score_alpha)
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

        self.pickups.draw(self.screen)

        if time_pass_ms < 850:
            alpha_ = 127 - 127 * time_pass_ms // 850
            self.sky_color_foreground.set_alpha(alpha_)

            self.screen.blit(self.sky_color_foreground, (0, -100))
        if time_pass_ms > 10000:# and time_pass_ms < 18000:
            alpha_ = 255 * (time_pass_ms - 10000) // 8000
            w_alpha_ = 70 * (time_pass_ms - 10000) // 4000
            self.sky_color_foreground.set_alpha(alpha_)
            self.wojaks.set_alpha(w_alpha_)
            self.screen.blit(self.ground_surf, (0, 300))
            self.screen.blit(self.wojaks, (0, 0))
            self.screen.blit(self.sky_color_foreground, (0, 0))

        if time_pass_ms > 18700:
            self.game_state = self.GameState.NUKE_CREDITS
            self.advanced_enemies = True
            self.sky_color = ColorAbs((255, 255, 255))
            self.animation_time = pygame.time.get_ticks()

    def post_nuke_credits(self):
        time_pass_ms = pygame.time.get_ticks() - self.animation_time
        a = False
        if time_pass_ms < 4000:
            self.sky_color.settle_for((238, 95, 17), 4, time_pass_ms)
        elif time_pass_ms < 5600:
            self.sky_color.starting_color = (238, 95, 17)
            self.sky_color.settle_for((225, 177, 0), 1.6, time_pass_ms - 4000)
        else:
            self.sky_color.starting_color = None
            a = True
        if a and self.advanced_enemies:
            self.advanced_enemies = False
            _color = self.sky_color.return_color()
            self.sky_color = ColorSine(phases=[0.0, 0.0, 0.0],
                                       freqs=[0.1, 0.6, 0.7],
                                       statics=[0.8, 0.6, 0.5],
                                       ampls=[0.1, 0.3, 0.5])
            self.sky_color.convert_from_abs(_color)

        if not a:
            self.screen.fill(self.sky_color.return_color())
        if a:
            self.screen.fill(self.sky_color.return_color())
            inc = self.delta_time * 60 / 2000
            self.sky_color.increment(inc)

        if time_pass_ms > 230300:
            self.game_state = self.GameState.NUKE_MENU
            self.sky_color.red, self.sky_color.green, self.sky_color.blue = 0, 0, 0
            self.music_handler.music_play(self.post_nuke_music)
        #  random credit generation

    def game_over(self):
        if self.game_state in [self.GameState.FIRST_MENU, self.GameState.DEFAULT_MENU]:
            ds = random.choice([self.death_sound,
                                self.death_sound_2,
                                self.death_sound_3,
                                self.death_sound_4])
            ds.play()
            self.sky_color.increment(50)
            if self.game_state == self.GameState.DEFAULT_MENU:
                self.music_handler.music_stop(1500)
            self.progress['highscore'] = max(self.progress.get('highscore', 0), int(self.score))
            if self.score >= 110:
                self.progress['achieved 110'] = True
            self.progress['deaths'] = self.progress.get('deaths', 0) + 1
            if self.progress['deaths'] > 6:
                self.progress['bear'] = True

            # print(self.player_sprite.rect.top - self.player_sprite.rect.bottom)

    def add_new_enemy(self, snail_relative_chance: int, fly_relative_chance: int):
        if random.randint(1, snail_relative_chance + fly_relative_chance) <= fly_relative_chance:
            if self.advanced_enemies and random.randint(1, 2) == 1:
                a = Bat(self)
                a.rect.bottomleft = (random.randint(self.enemy_placement_range[0], self.enemy_placement_range[1] + 100),
                                     150)
                a.set_speed(v_x=-1 * random.randint(self.fly_speed_range[0] - 50, self.fly_speed_range[1] - 50))
                a.set_difficulty((int(self.score)-99)//10)
                self.enemy_group.add(a)
                del a
            else:
                a = Fly(self)
                a.rect.bottomleft = (random.randint(self.enemy_placement_range[0], self.enemy_placement_range[1]),
                                     random.randint(self.fly_y_range[0], self.fly_y_range[1]))
                a.set_speed(v_x=-1 * random.randint(self.fly_speed_range[0], self.fly_speed_range[1]))
                self.enemy_group.add(a)
                del a
        else:
            if self.advanced_enemies and random.randint(1, 9) == 1:
                a = Cham(self)
                a.rect.bottomleft = (random.randint(815, 850), 300)
                a.set_speed(v_x=-1 * random.randint(200, 300))

            elif self.game_state == self.GameState.FIRST_GAME and len(self.enemy_spawn):
                a = Snail(self)
                a.rect.bottomleft = (810, 300)
                a.set_speed(v_x=-400)
            else: #elif self.game_state in [self.FIRST_GAME, self.DEFAULT_GAME]:
                a = Snail(self)
                a.rect.bottomleft = (random.randint(self.enemy_placement_range[0], self.enemy_placement_range[1]), 300)
                a.set_speed(v_x=-1 * random.randint(self.snail_speed_range[0], self.snail_speed_range[1]))

            self.enemy_group.add(a)
            del a

    def enemy_collision(self) -> bool:
        collisions = pygame.sprite.spritecollide(self.player_sprite, self.enemy_group, False)
        return bool(collisions)

    def aim_at_enemy(self):
        if bool(self.enemy_group.get_sprites_at(pygame.mouse.get_pos())):
            return pygame.mouse.get_pos()
        return None

    def draw_laser_sight(self):
        if self.player_sprite.weapon:
            enemy_pos = self.aim_at_enemy()
            if enemy_pos:
                start_pos = (self.player_sprite.weapon.rect.right - 40, self.player_sprite.weapon.rect.centery - 2)
                pygame.draw.line(self.screen, (240, 0, 0), start_pos, enemy_pos, 2)

    def shoot_at_enemy(self):
        return self.enemy_group.get_sprites_at(pygame.mouse.get_pos())

    def draw_shot_after_image(self):
        for index, i in enumerate(self.gunshot_afterimage):
            if i[1] > 0.0:
                pygame.draw.line(self.screen, (255, 255, 100), (self.player_sprite.weapon.rect.midright[0]-8, self.player_sprite.weapon.rect.midright[1]-4), i[0],
                             width= int(6 * math.sin(i[1]*math.pi/100.0)))
                i[1] -= self.delta_time
            else:
                self.gunshot_afterimage.pop(index)

    def draw_out_of_bounds_marker(self):
        if self.player_sprite.rect.bottom < -10:
            oob_marker_surf = pygame.transform.scale(self.oob_pointer, (40, 20))
            oob_marker_rect = oob_marker_surf.get_rect(midtop=(self.player_sprite.rect.centerx, 5))

            oob_text_surf = self.text_to_surface_mf(f'{-(self.player_sprite.rect.bottom - 10)//48}m',
                                                    True, (237, 28, 36), size=32)
            oob_text_rect = oob_text_surf.get_rect(midtop=[oob_marker_rect.centerx, oob_marker_rect.bottom + 3])

            self.screen.blit(oob_marker_surf, oob_marker_rect)
            self.screen.blit(oob_text_surf, oob_text_rect)

    def draw_tool_tips(self):
        match self.game_state:
            case self.GameState.DEFAULT_GAME | self.GameState.BEAR_GAME | self.GameState.ZEBRA_GAME:
                if int(self.score) < 20:
                    self.jump_tip.set_alpha(100-5*int(self.score))
                    self.move_tip.set_alpha(100-5*int(self.score))
                    self.shoot_tup.set_alpha(100-5*int(self.score))
                    self.pickup_tip.set_alpha(100-5*int(self.score))
                    self.screen.blit(self.jump_tip, (620, 25))
                    self.screen.blit(self.move_tip, (620, 45))
                    self.screen.blit(self.shoot_tup, (620, 65))
                    self.screen.blit(self.pickup_tip, (620, 85))
            case self.GameState.FIRST_GAME:
                if int(self.score) < 20:
                    self.jump_tip.set_alpha(100 - 5 * int(self.score))
                    self.screen.blit(self.jump_tip, (620, 25))

    def draw_ammo_count(self):
        if self.player_sprite.weapon:
            color = (240, 240, 240)
            ammo = self.player_sprite.weapon.ammo
            if ammo == 0:
                color = (210, 40, 40)
            elif ammo < 5:
                color = (230, 230, 40)
            if ammo < 10:
                ammo = f' {ammo}'
            else:
                ammo = str(ammo)
            ammo_count_surf = self.text_to_surface_mf(ammo, True, color, size=55)
            self.screen.blit(ammo_count_surf, (685, 345))
            self.screen.blit(self.ammo, (715, 335))

    def draw_jumps_count(self):
        if not self.kill_run:
            return None
        for i in range(self.player_sprite.max_jumps):
            if i < self.player_sprite.jumps:
                _image = self.jump_on
            else:
                _image = self.jump_off
            self.screen.blit(_image, (20 + i*55, 330))

    def draw_spec_abilities(self):
        if self.mask_sprite.bear_activation_time is not None and self.mask_sprite.bear_activation_time > 0:
            self.mask_sprite.image.set_alpha(0)
            _alpha = int(255 * math.sin(1 + (600 - self.mask_sprite.bear_activation_time)/300))
            self.bear_banner.set_alpha(_alpha)
            self.mask_sprite.bear_activation_time -= self.delta_time
            self.screen.blit(self.bear_banner, (0, 0))
        else:
            self.mask_sprite.bear_activation_time = None
        # if self.game_state == self.BEAR_GAME and not self.mask_sprite.deflect:



    def difficulty_scaling(self):
        if self.kill_run and int(self.score) != self.last_rescale_score:
            self.ground_stiffness = GROUND_STIFFNESS * (131 - int(self.score))/137

            self.player_sprite.max_jumps = 1 + int(self.score)//30

            self.max_ammo = MAX_AMMO_CAPACITY - int(self.score)//6
            self.pickup_rate = PICKUP_DROP_RATE - int(self.score)//10

            self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 7 * int(self.score) \
                                        - 50 * bool(self.advanced_enemies and (self.game_state != self.GameState.BEAR_GAME
                                                                               or self.mask_sprite.deflect))

            self.enemy_placement_range = [ENEMY_PLACEMENT_RANGE[0], ENEMY_PLACEMENT_RANGE[1] - int(self.score)]
            self.fly_y_range = [FLY_Y_RANGE[0] - int(self.score)//2, FLY_Y_RANGE[1] + int(self.score)]
            self.snail_speed_range = [SNAIL_SPEED_RANGE[0] + 50 + int(self.score), SNAIL_SPEED_RANGE[1] + 2*int(self.score)]
            self.fly_speed_range = [FLY_SPEED_RANGE[0] + 50 + int(self.score), FLY_SPEED_RANGE[1] + 2*int(self.score)]

            self.last_rescale_score = int(self.score)

    def enter_the_sandman(self):
        if not self.advanced_enemies and self.kill_run and int(self.score) >= 110:
            if not self.advanced_enemies:
                # self.sky_color_surf.set_alpha(0)
                self.kill_run_init_sound.play()
                self.music_handler.music_play(self.enter_the_sandman_music)
            self.advanced_enemies = True
            self.sky_is_over = True  # I don't wanna see you go

    def text_to_surface_mf(self, text, antialias, color, bg=None, size=50):
        _font = pygame.font.Font(self.main_font, size)
        return _font.render(text, antialias, color, bg)

    def score_add(self, mode: str):
        if not self.progress.get('achieved 110', False) and not self.advanced_enemies:
            match mode:
                case 'snail_kill':
                    self.score += 2.0
                case 'fly_kill':
                    self.score += 3.0
                case 'pass':
                    self.score += 1
        elif self.progress.get('achieved 110', False) and not self.advanced_enemies:
            if not self.advanced_enemies:
                match mode:
                    case 'snail_kill':
                        self.score += 3.9
                    case 'fly_kill':
                        self.score += 4.9
                    case 'pass':
                        self.score += 2.9
        else:
            match mode:
                case 'snail_kill':
                    self.score += 0
                case 'fly_kill':
                    self.score += 1
                case 'pass':
                    self.score += 0.25

if __name__ == '__main__':
    pass
