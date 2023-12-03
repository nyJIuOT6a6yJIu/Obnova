import math
import random
from enum import Enum, auto
from datetime import datetime
from json import dumps

import pygame

from R_Game.scripts.snail_sprite import Snail, DogMask
from R_Game.scripts.fly_sprite import Fly, OwlMask, Bat, BatMask

from R_Game.scripts.player_sprite import Player, Punch, Weapon, Stomp, Mask

from R_Game.config.subtitles import SUBTITLES
from R_Game.config.config import (STOMP_SPEED,
                                  GRAVITY_ACCELERATION,
                                  GROUND_STIFFNESS,
                                  ENEMY_SPAWN_INTERVAL_MS,
                                  ENEMY_PLACEMENT_RANGE,
                                  FLY_Y_RANGE,
                                  SNAIL_SPEED_RANGE,
                                  FLY_SPEED_RANGE,
                                  MAX_AMMO_CAPACITY,
                                  PICKUP_DROP_RATE)

class CB_Snail(Snail):
    def __init__(self, touhou, center=None, speed=None):
        self.source = touhou
        super().__init__(touhou.game, direct_init=False)
        self.anim_frames = [touhou.snail_1, touhou.snail_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index][touhou.color]
        self.rect = self.image.get_rect()
        self.center = center or [0.0, 0.0]
        self.speed = speed or [0, 0]

        self.mask_bool = not touhou.maskless_enemies
        self.mask = CB_DogMask(self)
        self.game.enemy_attachments.add(self.mask)

    def _animate(self):
        self.anim_index += 3.6 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)][self.source.color]


class CB_DogMask(DogMask):
    def __init__(self, _body):
        super().__init__(_body, direct_init=False)
        self.images = _body.source.snail_mask
        self.image = self.images[_body.source.color]
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.image = self.images[self.body.source.color]
        super().update()


class CB_Fly(Fly):
    def __init__(self, touhou, center=None, speed=None):
        self.source = touhou
        super().__init__(touhou.game, direct_init=False)
        self.anim_frames = [touhou.fly_1, touhou.fly_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index][touhou.color]
        self.rect = self.image.get_rect()
        self.center = center or [0.0, 0.0]
        self.speed = speed or [0, 0]

        self.mask_bool = not touhou.maskless_enemies
        self.mask = CB_OwlMask(self)
        self.game.enemy_attachments.add(self.mask)

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)][self.source.color]


class CB_OwlMask(OwlMask):
    def __init__(self, _body):
        super().__init__(_body, direct_init=False)

        self.images = _body.source.owl_mask
        self.image = self.images[_body.source.color]
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.image = self.images[self.body.source.color]
        super().update()


class CB_Bat(Bat):
    def __init__(self, touhou, center=None, speed=None):
        self.source = touhou
        super().__init__(touhou.game, direct_init=False)
        self.anim_frames = [touhou.fly_1, touhou.fly_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index][touhou.color]
        self.rect = self.image.get_rect()
        self.center = center or [0.0, 0.0]
        self.speed = speed or [0, 0]

        self.mask_bool = not touhou.maskless_enemies
        self.mask = CB_OwlMask(self)
        self.game.enemy_attachments.add(self.mask)

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)][self.body.source.color]


class CB_BatMask(BatMask):
    def __init__(self, _body):
        super().__init__(_body, direct_init=False)

        self.images = _body.source.bat_mask
        self.image = self.images[_body.source.color]
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.image = self.images[self.body.source.color]
        super().update()


class CB_Player(Player):
    def __init__(self, touhou, center=None):
        super().__init__(touhou.game, direct_init=False)
        self.source = touhou
        self.anim_frames = [touhou.player_walk_1,
                            touhou.player_walk_2,
                            touhou.player_jump]
        self.anim_index = 0

        self.image = self.anim_frames[self.anim_index][touhou.color]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.center = center or [0.0, 0.0]

    def _animate(self):
        if self.rect.bottom < 300:
            self.image = self.anim_frames[2][self.source.color]
        elif abs(self.speed[0]) >= 60:
            self.anim_index += 9 * self.game.delta_time / 1000
            if self.anim_index >= 2:
                self.anim_index = 0
            self.image = self.anim_frames[int(self.anim_index)][self.source.color]
        else:
            self.anim_index = 0
            self.image = self.anim_frames[self.anim_index][self.source.color]


