import math
import random
from enum import Enum, auto
from datetime import datetime

import pygame

from some_function import save

from R_Game.scripts.color_sine import ColorSine
from R_Game.scripts.abs_color import ColorAbs
from R_Game.scripts.misc_sprites import SunGroup

from R_Game.scripts.colorblind_mode import Touhou

from R_Game.scripts.MyQT import CB_CheckBox, EndlessMode_CheckBox, Epilepsy_CheckBox

from R_Game.scripts.player_sprite import Player, Mask, Weapon, Punch, Stomp
from R_Game.scripts.fly_sprite import Fly, Bat
from R_Game.scripts.snail_sprite import Snail, Cham, Toad, Stomped_Snail

from R_Game.config.config import (
                                  DISPLAY_CAPTION,
                                  RUNNER_SCREEN_RESOLUTION,
                                  STOMP_SPEED,
                                  GRAVITY_ACCELERATION,
                                  GROUND_STIFFNESS,
                                  ENEMY_SPAWN_INTERVAL_MS,
                                  ENEMY_PLACEMENT_RANGE,
                                  FLY_Y_RANGE,
                                  SNAIL_SPEED_RANGE,
                                  FLY_SPEED_RANGE,
                                  MAX_AMMO_CAPACITY,
                                  PICKUP_DROP_RATE
                                  )

from R_Game.config.titles import NUKE_TITLES


class MusicHandler:

    @staticmethod
    def music_play(new_music):
        _path, _volume = new_music

        pygame.mixer_music.unload()

        pygame.mixer_music.load(_path)
        pygame.mixer_music.set_volume(_volume)
        pygame.mixer_music.play(-1, fade_ms=400)

    @staticmethod
    def music_stop(fadeout=0):
        if fadeout is None:
            pygame.mixer_music.stop()
        else:
            pygame.mixer_music.fadeout(fadeout)


class HMGame(object):
    # 48px = 1 meter

    class GameState(Enum):
        EXIT         = auto()
        LOADING      = auto()

        FIRST_GAME   = auto()
        FIRST_MENU   = auto()

        DEFAULT_GAME = auto()
        BEAR_GAME    = auto()
        ZEBRA_GAME   = auto()
        TIGER_GAME   = auto()
        FROG_GAME    = auto()

        COLOR_BLIND  = auto()

        DEFAULT_MENU = auto()

        NUKE_START   = auto()
        NUKE_CREDITS = auto()
        NUKE_MENU    = auto()

        NO_KILL_START = auto()
        NO_KILL_MENU  = auto()

        TRANSITION_TO_SRALKER = auto()

    def __init__(self, progress=None):

        if progress is None:
            progress = dict()
        self.progress = progress

    def start_game(self):
        self.screen = pygame.display.set_mode(RUNNER_SCREEN_RESOLUTION)
        pygame.display.set_caption(DISPLAY_CAPTION)
        pygame.display.set_icon(pygame.image.load('R_Game/graphics/Player/rooster.png').convert_alpha())

        self.screen.blit(pygame.image.load('R_Game/graphics/banners/loading_1.png'), (0, 0))
        pygame.display.update()

        self.load_images()

        self.mouse = pygame.sprite.Sprite()
        self.mouse.image = pygame.Surface((2, 2))
        self.mouse.rect = pygame.Rect(0, 0, 2, 2)

        self.clock = pygame.time.Clock()
        self.main_font = 'R_Game/font/Pixeltype.ttf'
        self.japan_font = 'R_Game/font/Japanese.ttf'

        self.game_name_surf = self.text_to_surface_mf('Hohline Cherkasy', True, 'Red')

        self.sky_color_surf = pygame.Surface((800, 250))
        self.sky_color_foreground = pygame.Surface((800, 400))
        self.sky_color = ColorSine(phases= [math.pi * 0.5, math.pi * 0.7, 0.0],
                                   freqs=  [1.1,           0.2,           1.0],
                                   statics=[0.5,           0.7,           0.7],
                                   ampls=  [0.5,           0.3,           0.3])

        self.player_menu = pygame.transform.rotozoom(self.player_stand, 0, 3)
        self.player_menu_rect = self.player_menu.get_rect(center=(179, 200))
        self.frog_menu = pygame.transform.scale(self.frog_mask, (225, 195))
        self.frog_menu_rect = self.frog_menu.get_rect(midtop=[self.player_menu_rect.centerx+3, self.player_menu_rect.top-10])
        self.wasted_surf = self.text_to_surface_mf('[REDACTED]', True, 'White', 'Black', 48)
        self.wasted_rect = self.wasted_surf.get_rect(center=(179, 181))

        self.screen.blit(pygame.image.load('R_Game/graphics/banners/loading_2.png'), (0, 0))
        _warning_text_ = self.text_to_surface_mf('WARNING: Game contains flashing lights', True, (40, 40, 40), size=40)
        _rect_ = _warning_text_.get_rect(center=(400, 370))
        self.screen.blit(_warning_text_, _rect_)
        pygame.display.update()

        self.load_sounds()

        self.music_handler = MusicHandler()

        self.gun_sound.set_volume(1.1)
        self.empty_gun_sound.set_volume(1.1)
        self.gun_pickup_sound.set_volume(0.8)
        self.throw_sound.set_volume(4.5)
        self.swing_sound.set_volume(3.0)
        self.punch_sound.set_volume(4.0)
        self.stomp_sound.set_volume(4.0)
        self.jump_sound.set_volume(1.0)

        self.kill_run_init_sound.set_volume(1.5)

        self.death_sound.set_volume(1.3)
        self.death_sound_2.set_volume(1.3)
        self.death_sound_3.set_volume(6)
        self.death_sound_4.set_volume(2.3)

        self.pacifist_speech.set_volume(3.0)
        self.pacifist_speech_2.set_volume(3.0)
        self.pacifist_speech_3.set_volume(1.5)

        self.cb_mode = Touhou(self)

        self.enemy_spawn_timer = pygame.USEREVENT + 1

        self.score = -1
        self.delta_time = 1
        self.kills = 0
        self.advanced_enemies = False

        self.UI_colorblind = pygame.sprite.Group(CB_CheckBox(self, ' Colorblind mode', (120, 20)))

        self.UI_epilepsy = pygame.sprite.Group(Epilepsy_CheckBox(self, ' Less fun, more frames', (690, 380)))
        self.no_epilepsy = self.UI_epilepsy.sprites()[0].state

        self.UI_endless = pygame.sprite.Group(EndlessMode_CheckBox(self, ' Endless mode', (690, 355)))
        self.endless = self.UI_endless.sprites()[0].state

        if self.progress.get('deaths', 0) == 0:
            self.set_up_game('first')
        else:
            self.game_state = self.GameState.DEFAULT_MENU
            self.music_handler.music_play(self.menu_music)

        return self.game_loop()

    def load_images(self):

        self.normal_sky_surf = pygame.image.load('R_Game/graphics/background/Sky.png').convert_alpha()

        self.sky_surf    = pygame.image.load('R_Game/graphics/background/Sky_miami.png').convert_alpha()
        self.ground_surf = pygame.image.load('R_Game/graphics/background/ground.png').convert()

        self.poroh        = pygame.image.load('R_Game/graphics/misc/poroh.png').convert_alpha()
        self.poroh_banner = pygame.image.load('R_Game/graphics/banners/pacifist_banner.png').convert()
        self.no_kill_menu = pygame.image.load('R_Game/graphics/background/no_kill_menu.png').convert_alpha()

        self.wojaks           = pygame.image.load('R_Game/graphics/misc/wojaks.png').convert_alpha()
        self.sun_ray          = pygame.image.load('R_Game/graphics/misc/sun_ray.png').convert_alpha()
        self.nuke_menu_palms  = pygame.image.load('R_Game/graphics/background/palms_bg.png').convert_alpha()
        self.squidward_banner = pygame.image.load('R_Game/graphics/banners/squidward_meme_banner.png').convert_alpha()

        self.player_walk_1 = pygame.image.load('R_Game/graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('R_Game/graphics/Player/player_walk_2.png').convert_alpha()
        self.player_jump   = pygame.image.load('R_Game/graphics/Player/jump.png').convert_alpha()

        self.player_stand = pygame.image.load('R_Game/graphics/Player/player_stand.png').convert_alpha()

        self.rooster_mask = pygame.image.load('R_Game/graphics/Player/rooster.png').convert_alpha()

        self.bear_mask   = pygame.image.load('R_Game/graphics/Player/bear.png').convert_alpha()
        self.bear_banner = pygame.image.load('R_Game/graphics/banners/do_you_know_this_man.png').convert()

        self.zebra_mask = pygame.image.load('R_Game/graphics/Player/zebra.png').convert_alpha()

        self.tiger_mask_normal = pygame.image.load('R_Game/graphics/Player/tiger_normal.png').convert_alpha()
        self.tiger_mask_worn   = pygame.transform.scale(pygame.image.load('R_Game/graphics/Player/tiger.png').convert_alpha(), (90, 80))

        self.frog_mask = pygame.image.load('R_Game/graphics/Player/frog.png').convert_alpha()

        self.punch_frames = [pygame.image.load('R_Game/graphics/Player/punches/punch_1.png').convert_alpha(),
                             pygame.image.load('R_Game/graphics/Player/punches/punch_1-5.png').convert_alpha(),
                             pygame.image.load('R_Game/graphics/Player/punches/punch_2.png').convert_alpha(),
                             pygame.image.load('R_Game/graphics/Player/punches/punch_2-5.png').convert_alpha(),
                             pygame.image.load('R_Game/graphics/Player/punches/punch_3.png').convert_alpha()
                             ]
        for frame in self.punch_frames:
            frame.set_alpha(100)

        self.stomp_image   = pygame.image.load('R_Game/graphics/Player/stomp.png').convert_alpha()
        self.stomped_enemy = pygame.image.load('R_Game/graphics/snail/stomped.png').convert_alpha()

        self.sun_glasses = pygame.image.load('R_Game/graphics/Player/sun_glasses.png').convert_alpha()
        self.weapon   = pygame.image.load('R_Game/graphics/Player/GUN.png').convert_alpha()
        self.ammo     = pygame.transform.scale(pygame.image.load('R_Game/graphics/icons/ammo.png').convert_alpha(), (50, 50))
        self.jump_on  = pygame.transform.scale(pygame.image.load('R_Game/graphics/icons/jump_on.png').convert_alpha(), (50, 50))
        self.jump_off = pygame.transform.scale(pygame.image.load('R_Game/graphics/icons/jump_off.png').convert_alpha(), (50, 50))
        self.dash     = pygame.transform.scale(pygame.image.load('R_Game/graphics/icons/dash.png').convert_alpha(), (50, 50))
        self.punch    = pygame.transform.scale(pygame.image.load('R_Game/graphics/icons/punch.png').convert_alpha(), (50, 50))

        self.fly_1    = pygame.image.load('R_Game/graphics/fly/Fly1.png').convert_alpha()
        self.fly_2    = pygame.image.load('R_Game/graphics/fly/Fly2.png').convert_alpha()
        self.fly_mask = pygame.image.load('R_Game/graphics/fly/owl.png').convert_alpha()
        self.bat_mask = pygame.image.load('R_Game/graphics/fly/bat.png').convert_alpha()

        self.snail_1    = pygame.image.load('R_Game/graphics/snail/snail1.png').convert_alpha()
        self.snail_2    = pygame.image.load('R_Game/graphics/snail/snail2.png').convert_alpha()
        self.snail_mask = pygame.image.load('R_Game/graphics/snail/dog.png').convert_alpha()
        self.cham_1     = pygame.image.load('R_Game/graphics/snail/cham1.png').convert_alpha()
        self.cham_2     = pygame.image.load('R_Game/graphics/snail/cham2.png').convert_alpha()
        self.cham_mask  = pygame.image.load('R_Game/graphics/snail/cham.png').convert_alpha()

        self.oob_pointer = pygame.image.load('R_Game/graphics/icons/oob_pointer.png').convert_alpha()

    def load_sounds(self):
        self.death_sound     = pygame.mixer.Sound('R_Game/audio/death sounds/death.mp3')
        self.death_sound_2   = pygame.mixer.Sound('R_Game/audio/death sounds/death2.mp3')
        self.death_sound_3   = pygame.mixer.Sound('R_Game/audio/death sounds/death3.mp3')
        self.death_sound_4   = pygame.mixer.Sound('R_Game/audio/death sounds/death4.mp3')

        self.menu_music      = ['R_Game/audio/menu music/menu.mp3', 0.2]
        self.post_nuke_music = ['R_Game/audio/menu music/post_nuke_menu.mp3', 0.6]

        self.pacifist_speech     = pygame.mixer.Sound('R_Game/audio/misc sounds/pacifist_speech_1.mp3')
        self.pacifist_speech_2   = pygame.mixer.Sound('R_Game/audio/misc sounds/pacifist_speech_2.mp3')
        self.pacifist_speech_3   = pygame.mixer.Sound('R_Game/audio/misc sounds/pacifist_speech_3.mp3')
        self.pacifist_menu_music = ['R_Game/audio/menu music/pacifist_menu.mp3', 0.5]

        self.screen.blit(pygame.image.load('R_Game/graphics/banners/loading_3.png'), (0, 0))
        _warning_text_ = self.text_to_surface_mf('WARNING: Game contains flashing lights', True, (50, 50, 50), size=40)
        _rect_ = _warning_text_.get_rect(center=(400, 370))
        self.screen.blit(_warning_text_, _rect_)
        pygame.display.update()

        self.first_run_music = ['R_Game/audio/run music/first_run_music.mp3', 0.2]

        self.run_music_1 = ['R_Game/audio/run music/run_music1.mp3', 0.3]
        self.run_music_2 = ['R_Game/audio/run music/run_music2.mp3', 0.3]
        self.run_music_3 = ['R_Game/audio/run music/run_music3.mp3', 0.3]

        self.bear_music  = ['R_Game/audio/run music/bear_run_music.mp3', 0.4]
        self.zebra_music = ['R_Game/audio/run music/zebra_run_music.mp3', 0.4]
        self.tiger_music = ['R_Game/audio/run music/tiger_run_music.mp3', 0.8]

        self.post_bear_music  = ['R_Game/audio/run music/post_bear_music.mp3', 0.4]
        self.post_zebra_music = ['R_Game/audio/run music/post_zebra_music.mp3', 0.4]
        self.post_tiger_music = ['R_Game/audio/run music/post_tiger_music.mp3', 0.4]

        self.spain_music = ['R_Game/audio/run music/spain_music.mp3', 1.0]

        self.enter_the_sandman_music = ['R_Game/audio/boss music/enter_the_sandman.mp3', 0.8]
        self.enter_the_siemen_music  = ['R_Game/audio/boss music/t00rbo_ki11er_BLOODY_run.mp3', 1.0]
        self.enter_the_sweden_music  = ['R_Game/audio/boss music/enter_the_sweden.mp3', 1.0]

        self.nuke_music      = ['R_Game/audio/misc music/nuke.mp3', 1.0]

        self.gun_sound           = pygame.mixer.Sound('R_Game/audio/misc sounds/gunshot.mp3')
        self.empty_gun_sound     = pygame.mixer.Sound('R_Game/audio/misc sounds/empty_gun.mp3')
        self.gun_pickup_sound    = pygame.mixer.Sound('R_Game/audio/misc sounds/gun_pickup.mp3')
        self.kill_run_init_sound = pygame.mixer.Sound('R_Game/audio/misc sounds/kill_run_init.mp3')
        self.throw_sound         = pygame.mixer.Sound('R_Game/audio/misc sounds/throw.mp3')
        self.swing_sound         = pygame.mixer.Sound('R_Game/audio/misc sounds/swing.mp3')
        self.punch_sound         = pygame.mixer.Sound('R_Game/audio/misc sounds/punch.mp3')
        self.stomp_sound         = pygame.mixer.Sound('R_Game/audio/misc sounds/stomp.mp3')
        self.jump_sound          = pygame.mixer.Sound('R_Game/audio/misc sounds/jump.mp3')

    def choose_music(self, mode):
        music_ = [self.menu_music]
        if mode == 'first':
            return self.music_handler.music_play(self.first_run_music)
        match mode:
            case 'rooster':
                music_ = [self.run_music_1]
            case 'bear':
                music_ = [self.bear_music]
            case 'zebra':
                music_ = [self.zebra_music]
            case 'tiger':
                music_ = [self.tiger_music]
            case 'frog':
                music_ = [self.run_music_1, self.bear_music, self.zebra_music, self.tiger_music]

        if self.progress.get(f"{mode}_played", False):
            if self.progress.get('rooster_finished', False):
                music_.extend([self.run_music_1, self.run_music_2, self.run_music_3])
            if self.progress.get('bear_finished', False):
                music_.extend([self.bear_music, self.post_bear_music])
            if self.progress.get('zebra_finished', False):
                music_.extend([self.zebra_music, self.post_zebra_music])
            if self.progress.get('tiger_finished', False):
                music_.extend([self.tiger_music, self.post_tiger_music])
            if self.progress.get('frog_finished', False):
                music_.append(self.first_run_music)
            if self.progress.get('all speeches', False):
                music_.append(self.spain_music)

        choice_ = random.choice(music_)

        self.music_handler.music_play(choice_)

    def set_up_game(self, _mode='rooster'):
        self.sky_color_surf.fill(self.sky_color.return_color())
        if self.UI_colorblind.sprites()[0].state:
            self.music_handler.music_stop(300)
            self.score = 0
            self.game_state = self.GameState.COLOR_BLIND
            self.cb_mode.start = pygame.time.get_ticks()
            return self.cb_mode.set_up_run()

        if self.UI_endless.sprites()[0].state:
            self.endless = True
        else:
            self.endless = False

        if self.UI_epilepsy.sprites()[0].state:
            self.no_epilepsy = True
        else:
            self.no_epilepsy = False

        # Semen's suggestion was to make pacifist root a bit more fun
        self.harder_mode = self.progress.get('zebra', False)

        if _mode == 'second':
            mode = 'rooster'
        else:
            mode = _mode

        self.titles = None

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

        else:
            self.enemy_spawn = []
            if mode != 'tiger' and _mode != 'second':
                self.player_sprite.pick_up_weapon(Weapon(self))
            elif mode != 'tiger' and _mode == 'second':
                self.pickups.add(Weapon(self, (200, 300)))
                self.enemy_spawn = [None, 'fly']

        self.enemy_group = pygame.sprite.LayeredUpdates()
        self.enemy_attachments = pygame.sprite.LayeredUpdates()

        self.score = 0
        self.kills = 0

        self.gunshot_afterimage = []

        if mode in ['rooster', 'bear', 'zebra', 'tiger', 'frog']:
            self.jump_tip = self.text_to_surface_mf('SPACE/W to Jump', True, '#5d5d5d', size=32)
            self.move_tip = self.text_to_surface_mf('A/D to Move', True, '#5d5d5d', size=32)
            self.shoot_tip = self.text_to_surface_mf('LMB to Shoot', True, '#5d5d5d', size=32)
            self.pickup_tip = self.text_to_surface_mf('RMB to Drop/Pickup', True, '#5d5d5d', size=32)
            self.dash_tip = self.text_to_surface_mf('SHIFT to Air Dash', True, '#5d5d5d', size=32)
            if mode == 'tiger':
                self.shoot_tip = self.text_to_surface_mf('LMB to Punch', True, '#5d5d5d', size=32)
        elif mode == 'first':
            self.jump_tip = self.text_to_surface_mf('SPACE to Jump', True, '#4d4d4d', size=35)
            self.move_tip = self.text_to_surface_mf('', True, '#5d5d5d', size=32)
            self.shoot_tip = self.text_to_surface_mf('', True, '#5d5d5d', size=32)
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
                           'zebra': self.GameState.ZEBRA_GAME,
                           'tiger': self.GameState.TIGER_GAME,
                           'frog': self.GameState.FROG_GAME}[mode]

        self.advanced_enemies = False
        self.sky_is_over = False  # Even though we can't afford
        self.sky_color_surf.set_alpha(255)
        self.ground_surf.set_alpha(255)
        self.sky_color_foreground.set_alpha(0)
        if self.no_epilepsy:
            self.sky_color_foreground.fill((208, 244, 247))
            self.sky_color_foreground.set_alpha(80)

        self.choose_music(mode)

        self.progress[f"{mode}_played"] = True

        self.run_start_time = pygame.time.get_ticks()

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
                case self.GameState.NO_KILL_START:
                    self.pacifist_animation()
                case self.GameState.NO_KILL_MENU:
                    self.pacifist_menu()
                case self.GameState.DEFAULT_GAME | self.GameState.BEAR_GAME | \
                     self.GameState.ZEBRA_GAME | self.GameState.TIGER_GAME | self.GameState.FROG_GAME:
                    self.runtime_frame()
                case self.GameState.DEFAULT_MENU:
                    self.menu_frame()
                case self.GameState.FIRST_GAME:
                    self.runtime_frame('first')
                case self.GameState.FIRST_MENU:
                    self.menu_frame_first()
                case self.GameState.COLOR_BLIND:
                    self.cb_mode.runtime_frame()
                case self.GameState.LOADING:
                    pass
                case self.GameState.TRANSITION_TO_SRALKER:
                    self.music_handler.music_stop()
                    return self.progress, "launch_sralker"
            if self.game_state != self.GameState.EXIT:
                pygame.display.update()
                self.clock.tick(60)
                self.delta_time = (pygame.time.get_ticks() - self.last_time_frame)
        return self.progress, None

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = self.GameState.EXIT

            if self.game_state in [self.GameState.FIRST_GAME,
                                   self.GameState.DEFAULT_GAME,
                                   self.GameState.BEAR_GAME,
                                   self.GameState.ZEBRA_GAME,
                                   self.GameState.TIGER_GAME,
                                   self.GameState.FROG_GAME,
                                   self.GameState.COLOR_BLIND]:

                # players controls

                if event.type == pygame.KEYDOWN:
                    self.player_sprite.player_input(event.key, False)
                if event.type == pygame.KEYUP:
                    self.player_sprite.player_input(event.key, True)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.player_sprite.player_input(event.button, False, event.pos)

                # enemy spawn
                if event.type == self.enemy_spawn_timer and self.game_state == self.GameState.COLOR_BLIND:

                    if self.enemy_spawn:
                        pass
                    else:
                        self.cb_mode.spawn_new_enemy()
                        pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)

                elif event.type == self.enemy_spawn_timer:
                    if self.enemy_spawn:
                        next_enemy = self.enemy_spawn.pop(0)
                        if next_enemy == 'snail':
                            self.add_new_enemy(1, 0)
                        elif next_enemy == 'fly':
                            self.add_new_enemy(0, 1)
                    elif self.game_state == self.GameState.COLOR_BLIND:
                        pass
                    else:
                        self.add_new_enemy(3, 1)
                    pygame.time.set_timer(self.enemy_spawn_timer, self.enemy_spawn_interval, 1)


            elif self.game_state in [self.GameState.FIRST_MENU, self.GameState.DEFAULT_MENU, self.GameState.NUKE_MENU, self.GameState.NO_KILL_MENU] \
                    and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    if self.game_state == self.GameState.FIRST_MENU:
                        if self.score == 0:
                            self.set_up_game('first')
                        else:
                            self.set_up_game('second')
                    else:
                        self.set_up_game()
                elif self.progress.get('bear', False) and event.key == pygame.K_b:
                    self.set_up_game('bear')
                elif self.progress.get('zebra', False) and event.key == pygame.K_z:
                    self.set_up_game('zebra')
                elif self.progress.get('tiger', False) and event.key == pygame.K_t:
                    self.set_up_game('tiger')
                elif datetime.today().isoweekday() == 3 and event.key == pygame.K_f:
                    self.set_up_game('frog')
                elif self.progress.get('sralker_unlocked', False) and not self.progress.get('sralker_opened', False) \
                        and event.key == pygame.K_n:
                    self.progress["sralker_opened"] = True
                    self.game_state = self.GameState.TRANSITION_TO_SRALKER

            elif self.game_state == self.GameState.DEFAULT_MENU and event.type == pygame.MOUSEBUTTONDOWN:
                for elem in self.UI_colorblind:
                    if elem.collide(event.pos):
                        elem.on_click()
                for elem in self.UI_epilepsy:
                    if elem.collide(event.pos):
                        elem.on_click()
                for elem in self.UI_endless:
                    if elem.collide(event.pos):
                        elem.on_click()


            elif self.game_state == self.GameState.NUKE_CREDITS and (event.type == pygame.KEYDOWN and self.progress.get('zebra', False)):
                self.game_state = self.GameState.NUKE_MENU
                self.progress['zebra'] = True
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
        if self.no_epilepsy:
            pass
        elif not self.sky_is_over and self.mask_sprite.dash_status != 'active':
            self.sky_color_surf.fill(sky_color)
        else:
            self.sky_color_foreground.fill(sky_color)
            inc = inc * 2
        if not self.no_epilepsy:
            self.sky_color.increment(inc)
        self.screen.blit(self.ground_surf, (0, 300))

        if mode == 'first' or self.no_epilepsy:
            if not (self.sky_is_over or self.mask_sprite.dash_status == 'active'):
                self.screen.blit(self.normal_sky_surf, (0, 0))
        else:
            if not self.sky_is_over and self.mask_sprite.dash_status != 'active':
                self.screen.blit(self.sky_color_surf, (0, 0))
                self.screen.blit(self.sky_surf, (0, 0))
        if self.endless:
            score_display = int(self.score)
        else:
            score_display = int(min(self.score, 137))
        score_surf = self.text_to_surface_mf(f'Score: {score_display}', True, (44+200*bool(self.kills > 0 or int(self.score) >= 110),
                                                                                      44+200*bool(not self.kills > 0 and int(self.score) >= 110),
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

        self.weapon_collision()

        self.draw_laser_sight()
        self.draw_shot_after_image()
        self.draw_out_of_bounds_marker()
        self.draw_tool_tips()
        self.draw_ammo_count()
        self.draw_jumps_count()
        self.draw_spec_abilities()

        self.difficulty_scaling()
        self.enter_the_sandman()

        if self.score >= 137 and not self.endless:

            string_ = f"{self.mask_sprite.type_}_finished"
            self.progress[string_] = True
            save(self.progress)

            if self.kills > 0:
                self.game_state = self.GameState.NUKE_START
                self.music_handler.music_stop(1050)
                _color = self.sky_color.return_color()

                self.sky_color = ColorAbs(_color)
                self.screen.blit(self.ground_surf, (0, 300))
                self.animation_time = pygame.time.get_ticks()
                self.sunrays = SunGroup(self)
                return

            else:
                self.progress['tiger'] = True
                self.game_state = self.GameState.NO_KILL_START
                self.sky_color_foreground.fill('Black')
                self.music_handler.music_stop(550)
                self.poroh_banner.set_alpha(255)
                self.mask_sprite.image.set_alpha(0)
                for i in self.enemy_group:
                    i.mask_bool = False
                self.kill_run_init_sound.play()
                if self.progress.get('all speeches', False):
                    pass
                elif self.progress.get('both speeches', False):
                    self.pacifist_speech_3.play()
                elif self.progress.get('color_blind_unlocked', False):
                    self.pacifist_speech_2.play()
                else:
                    self.pacifist_speech.play()

                self.animation_time = pygame.time.get_ticks()

        if self.mask_sprite.dash_status != 'active' \
           and not (self.mask_sprite.dash_status == 'cooldown' and self.player_sprite.is_airborne()) \
           and self.enemy_collision():
            if self.mask_sprite.deflect:
                self.mask_sprite.deflect = False
                self.mask_sprite.deflect_ability()
            else:
                if self.game_state in [self.GameState.DEFAULT_GAME, self.GameState.BEAR_GAME, self.GameState.ZEBRA_GAME, self.GameState.TIGER_GAME, self.GameState.FROG_GAME]:
                    self.game_state = self.GameState.DEFAULT_MENU
                elif self.game_state == self.GameState.FIRST_GAME:
                    self.game_state = self.GameState.FIRST_MENU
        self.game_over()

        if not self.no_epilepsy and (self.sky_is_over or self.mask_sprite.dash_status == 'active'):
            self.sky_color_foreground.set_alpha(max(min(137, int(self.score)) - 50, 60))
            self.ground_surf.set_alpha(max(365 - 3*min(137, int(self.score)), 50))
            self.screen.blit(self.sky_color_foreground, (0, 0))
        elif self.no_epilepsy and (self.sky_is_over or self.mask_sprite.dash_status == 'active'):
            self.screen.blit(self.sky_color_foreground, (0, 0))

    def menu_frame(self):

        self.screen.fill(self.sky_color.return_color())

        self.screen.blit(self.player_menu, self.player_menu_rect)
        if datetime.today().isoweekday() == 3:
            self.screen.blit(self.frog_menu, self.frog_menu_rect)
        elif not self.runner_completed():
            if self.progress.get('all speeches', False):
                self.screen.blit(self.sun_glasses, (70, 156))
            else:
                self.screen.blit(self.wasted_surf, self.wasted_rect)
        if (int(self.score) >= self.progress.get('highscore', 0) and not self.endless) or \
                (int(self.score) >= self.progress.get('endless_highscore', 0) and self.endless):
            score_line = f"New highscore: {int(self.score)}"
        else:
            score_line = f'Your score is {int(self.score)}'
        rooster_game_line = 'Press Y to continue'
        bear_game_line = ''
        zebra_game_line = ''
        tiger_game_line = ''
        frog_game_line = ''
        final_line = ''
        if int(self.score) <= 0:
            score_line = ''
            rooster_game_line = 'Press Y key to start'
        elif int(self.score) >= 137:
            rooster_game_line = 'Press Y key to start'
        elif 110 <= int(self.score) < 137:
            rooster_game_line = 'Pacan k uspehoo shol (Y)'
        if self.progress.get('bear', False):
            bear_game_line = 'Press B to bear the unbearable'
        if self.progress.get('zebra', False):
            zebra_game_line = 'Press Z for zebra'
        if self.progress.get('tiger', False):
            tiger_game_line = 'Press T for tiger'
        if datetime.today().isoweekday() == 3:
            frog_game_line = 'Its Wednesday, ma dudes (F)'
        if self.progress.get('sralker_unlocked') and not self.progress.get('sralker_opened', False):
            if self.progress.get('zebra', False):
                final_line = 'Press'
            else:
                final_line = 'Press N'

        final_score_surf = self.text_to_surface_mf(score_line, True, 'Red')
        final_score_rect = final_score_surf.get_rect(center=(380, 100))
        rooster_game_surf = self.text_to_surface_mf(rooster_game_line, True, 'Red')
        rooster_game_rect = rooster_game_surf.get_rect(midleft=(415, 250))
        bear_game_surf = self.text_to_surface_mf(bear_game_line, True, 'Red')
        bear_game_surf.set_alpha(120)
        zebra_game_surf = self.text_to_surface_mf(zebra_game_line, True, 'Red')
        zebra_game_rect = zebra_game_surf.get_rect(midleft=(415, 210))
        tiger_game_surf = self.text_to_surface_mf(tiger_game_line, True, 'Red')
        tiger_game_rect = tiger_game_surf.get_rect(midleft=(415, 290))
        frog_game_surf = self.text_to_surface_mf(frog_game_line, True, 'Pink')
        frog_game_rect = frog_game_surf.get_rect(midleft=(365, 20))

        if final_line:
            color = self.sky_color.return_color()
            color = [max(0, i-8) for i in color]
            final_line_surf = self.text_to_surface_mf(final_line, True, color)
            final_line_surf = pygame.transform.rotate(final_line_surf, -90)
            final_line_rect = final_line_surf.get_rect(midbottom=(522, 190))

            self.screen.blit(final_line_surf, final_line_rect)

        self.screen.blit(final_score_surf, final_score_rect)
        self.screen.blit(rooster_game_surf, rooster_game_rect)
        self.screen.blit(zebra_game_surf, zebra_game_rect)
        self.screen.blit(tiger_game_surf, tiger_game_rect)
        self.screen.blit(frog_game_surf, frog_game_rect)

        self.screen.blit(bear_game_surf, (20, 350))

        self.screen.blit(self.game_name_surf, (200, 40))

        self.draw_menu_ui()

        if not self.no_epilepsy:
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

        if a is True and self.advanced_enemies:  # this will happen only once
            self.advanced_enemies = False
            self.sky_color_foreground.fill('White')
            self.music_handler.music_play(self.nuke_music)
            self.ground_surf.set_alpha(255)

        if a is True:
            if time_pass_ms > 5700:
                radius = -20 + 145 * round(math.log(time_pass_ms/1000 - 4.7, 10.3), 2)
            else:
                radius = 0

            self.sunrays.update(time_pass_ms)
            self.sunrays.draw(self.screen)
            pygame.draw.circle(self.screen, 'White', (365, 170), radius, draw_top_right=True, draw_top_left=True, draw_bottom_left=True)

        self.screen.blit(self.ground_surf, (0, 300))

        self.screen.blit(self.sky_surf, (0, 0))

        score_surf = self.text_to_surface_mf(f'Score: {int(min(self.score, 137))}', True,
                                             (44 + 200 * bool(self.kills > 0 or int(self.score) >= 110),
                                              44 + 200 * bool(not self.kills > 0 and int(self.score) >= 110),
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
        if time_pass_ms < 6000:
            self.enemy_group.update()
            self.enemy_attachments.update()
        self.enemy_group.draw(self.screen)
        self.enemy_attachments.draw(self.screen)

        self.pickups.draw(self.screen)

        if time_pass_ms < 850:
            alpha_ = 127 - 127 * time_pass_ms // 850
            self.sky_color_foreground.set_alpha(alpha_)

            self.screen.blit(self.sky_color_foreground, (0, -100))
        if time_pass_ms > 10000:
            alpha_ = 255 * (time_pass_ms - 10000) // 8000
            w_alpha_ = 70 * (time_pass_ms - 10000) // 4000
            self.sky_color_foreground.set_alpha(alpha_)
            self.wojaks.set_alpha(w_alpha_)

            if not self.progress.get('zebra', False):
                self.screen.blit(self.wojaks, (0, 0))

            self.screen.blit(self.sky_color_foreground, (0, 0))

        if time_pass_ms > 18700:
            self.game_state = self.GameState.NUKE_CREDITS
            self.advanced_enemies = True
            self.titles = [i for i in NUKE_TITLES]
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

        self.draw_titles(time_pass_ms)

        if time_pass_ms > 230300:
            self.progress['zebra'] = True
            self.game_state = self.GameState.NUKE_MENU
            self.sky_color.red, self.sky_color.green, self.sky_color.blue = 0, 0, 0
            self.music_handler.music_play(self.post_nuke_music)

    def pacifist_animation(self):
        time_pass_ms = pygame.time.get_ticks() - self.animation_time

        self.screen.blit(self.normal_sky_surf, (0, 0))

        self.screen.blit(self.ground_surf, (0, 300))

        score_surf = self.text_to_surface_mf(f'Score: {int(min(self.score, 137))}', True, (255, 0, 250))

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

        self.screen.blit(self.poroh, (650, 50))

        if time_pass_ms < 1200:
            if time_pass_ms < 600:
                _alpha = 255
            else:
                _alpha = int(255 * math.sin((1200-time_pass_ms)/400))
            self.poroh_banner.set_alpha(_alpha)

            self.screen.blit(self.poroh_banner, (0, 0))

        # checks ending time

        if self.progress.get('all speeches', False):
            speech_number = 4
        elif self.progress.get('both speeches', False):
            speech_number = 3
        elif self.progress.get('color_blind_unlocked', False):
            speech_number = 2
        else:
            speech_number = 1

        if (time_pass_ms > 600 and speech_number == 4) or \
           (time_pass_ms > 30700 and speech_number == 3) or \
           (time_pass_ms > 11500 and speech_number == 2) or \
           (time_pass_ms > 10700 and speech_number == 1):
            self.game_state = self.GameState.NO_KILL_MENU
            if speech_number == 1:
                self.progress['color_blind_unlocked'] = True
            elif speech_number == 2:
                self.progress['both speeches'] = True
            if speech_number == 3:
                self.progress['all speeches'] = True
            save(self.progress)
            self.music_handler.music_play(self.pacifist_menu_music)

    def pacifist_menu(self):
        _color = self.sky_color.return_color()

        self.screen.fill(_color)
        self.screen.blit(self.no_kill_menu, (0, 0))

        new_game_line = 'Good Ending!'
        new_game_surf = self.text_to_surface_mf(new_game_line, True, (255, 0, 250), size=65)
        new_game_rect = new_game_surf.get_rect(center=(400, 50))

        self.screen.blit(new_game_surf, new_game_rect)

        new_game_line = 'World Peace!!'
        new_game_surf = self.text_to_surface_mf(new_game_line, True, (255, 0, 250), size=65)
        new_game_rect = new_game_surf.get_rect(center=(400, 350))

        self.screen.blit(new_game_surf, new_game_rect)

        inc = self.delta_time * 60 / 4000
        self.sky_color.increment(inc)


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
            if self.endless:
                self.progress['endless_highscore'] = max(self.progress.get('endless_highscore', 0), int(self.score))

            if self.score >= 110:
                self.progress['achieved 110'] = True
            self.progress['deaths'] = self.progress.get('deaths', 0) + 1
            if self.progress['deaths'] > 6:
                self.progress['bear'] = True
            self.progress['kills'] = self.progress.get('kills', 0) + self.kills
            if self.progress['kills'] > 100:
                self.progress['tiger'] = True

            save(self.progress)

    def runner_completed(self):
        return self.progress.get('sralker_unlocked', False) and \
               self.progress.get('rooster_finished', False) and \
               self.progress.get('bear_finished', False) and \
               self.progress.get('tiger_finished', False) and \
               self.progress.get('zebra_finished', False) and \
               self.progress.get('frog_finished', False) and \
               self.progress.get('all speeches', False)

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
            else:
                if (self.endless or self.game_state == self.GameState.FROG_GAME) and random.randint(1, 8) == 8:
                    a = Toad(self)
                    a.rect.bottomleft = (random.randint(self.enemy_placement_range[0],
                                                        self.enemy_placement_range[1]), 300)
                    a.set_speed(v_x=-1 * random.randint(100, 150))
                else:
                    a = Snail(self)
                    a.rect.bottomleft = (random.randint(self.enemy_placement_range[0],
                                                        self.enemy_placement_range[1]), 300)
                    a.set_speed(v_x=-1 * random.randint(self.snail_speed_range[0], self.snail_speed_range[1]))

            self.enemy_group.add(a)
            del a

    def enemy_collision(self) -> bool:
        collisions = pygame.sprite.spritecollide(self.player_sprite, self.enemy_group, False)
        result = False
        for i in collisions:
            if not isinstance(i, Toad):
                result = True
            else:
                self.player_sprite.get_toaded()
                i.mask.kill()
                i.kill()
        return result

    def weapon_collision(self):
        for weapon in self.player_attachments:
            if isinstance(weapon, Punch) and self.mask_sprite.punch_status == 'active':
                collisions = pygame.sprite.spritecollide(weapon, self.enemy_group, False)
                if collisions:
                    self.punch_sound.play()
                for i in collisions:
                    self.score_add(f'{i.get_type()}_kill')
                    i.mask.kill()
                    i.kill()

            if isinstance(weapon, Stomp) and self.mask_sprite.type_ in ['tiger', 'frog'] \
                and self.player_sprite.speed[1] > STOMP_SPEED:
                collisions = pygame.sprite.spritecollide(weapon, self.enemy_group, False)
                for i in collisions:
                    self.score_add(f'{i.get_type()}_kill')
                    self.mask_sprite.punch_status = 'cooldown'
                    self.mask_sprite.punch_used = pygame.time.get_ticks() - 165 - int(2.5 * self.score)
                    if isinstance(i, Snail) and self.game_state != self.GameState.COLOR_BLIND:
                        self.enemy_attachments.add(Stomped_Snail(self, [self.player_sprite.rect.centerx, 300]))
                    i.mask.kill()
                    i.kill()

                    self.mask_sprite.stomps += 1

            if not isinstance(weapon, Weapon):
                continue
            if weapon.speed == [0, 0]:
                continue
            collisions = pygame.sprite.spritecollide(weapon, self.enemy_group, False)
            for i in collisions:
                self.score_add(f'{i.get_type()}_kill')
                i.mask.kill()
                i.kill()

            if collisions and self.mask_sprite.type_ not in ['tiger', 'frog']:
                weapon.kill()
                self.punch_sound.play()

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

    def shoot_at_enemy(self, event_pos):
        return self.enemy_group.get_sprites_at(event_pos)

    def draw_shot_after_image(self):
        for index, i in enumerate(self.gunshot_afterimage):
            if self.player_sprite.weapon and i[1] > 0.0:
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
            case self.GameState.DEFAULT_GAME | self.GameState.BEAR_GAME | self.GameState.ZEBRA_GAME | self.GameState.TIGER_GAME:
                if int(self.score) < 20:
                    self.jump_tip.set_alpha(100-5*int(self.score))
                    self.move_tip.set_alpha(100-5*int(self.score))
                    self.shoot_tip.set_alpha(100 - 5 * int(self.score))
                    self.pickup_tip.set_alpha(100-5*int(self.score))
                    self.dash_tip.set_alpha(100-5*int(self.score))
                    self.screen.blit(self.jump_tip, (615, 25))
                    self.screen.blit(self.move_tip, (615, 45))
                    self.screen.blit(self.shoot_tip, (615, 65))
                    self.screen.blit(self.pickup_tip, (615, 85))
                    if self.game_state == self.GameState.ZEBRA_GAME:
                        self.screen.blit(self.dash_tip, (615, 105))
            case self.GameState.FIRST_GAME:
                if int(self.score) < 20:
                    self.jump_tip.set_alpha(100 - 5 * int(self.score))
                    self.screen.blit(self.jump_tip, (615, 25))

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
        if not (self.kills > 0 or self.endless):
            return None
        for i in range(self.player_sprite.max_jumps):
            if i < self.player_sprite.jumps:
                _image = self.jump_on
            else:
                _image = self.jump_off
            self.screen.blit(_image, (20 + i*55, 330))

    def draw_spec_abilities(self):
        if self.mask_sprite.type_ in ['bear', 'frog'] and self.mask_sprite.bear_activation_time is not None:
            self.mask_sprite.image.set_alpha(0)
            _alpha = int(255 * math.sin(1 + (600 - self.mask_sprite.bear_activation_time)/300))
            self.bear_banner.set_alpha(_alpha)
            self.mask_sprite.bear_activation_time -= self.delta_time
            self.screen.blit(self.bear_banner, (0, 0))
            if self.mask_sprite.bear_activation_time < 0:
                self.mask_sprite.bear_activation_time = None
        else:
            self.mask_sprite.bear_activation_time = None

        if self.mask_sprite.type_ in ['zebra', 'frog']:
            _dash_cd_text = ''
            self.dash.set_alpha(255)
            if self.mask_sprite.dash_status != 'ready':
                _dash_cd_text = str(round(self.mask_sprite.dash_cd()/1000, 1))
                self.dash.set_alpha(125)
            _dash_cd_surf = self.text_to_surface_mf(_dash_cd_text, True, (255, 255, 255), size=60)
            _dash_cd_rect = _dash_cd_surf.get_rect(center=(48, 60))
            self.screen.blit(self.dash, (20, 30))
            self.screen.blit(_dash_cd_surf, _dash_cd_rect)

        if self.mask_sprite.type_ in ['tiger', 'frog'] and self.player_sprite.weapon is None:
            _punch_cd_text = ''
            self.punch.set_alpha(255)
            if self.mask_sprite.punch_status != 'ready':
                _punch_cd_text = str(round(self.mask_sprite.punch_cd()/1000, 1))
                self.punch.set_alpha(125)
            _punch_cd_surf = self.text_to_surface_mf(_punch_cd_text, True, (255, 255, 255), size=60)
            _punch_cd_rect = _punch_cd_surf.get_rect(center=(710, 360))
            self.screen.blit(self.punch, (685, 335))
            self.screen.blit(_punch_cd_surf, _punch_cd_rect)

    def draw_titles(self, time_pass):
        if time_pass > 223000:
            _alpha = int(pygame.math.clamp((time_pass - 223000) * 255 // 1300, 0, 255))
            self.squidward_banner.set_alpha(_alpha)
            self.screen.blit(self.squidward_banner, (0, 0))
        if self.titles is None or self.titles == []:
            return
        current_title = self.titles[0]
        if time_pass > current_title[0]:  # pora
            top_text_surf = self.text_to_surface_mf(current_title[2], True, '#0cf3ab', size=60)
            bottom_text_surf = self.text_to_surface_mf(current_title[3], True, '#F30C54', size=52)
            _alpha = 255
            if time_pass - current_title[0] < 800:
                _alpha = pygame.math.clamp((time_pass - current_title[0]) * 255 // 800, 0, 255)
            elif current_title[1] - time_pass < 1200:
                _alpha = pygame.math.clamp((current_title[1] - time_pass) * 255 // 1200, 0, 255)
            top_text_surf.set_alpha(_alpha)
            bottom_text_surf.set_alpha(_alpha)
            top_text_rect = top_text_surf.get_rect(center=(400, 175))
            bottom_text_rect = bottom_text_surf.get_rect(center=(400, 275))
            self.screen.blit(top_text_surf, top_text_rect)
            self.screen.blit(bottom_text_surf, bottom_text_rect)
        if time_pass > current_title[1]:
            self.titles.pop(0)

    def draw_menu_ui(self):
        self.UI_epilepsy.update()
        self.UI_epilepsy.draw(self.screen)

        if self.progress.get('color_blind_unlocked', False):
            self.UI_colorblind.update()
            self.UI_colorblind.draw(self.screen)

        if self.progress.get('sralker_unlocked', False):
            self.UI_endless.update()
            self.UI_endless.draw(self.screen)


    def difficulty_scaling(self):
        if (self.kills > 0 or self.endless) and int(self.score) != self.last_rescale_score:
            if self.endless:
                _score = min(110 + 27*bool(self.advanced_enemies), int(self.score))
            else:
                _score = min(137, int(self.score))
            self.ground_stiffness = GROUND_STIFFNESS * (131 - _score)/137

            self.player_sprite.max_jumps = 1 + _score//(30 + 5*self.mask_sprite.stomps)

            self.max_ammo = MAX_AMMO_CAPACITY - int(_score)//6
            self.pickup_rate = PICKUP_DROP_RATE - int(_score)//10

            self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 7 * int(_score) \
                                        - 50 * bool(self.advanced_enemies and (self.game_state != self.GameState.BEAR_GAME
                                                                               or self.mask_sprite.deflect))

            self.enemy_placement_range = [ENEMY_PLACEMENT_RANGE[0], ENEMY_PLACEMENT_RANGE[1] - int(_score)]
            self.fly_y_range = [FLY_Y_RANGE[0] - int(_score)//2, FLY_Y_RANGE[1] + int(_score)]
            self.snail_speed_range = [SNAIL_SPEED_RANGE[0] + 50 + int(_score), SNAIL_SPEED_RANGE[1] + 2*int(_score)]
            self.fly_speed_range = [FLY_SPEED_RANGE[0] + 50 + int(_score), FLY_SPEED_RANGE[1] + 2*int(_score)]

            self.last_rescale_score = int(self.score)

    def enter_the_sandman(self):
        if self.endless:
            now = pygame.time.get_ticks()
            if (now - self.run_start_time) % 90000 >= 60000:
                if not self.advanced_enemies:
                    if self.game_state == self.GameState.TIGER_GAME:
                        self.mask_sprite.image = self.tiger_mask_worn
                    self.kill_run_init_sound.play()
                    boss_music_list = [self.enter_the_sandman_music,
                                       self.enter_the_siemen_music]
                    if self.progress.get('all speeches', False):
                        boss_music_list.append(self.enter_the_sweden_music)
                    boss_music = random.choice(boss_music_list)
                    self.music_handler.music_play(boss_music)
                self.advanced_enemies = True
                self.sky_is_over = True
            else:
                if self.advanced_enemies:
                    if self.game_state == self.GameState.TIGER_GAME:
                        self.mask_sprite.image = pygame.transform.scale(self.tiger_mask_normal, (90, 80))
                    self.kill_run_init_sound.play()
                    self.choose_music(self.mask_sprite.type_)

                self.advanced_enemies = False
                self.sky_is_over = False
            return

        if not self.advanced_enemies and self.kills > 0 and int(self.score) >= 110:
            if not self.advanced_enemies:
                if self.game_state == self.GameState.TIGER_GAME:
                    self.mask_sprite.image = self.tiger_mask_worn
                self.kill_run_init_sound.play()
                boss_music_list = [self.enter_the_sandman_music,
                                            self.enter_the_siemen_music]
                if self.progress.get('all speeches', False):
                    boss_music_list.append(self.enter_the_sweden_music)
                boss_music = random.choice(boss_music_list)
                self.music_handler.music_play(boss_music)
            self.advanced_enemies = True
            self.sky_is_over = True  # I don't wanna see you go
        elif not self.kills > 0:
            if int(self.score) >= 110:
                self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 500
            elif self.harder_mode:
                self.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 300

    def text_to_surface_mf(self, text, antialias, color, bg=None, size=50):
        _font = pygame.font.Font(self.main_font, size)
        return _font.render(text, antialias, color, bg)

    def text_to_surface_jf(self, text, antialias, color, bg=None, size=50):
        _font = pygame.font.Font(self.japan_font, size)
        return _font.render(text, antialias, color, bg)

    def score_add(self, mode: str):
        if self.game_state in [self.GameState.COLOR_BLIND, self.GameState.DEFAULT_MENU]:
            return
        if mode.endswith('kill'):
            if self.kills == 0:
                self.kill_run_init_sound.play()
            self.kills += 1
        if self.endless:
            match mode:
                case 'snail_kill':
                    self.score += 1.4 - 1.0 * bool(self.advanced_enemies)
                case 'fly_kill':
                    self.score += 3.4 + 3.6 * bool(self.advanced_enemies)
                case 'pass':
                    self.score += 2.0 - 0.9 * bool(self.advanced_enemies)
        elif not self.progress.get('achieved 110', False) and not self.advanced_enemies:
            # never achieved 110 and not sandman
            match mode:
                case 'snail_kill':
                    self.score += 2.0
                case 'fly_kill':
                    self.score += 3.0
                case 'pass':
                    self.score += 1.0
        elif self.progress.get('achieved 110', False) and not self.advanced_enemies:
            if self.score < 110:
                # non sandman, 110 was achieved, score < 110
                match mode:
                    case 'snail_kill':
                        self.score += 3.9
                    case 'fly_kill':
                        self.score += 4.9
                    case 'pass':
                        self.score += 3.2
            else:
                # non sandman, 110 was achieved, score > 110
                match mode:
                    case 'snail_kill':
                        self.score += 1.0
                    case 'fly_kill':
                        self.score += 1.0
                    case 'pass':
                        self.score += 0.6
                        if self.progress.get('color_blind_unlocked', False) is False:
                            self.score += self.progress.get('deaths', 0) / 50
        else:
            # boss mode
            match mode:
                case 'snail_kill':
                    self.score += 0.5 * bool(self.endless)
                case 'fly_kill':
                    self.score += 1.0 + 1.0 * bool(self.endless)
                case 'pass':
                    self.score += 0.25
                    if self.progress.get('zebra', False) is False:
                        self.score += self.progress.get('deaths', 0) / 50


if __name__ == '__main__':
    pass