class CB_Mask(Mask):
    def __init__(self, _player, _type):
        super().__init__(_player, _type, False)
        self.punch_sprite = Punch(_player)

        _player.game.player_attachments.add(self.punch_sprite)

        self.stomp_sprite = None
        self.stomps = 0

        if _type == 'rooster':
            self.images = _player.source.rooster_mask
            self.image = self.images[_player.source.color]
        elif _type == 'bear':
            self.deflect = True
            self.images = _player.source.bear_mask
            self.images[0].set_alpha(255)
            self.images[1].set_alpha(255)
            self.image = self.images[_player.source.color]

        elif _type == 'zebra':
            self.images = _player.source.zebra_mask
            self.image = self.images[_player.source.color]
            self.dash_status = 'ready'
            self.dash = self.dash_process
        elif _type == 'tiger':
            self.images = _player.source.tiger_mask
            self.image = self.images[_player.source.color]
            self.punch_status = 'ready'
            self.punch = self.punch_process

            self.stomp_sprite = CB_Stomp(_player)
            _player.game.player_attachments.add(self.stomp_sprite)
            _player.game.player_attachments.change_layer(self.stomp_sprite, 1)
        else:
            self.images = [pygame.surface.Surface((90, 95)), pygame.surface.Surface((90, 95))]
            self.image = self.images[_player.source.color]
            self.image.set_alpha(0)

        self.type_ = _type
        self.rect = self.image.get_rect()
        self.body = _player
        _player.mask = self

    def deflect_ability(self):
        self.bear_activation_time = 600
        for enemy in self.body.game.enemy_group:
            self.body.game.score_add(f'{enemy.get_type()}_kill')
            enemy.mask.kill()
            enemy.kill()
            # self.body.game.kill_run = True

    def dash_cd(self):
        return 1300 + self.dash_used - pygame.time.get_ticks()

    def punch_process(self):
        if self.punch_used is None:
            return
        _now = pygame.time.get_ticks()
        _time_spent = _now - self.punch_used
        _final = 160 + int(2.5 * self.body.game.score)*bool(self.body.game.kills)
        _time_by_punch = _time_spent % 160

        if _time_by_punch < 40:
            self.punch_sprite.image = self.body.source.punch_1[self.body.source.color]
        elif _time_by_punch < 60:
            self.punch_sprite.image = self.body.source.punch_2[self.body.source.color]
        elif _time_by_punch < 100:
            self.punch_sprite.image = self.body.source.punch_3[self.body.source.color]
        elif _time_by_punch < 120:
            self.punch_sprite.image = self.body.source.punch_4[self.body.source.color]
        elif _time_by_punch < 160:
            self.punch_sprite.image = self.body.source.punch_5[self.body.source.color]
        if _time_spent > _final:
            self.punch_status = 'cooldown'
            self.punch_sprite.image = self.punch_sprite.default_image
        if self.punch_cd() <= 0:
            self.punch_status = 'ready'
            self.punch_used = None

    def punch_cd(self):
        return 950 - self.body.game.score + self.punch_used - pygame.time.get_ticks()

    def update(self):
        self.image = self.images[self.body.source.color]
        super().update()


class CB_Stomp(Stomp):
    def __init__(self, _body):
        super().__init__(_body, False)

        self.images = _body.source.stomp_image
        self.images[0].set_alpha(0)
        self.images[1].set_alpha(0)

        self.image = self.images[_body.source.color]

        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.image = self.body.source.stomp_image[self.body.source.color]
        super().update()


class CB_Weapon(Weapon):
    def __init__(self, touhou, pos=None):
        super().__init__(touhou.game, pos, False)
        self.og_images = touhou.game.gun_image
        self.image = self.og_images[touhou.color]
        self.rect = self.image.get_rect()
        if pos:
            self.rect.midbottom = pos

    def shoot_at(self, shot):
        if shot:
            for enemy in shot:
                self.game.score_add(f'{enemy.get_type()}_kill')
                enemy.mask.kill()
                enemy.kill()

            self.game.gunshot_afterimage.append([pygame.mouse.get_pos(), 100.0])

            self.ammo -= 1

    def rotate(self):
        self.angle += -15
        self.image = pygame.transform.rotozoom(self.og_image[self.body.source.color], self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

class Touhou:
    def __init__(self, game):
        self.game = game
        self.load_images()
        self.music = pygame.mixer.Sound('R_Game/audio/misc music/color_blind.mp3')
        self.color = 1  # 0 - black character, 1 - white character

        self.start = None

        self.sky_surf = pygame.Surface((800, 300))
        self.ground_surf = pygame.Surface((800, 100))
        self.foreground = pygame.Surface((800, 300))

        self.score = 0
        self.delta_time = 1

        self.player_mask = None

        self.sky_is_over = False
        self.maskless_enemies = True

    def load_images(self):
        path = 'R_Game/graphics/color_blind_images/'
        self.ammo_icon      = [pygame.image.load(path + 'ammo_white.png'), pygame.image.load(path + 'ammo_black.png')]
        self.dash_icon      = [pygame.image.load(path + 'dash_black.png'), pygame.image.load(path + 'dash_white.png')]
        self.jump_off_icon  = [pygame.image.load(path + 'jump_off_white.png'), pygame.image.load(path + 'jump_off_black.png')]
        self.jump_on_icon   = [pygame.image.load(path + 'jump_on_white.png'), pygame.image.load(path + 'jump_on_black.png')]
        self.oob_pointer    = [pygame.image.load(path + 'oob_pointer_black.png'), pygame.image.load(path + 'oob_pointer_white.png')]
        self.punch_icon     = [pygame.image.load(path + 'punch_white.png'), pygame.image.load(path + 'punch_black.png')]

        self.bat_mask  = [pygame.transform.scale(pygame.image.load(path + 'Bat_black.png'), (35, 45)),
                          pygame.transform.scale(pygame.image.load(path + 'Bat_white.png'), (35, 45))]
        self.owl_mask  = [pygame.transform.scale(pygame.image.load(path + 'owl_black.png'), (35, 45)),
                          pygame.transform.scale(pygame.image.load(path + 'owl_white.png'), (35, 45))]
        self.fly_1     = [pygame.image.load(path + 'Fly1_black.png'), pygame.image.load(path + 'Fly1_white.png')]
        self.fly_2     = [pygame.image.load(path + 'Fly2_black.png'), pygame.image.load(path + 'Fly2_white.png')]

        self.dog_mask = [pygame.transform.scale(pygame.image.load(path + 'dog_black.png'), (35, 45)),
                         pygame.transform.scale(pygame.image.load(path + 'dog_white.png'), (35, 45))]
        self.snail_1  = [pygame.image.load(path + 'snail1_black.png'), pygame.image.load(path + 'snail1_white.png')]
        self.snail_2  = [pygame.image.load(path + 'snail2_black.png'), pygame.image.load(path + 'snail2_white.png')]
        self.stomped  = [pygame.image.load(path + 'stomped_black.png'), pygame.image.load(path + 'stomped_white.png')]

        self.bear_mask    = [pygame.transform.scale(pygame.image.load(path + 'bear_black.png'), (90, 80)),
                             pygame.transform.scale(pygame.image.load(path + 'bear_white.png'), (90, 80))]
        self.rooster_mask = [pygame.transform.scale(pygame.image.load(path + 'rooster_black.png'), (90, 95)),
                             pygame.transform.scale(pygame.image.load(path + 'rooster_white.png'), (90, 95))]
        self.tiger_mask   = [pygame.transform.scale(pygame.image.load(path + 'tiger_black.png'), (96, 80)),
                             pygame.transform.scale(pygame.image.load(path + 'tiger_white.png'), (96, 80))]
        self.zebra_mask   = [pygame.transform.scale(pygame.image.load(path + 'zebra_black.png'), (96, 90)),
                             pygame.transform.scale(pygame.image.load(path + 'zebra_white.png'), (96, 90))]
        self.gun_image    = [pygame.transform.scale(pygame.image.load(path + 'GUN_black.png'), (120, 60)),
                             pygame.transform.scale(pygame.image.load(path + 'GUN_white.png'), (120, 60))]

        self.player_jump   = [pygame.image.load(path + 'jump_black.png'), pygame.image.load(path + 'jump_white.png')]
        self.player_walk_1 = [pygame.image.load(path + 'player_walk_1_black.png'), pygame.image.load(path + 'player_walk_1_white.png')]
        self.player_walk_2 = [pygame.image.load(path + 'player_walk_2_black.png'), pygame.image.load(path + 'player_walk_2_white.png')]

        self.punch_1 = [pygame.image.load(path + 'punch_1_black.png'), pygame.image.load(path + 'punch_1_white.png')]
        self.punch_2 = [pygame.image.load(path + 'punch_1-5_black.png'), pygame.image.load(path + 'punch_1-5_white.png')]
        self.punch_3 = [pygame.image.load(path + 'punch_2_black.png'), pygame.image.load(path + 'punch_2_white.png')]
        self.punch_4 = [pygame.image.load(path + 'punch_2-5_black.png'), pygame.image.load(path + 'punch_2-5_white.png')]
        self.punch_5 = [pygame.image.load(path + 'punch_3_black.png'), pygame.image.load(path + 'punch_3_white.png')]

        self.stomp_image = [pygame.image.load(path + 'stomp_black.png'), pygame.image.load(path + 'stomp_white.png')]

    def set_up_run(self):
        self.subtitles = SUBTITLES

        self.sky_surf.fill('Black')
        self.ground_surf.fill('White')
        self.foreground.fill('Black')

        self.game.max_ammo = MAX_AMMO_CAPACITY
        self.game.pickup_rate = PICKUP_DROP_RATE  # percentage chance
        self.game.pickups = pygame.sprite.LayeredUpdates()

        self.game.player = pygame.sprite.GroupSingle()
        self.game.player_sprite = CB_Player(self)
        self.game.player.add(self.game.player_sprite)

        self.game.player_attachments = pygame.sprite.LayeredUpdates()

        self.game.mask_sprite = CB_Mask(self.game.player_sprite, None)
        self.game.player_attachments.add(self.game.mask_sprite)

        self.game.enemy_spawn = None #[None, None, 'snail', 'snail', 'fly', 'snail', None]


        self.game.enemy_group = pygame.sprite.LayeredUpdates()
        self.game.enemy_attachments = pygame.sprite.LayeredUpdates()

        self.score = 0

        self.game.gunshot_afterimage = []

        self.game.delta_time = 0
        self.game.last_time_frame = pygame.time.get_ticks()
        self.game.last_rescale_score = None

        self.game.gravity_acceleration = GRAVITY_ACCELERATION
        self.game.ground_stiffness = GROUND_STIFFNESS

        self.game.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS

        pygame.time.set_timer(self.game.enemy_spawn_timer, self.game.enemy_spawn_interval, 1)

        self.game.enemy_placement_range = ENEMY_PLACEMENT_RANGE
        self.game.fly_y_range = FLY_Y_RANGE
        self.game.snail_speed_range = SNAIL_SPEED_RANGE
        self.game.fly_speed_range =  FLY_SPEED_RANGE

        self.sky_is_over = False  # Even though we can't afford

        self.game.screen.fill('White')

        self.game.music_handler.music_play(self.music)

    def runtime_frame(self):
        now = pygame.time.get_ticks()

        time_pass = now - self.start

        self.game.screen.blit(self.ground_surf, (0, 300))

        if time_pass < 4000:
            y = (time_pass)//10
            self.game.screen.blit(self.sky_surf, (0, y-400))
        else:
            self.game.screen.blit(self.sky_surf, (0, 0))

        if time_pass > 14990 and time_pass < 20000:
            self.change_color(0)
            self.change_mask('rooster')

        elif time_pass > 42990 and time_pass < 45000:
            self.change_color(1)
            self.change_mask('bear')

        elif time_pass > 69990 and time_pass < 73000:
            self.change_mask('tiger')

        elif time_pass > 84990 and time_pass < 88000:
            self.change_color(0)

        elif time_pass > 97990 and time_pass < 100000:
            self.change_mask('zebra')

        elif time_pass > 110990 and time_pass < 115000:
            self.change_color(1)

        elif time_pass > 130990 and time_pass < 133000:
            self.change_mask('tiger')

        elif time_pass > 166990 and time_pass < 170000:
            self.change_mask('bear')

        elif time_pass > 180990 and time_pass < 185000:
            self.change_color(0)
            self.change_mask('rooster')

        elif time_pass > 194990 and time_pass < 198000:
            self.change_color(1)

        elif time_pass > 209990 and time_pass < 212000:
            self.change_color(0)
            self.change_mask('None')

        self.game.player.update()
        self.game.player_attachments.update()
        self.game.player.draw(self.game.screen)
        self.game.player_attachments.draw(self.game.screen)

        self.game.enemy_group.update()
        self.game.enemy_group.draw(self.game.screen)

        self.game.enemy_attachments.update()
        self.game.enemy_attachments.draw(self.game.screen)

        self.game.pickups.update()
        self.game.pickups.draw(self.game.screen)

        self.draw_subtitles(time_pass)

        self.game.weapon_collision()
    #
    # game.draw_laser_sight()
    # game.draw_shot_after_image()
    # game.draw_out_of_bounds_marker()
    # game.draw_tool_tips()
    # game.draw_ammo_count()
    # game.draw_jumps_count()
    # game.draw_spec_abilities()
    #
    # game.difficulty_scaling()
    # game.enter_the_sandman()
    #
        if self.game.mask_sprite.dash_status != 'active' \
                and not (self.game.mask_sprite.dash_status == 'cooldown' and self.game.player_sprite.is_airborne()) \
                and self.game.enemy_collision():
            if self.game.mask_sprite.deflect:
                self.game.mask_sprite.deflect = False
                self.game.mask_sprite.deflect_ability()
            else:
                self.game.game_state = self.game.GameState.DEFAULT_MENU

        self.game.game_over()


    #
    # if game.sky_is_over or game.mask_sprite.dash_status == 'active':
    #     game.sky_color_foreground.set_alpha(max(int(game.score) - 50, 60))
    #     game.ground_surf.set_alpha(max(365 - 3 * int(game.score), 50))
    #     game.screen.blit(game.sky_color_foreground, (0, 0))

    def draw_subtitles(self, time_pass):
        if self.subtitles is None or self.subtitles == []:
            return
        current_subtitle = self.subtitles[0]
        if time_pass > current_subtitle[0]: # pora
            jap_text_surf = self.game.text_to_surface_jf(current_subtitle[2], True, ['White', 'Black'][self.color], size=26)
            eng_text_surf = self.game.text_to_surface_mf(current_subtitle[3], True, ['White', 'Black'][self.color], size=36)
            _alpha = 255
            if current_subtitle[1] == 129990 and time_pass - current_subtitle[0] < 800:
                _alpha = pygame.math.clamp((time_pass - current_subtitle[0]) * 255 // 800, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
            if current_subtitle[1] in [110990, 209000] and current_subtitle[1] - time_pass < 1200:
                _alpha = pygame.math.clamp((current_subtitle[1] - time_pass) * 255 // 1200, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
            jap_text_rect = jap_text_surf.get_rect(center=(400, 330))
            eng_text_rect = eng_text_surf.get_rect(center=(400, 370))
            self.game.screen.blit(jap_text_surf, jap_text_rect)
            self.game.screen.blit(eng_text_surf, eng_text_rect)
        if time_pass > current_subtitle[1]:
            self.subtitles.pop(0)

    def change_color(self, new_color):
        if self.color == new_color:
            return
        self.color = new_color
        self.ground_surf.fill(['Black', 'White'][self.color])
        self.sky_surf.fill(['White', 'Black'][self.color])
        self.foreground.fill(['White', 'Black'][self.color])

    def change_mask(self, new_mask):
        if self.game.mask_sprite.type_ == new_mask:
            return
        self.game.mask_sprite.kill()
        self.game.mask_sprite = CB_Mask(self.game.player_sprite, new_mask)
        self.game.player_attachments.add(self.game.mask_sprite)
