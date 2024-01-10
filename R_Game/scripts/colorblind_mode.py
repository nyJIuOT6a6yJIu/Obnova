import math
import random
from enum import Enum, auto
from datetime import datetime
from json import dumps

# TODO:
#  add UI (skill icons and cd)
#  add snow to post sky rooster until color change
#  add spinning girl and leaves
#  add sun
#  add player enlargement (menu sprite)
#  add ending sequence

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
                                  )

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
        self.images = _body.source.dog_mask
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
        self.image = self.anim_frames[int(self.anim_index)][self.source.color]


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

class CB_Leaf(pygame.sprite.Sprite):
    def __init__(self, source, image_index, pos):
        super().__init__()
        self.source = source

        self.source.leaves_sprites.add(self)

        self.og_image = source.leaves[image_index]
        self.image = self.og_image
        self.rect = self.image.get_rect()
        self.rect.midbottom = (pos, -30)

        self.angle = 0

    def rotate(self):
        self.angle += 2  # 180 * self.source.game.delta_time / 1000
        self.image = pygame.transform.rotozoom(self.og_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        self.rotate()
        self.rect.center = (self.rect.centerx, self.rect.centery + 1)
        if self.rect.top > 300:
            self.kill()


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

    def player_input(self, key_pressed, released=False, event_pos=None):
        if key_pressed == 1:
            if self.weapon:
                shot = self.game.shoot_at_enemy(event_pos)
                self.weapon.shoot_at(shot)
            else:
                if self.mask.punch_status == 'ready':
                    self.mask.punch_status = 'active'
                    self.mask.punch_used = pygame.time.get_ticks()
        else:
            super().player_input(key_pressed, released, event_pos)

    def _movement(self):
        gravity_acc = self.game.gravity_acceleration
        stiffness = self.game.ground_stiffness

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        if self.mask.dash_status != 'active':
            self.speed[1] += gravity_acc * self.game.delta_time / 2000

        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.center[1] += self.speed[1] * self.game.delta_time / 1000

        self.rect.center = [int(self.center[0]), int(self.center[1])]

        if not self.is_airborne():
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        elif self.mask.dash_status != 'active':
            self.speed[1] += gravity_acc * self.game.delta_time / 2000  # 1300 - stomp limit

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 780:
            self.rect.right = 780

        if self.mask.dash_status == 'active':
            pass
        else:
            self.speed[0] = -375*bool(self.a_pressed) + 375*bool(self.d_pressed)

        if not self.is_airborne():
            minus = stiffness*self.game.delta_time / 1000
            if abs(self.speed[0]) > abs(minus):
                self.speed[0] -= minus*self.speed[0]/abs(self.speed[0])
            else:
                self.speed[0] = 0

    def pick_up_weapon(self, weapon, event_pos=None):
        if event_pos is not None and self.weapon:
            self.drop_weapon(event_pos)
        self.weapon = weapon
        self.game.pickups.remove(weapon)
        self.game.player_attachments.add(weapon)
        weapon.set_body(self)

    def drop_weapon(self, event_pos):
        if self.weapon:
            self.weapon.body = None
            speed_x = event_pos[0] - self.rect.centerx
            speed_y = event_pos[1] - self.rect.centery
            speed = pygame.math.Vector2((speed_x, speed_y))
            speed = speed.normalize()
            speed_x = speed.x * 30
            speed_y = speed.y * 30
            self.weapon.speed = [speed_x, speed_y]
            self.weapon = None

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

        self.punch = self.punch_process

        if _type == 'rooster':
            self.images = _player.source.rooster_mask
            self.image = self.images[_player.source.color]
        elif _type == 'bear':
            self.deflect = True
            self.images = _player.source.bear_mask
            self.images[0].set_alpha(255)
            self.images[1].set_alpha(255)
            self.image = self.images[_player.source.color]
            self.bear_banner = pygame.Surface((800, 300))
            self.bear_banner.fill('White')

        elif _type == 'zebra':
            self.images = _player.source.zebra_mask
            self.image = self.images[_player.source.color]
            self.dash_status = 'ready'
            self.dash = self.dash_process
        elif _type == 'tiger':
            self.images = _player.source.tiger_mask
            self.image = self.images[_player.source.color]
            self.punch_status = 'ready'

            self.stomp_sprite = CB_Stomp(_player)
            _player.game.player_attachments.add(self.stomp_sprite)
            _player.game.player_attachments.change_layer(self.stomp_sprite, 1)
        else:
            self.images = [pygame.surface.Surface((90, 95)), pygame.surface.Surface((90, 95))]
            self.image = self.images[_player.source.color]
            self.images[0].set_alpha(0)
            self.images[1].set_alpha(0)

        self.type_ = _type
        self.rect = self.image.get_rect()
        self.body = _player
        _player.mask = self

        self.culmination = False

    def deflect_ability(self):
        self.bear_activation_time = 600
        for enemy in self.body.game.enemy_group:
            enemy.mask.kill()
            enemy.kill()
            # self.body.game.kill_run = True

    def dash_cd(self):
        return 1300 + self.dash_used - pygame.time.get_ticks() - 700 * bool(self.culmination)

    def punch_process(self):
        if self.punch_used is None or self.type_ != 'tiger':
            self.punch_sprite.image = self.punch_sprite.default_image
            return
        _now = pygame.time.get_ticks()
        _time_spent = _now - self.punch_used
        _final = 160 + int(2.5 * self.body.source.score)
        _time_by_punch = _time_spent % 160

        if self.punch_status != 'cooldown' and _time_by_punch < 40:
            self.punch_sprite.image = self.body.source.punch_1[self.body.source.color]
        elif self.punch_status != 'cooldown' and _time_by_punch < 60:
            self.punch_sprite.image = self.body.source.punch_2[self.body.source.color]
        elif self.punch_status != 'cooldown' and _time_by_punch < 100:
            self.punch_sprite.image = self.body.source.punch_3[self.body.source.color]
        elif self.punch_status != 'cooldown' and _time_by_punch < 120:
            self.punch_sprite.image = self.body.source.punch_4[self.body.source.color]
        elif self.punch_status != 'cooldown' and _time_by_punch < 160:
            self.punch_sprite.image = self.body.source.punch_5[self.body.source.color]
        if _time_spent > _final:
            self.punch_status = 'cooldown'
            self.punch_sprite.image = self.punch_sprite.default_image
        if self.punch_cd() <= 0:
            self.punch_status = 'ready'
            self.punch_used = None

    def punch_cd(self):
        return 950 - self.body.source.score + self.punch_used - pygame.time.get_ticks()

    def update(self):
        self.image = self.images[self.body.source.color]
        match self.type_:
            case 'rooster':
                self.rect.center = (self.body.rect.midtop[0] + 7, self.body.rect.midtop[1] + 23)
            case 'bear':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
            case 'zebra':
                self.rect.center = (self.body.rect.center[0] + 3, self.body.rect.center[1] - 10)
            case 'tiger':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
            case 'frog':
                self.rect.center = (self.body.rect.midtop[0], self.body.rect.midtop[1] + 23)
        self.dash()
        self.punch()


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
        self.source = touhou
        self.og_images = touhou.gun_image
        self.image = self.og_images[touhou.color]
        self.rect = self.image.get_rect()
        if pos:
            self.rect.midbottom = pos

    def shoot_at(self, shot):
        if self.ammo and shot:
            for enemy in shot:
                enemy.mask.kill()
                enemy.kill()

            self.game.gunshot_afterimage.append([pygame.mouse.get_pos(), 100.0])

            self.ammo -= 1

    def rotate(self):
        self.angle += -15
        self.image = pygame.transform.rotozoom(self.og_images[self.source.color], self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def update(self):
        self.image = self.og_images[self.source.color]
        super().update()


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
        self.overlay = pygame.Surface((800, 400))
        self.foreground.set_alpha(45)

        self.no_surf = pygame.surface.Surface((2, 2))
        self.no_surf.set_alpha(0)

        self.score = 0
        self.last_rescale_score = None

        self.player_mask = None

        self.sky_is_over = False
        self.maskless_enemies = True

    def load_images(self):
        path = 'R_Game/graphics/color_blind_images/'
        self.ammo_icon      = [pygame.transform.scale(pygame.image.load(path + 'ammo_black.png').convert_alpha(), (30, 30)), pygame.transform.scale(pygame.image.load(path + 'ammo_white.png').convert_alpha(), (30, 30))]
        self.jump_off_icon  = [pygame.transform.scale(pygame.image.load(path + 'jump_off_black.png').convert_alpha(), (30, 30)), pygame.transform.scale(pygame.image.load(path + 'jump_off_white.png').convert_alpha(), (30, 30))]
        self.jump_on_icon   = [pygame.transform.scale(pygame.image.load(path + 'jump_on_black.png').convert_alpha(), (30, 30)), pygame.transform.scale(pygame.image.load(path + 'jump_on_white.png').convert_alpha(), (30, 30))]
        self.oob_pointer    = [pygame.image.load(path + 'oob_pointer_black.png').convert_alpha(), pygame.image.load(path + 'oob_pointer_white.png').convert_alpha()]

        self.punch_icon     = [pygame.transform.scale(pygame.image.load(path + 'punch_black.png').convert_alpha(), (50, 50)), pygame.transform.scale(pygame.image.load(path + 'punch_white.png').convert_alpha(), (50, 50))]
        self.dash_icon = [pygame.transform.scale(pygame.image.load(path + 'dash_black.png').convert_alpha(), (50, 50)),
                          pygame.transform.scale(pygame.image.load(path + 'dash_white.png').convert_alpha(), (50, 50))]
        self.shield_icon = [pygame.transform.scale(pygame.image.load(path + 'shield_black.png').convert_alpha(), (50, 50)),
                          pygame.transform.scale(pygame.image.load(path + 'shield_white.png').convert_alpha(), (50, 50))]

        self.bat_mask  = [pygame.transform.scale(pygame.image.load(path + 'Bat_black.png').convert_alpha(), (35, 45)),
                          pygame.transform.scale(pygame.image.load(path + 'Bat_white.png').convert_alpha(), (35, 45))]
        self.owl_mask  = [pygame.transform.scale(pygame.image.load(path + 'owl_black.png').convert_alpha(), (35, 45)),
                          pygame.transform.scale(pygame.image.load(path + 'owl_white.png').convert_alpha(), (35, 45))]
        self.fly_1     = [pygame.image.load(path + 'Fly1_black.png').convert_alpha(),
                          pygame.image.load(path + 'Fly1_white.png').convert_alpha()]
        self.fly_2     = [pygame.image.load(path + 'Fly2_black.png').convert_alpha(),
                          pygame.image.load(path + 'Fly2_white.png').convert_alpha()]

        self.dog_mask = [pygame.transform.scale(pygame.image.load(path + 'dog_black.png').convert_alpha(), (35, 45)),
                         pygame.transform.scale(pygame.image.load(path + 'dog_white.png').convert_alpha(), (35, 45))]
        self.snail_1  = [pygame.image.load(path + 'snail1_black.png').convert_alpha(),
                         pygame.image.load(path + 'snail1_white.png').convert_alpha()]
        self.snail_2  = [pygame.image.load(path + 'snail2_black.png').convert_alpha(),
                         pygame.image.load(path + 'snail2_white.png').convert_alpha()]
        self.stomped  = [pygame.image.load(path + 'stomped_black.png').convert_alpha(),
                         pygame.image.load(path + 'stomped_white.png').convert_alpha()]

        self.bear_mask    = [pygame.transform.scale(pygame.image.load(path + 'bear_black.png').convert_alpha(), (90, 80)),
                             pygame.transform.scale(pygame.image.load(path + 'bear_white.png').convert_alpha(), (90, 80))]
        self.rooster_mask = [pygame.transform.scale(pygame.image.load(path + 'rooster_black.png').convert_alpha(), (90, 95)),
                             pygame.transform.scale(pygame.image.load(path + 'rooster_white.png').convert_alpha(), (90, 95))]
        self.tiger_mask   = [pygame.transform.scale(pygame.image.load(path + 'tiger_black.png').convert_alpha(), (96, 80)),
                             pygame.transform.scale(pygame.image.load(path + 'tiger_white.png').convert_alpha(), (96, 80))]
        self.zebra_mask   = [pygame.transform.scale(pygame.image.load(path + 'zebra_black.png').convert_alpha(), (96, 90)),
                             pygame.transform.scale(pygame.image.load(path + 'zebra_white.png').convert_alpha(), (96, 90))]
        self.gun_image    = [pygame.transform.scale(pygame.image.load(path + 'GUN_black.png').convert_alpha(), (120, 60)),
                             pygame.transform.scale(pygame.image.load(path + 'GUN_white.png').convert_alpha(), (120, 60))]

        self.player_jump   = [pygame.image.load(path + 'jump_black.png').convert_alpha(),
                              pygame.image.load(path + 'jump_white.png').convert_alpha()]
        self.player_walk_1 = [pygame.image.load(path + 'player_walk_1_black.png').convert_alpha(),
                              pygame.image.load(path + 'player_walk_1_white.png').convert_alpha()]
        self.player_walk_2 = [pygame.image.load(path + 'player_walk_2_black.png').convert_alpha(),
                              pygame.image.load(path + 'player_walk_2_white.png').convert_alpha()]
        self.player_stand = [pygame.image.load(path + 'player_stand_black.png').convert_alpha(),
                            pygame.image.load(path + 'player_stand_white.png').convert_alpha()]

        self.punch_1 = [pygame.image.load(path + 'punch_1_black.png').convert_alpha(),
                        pygame.image.load(path + 'punch_1_white.png').convert_alpha()]
        self.punch_2 = [pygame.image.load(path + 'punch_1-5_black.png').convert_alpha(),
                        pygame.image.load(path + 'punch_1-5_white.png').convert_alpha()]
        self.punch_3 = [pygame.image.load(path + 'punch_2_black.png').convert_alpha(),
                        pygame.image.load(path + 'punch_2_white.png').convert_alpha()]
        self.punch_4 = [pygame.image.load(path + 'punch_2-5_black.png').convert_alpha(),
                        pygame.image.load(path + 'punch_2-5_white.png').convert_alpha()]
        self.punch_5 = [pygame.image.load(path + 'punch_3_black.png').convert_alpha(),
                        pygame.image.load(path + 'punch_3_white.png').convert_alpha()]

        self.stomp_image = [pygame.image.load(path + 'stomp_black.png').convert_alpha(),
                            pygame.image.load(path + 'stomp_white.png').convert_alpha()]

        self.leaves = []
        for index in range(1, 9):
            image = pygame.transform.scale(
                pygame.image.load(f"{path}leaves/{index}.png").convert_alpha(), (80, 80)
            )
            self.leaves.append(image)

        self.girl = []
        for index in range(1, 31):
            image = pygame.image.load(f"{path}girl/{index}.png").convert_alpha()
            self.girl.append(image)

    def set_up_run(self):
        self.subtitles = list(i for i in SUBTITLES)
        self.sub_drawn = False

        self.sky_surf.fill('Black')
        self.ground_surf.fill('White')
        self.foreground.fill('Black')

        self.game.max_ammo = MAX_AMMO_CAPACITY
        self.game.pickup_rate = -100
        self.game.pickups = pygame.sprite.LayeredUpdates()

        self.game.player = pygame.sprite.GroupSingle()
        self.game.player_sprite = CB_Player(self)
        self.game.player.add(self.game.player_sprite)

        self.game.player_attachments = pygame.sprite.LayeredUpdates()

        self.game.mask_sprite = CB_Mask(self.game.player_sprite, None)
        self.game.player_attachments.add(self.game.mask_sprite)

        # list(type, spawn time, spawn location, spawn speed, args)
        self.game.enemy_spawn = [['snail', 4500, None, -400, 0], ['snail', 6000, None, -400, 0],
                                 ['fly', 7500, 150, -450, 0],    ['snail', 9000, None, -400, 0]]


        self.game.enemy_group = pygame.sprite.LayeredUpdates()
        self.game.enemy_attachments = pygame.sprite.LayeredUpdates()

        self.leaves_sprites = pygame.sprite.Group()
        self.spin_girl = None

        self.color = 1  # 0 - black character, 1 - white character

        self.start = pygame.time.get_ticks()

        self.foreground.set_alpha(45)

        self.score = 0
        self.last_rescale_score = None

        self.player_mask = None

        self.ability_icon = self.no_surf

        self.sky_is_over = False
        self.maskless_enemies = True

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
        self.overlay.set_alpha(0)

        self.game.screen.fill('White')

        # self.game.music_handler.music_play(self.music)
        pygame.mixer_music.load('R_Game/audio/misc music/color_blind.mp3')
        pygame.mixer_music.play(start=0.0)#83.0)
        self.game.screen.blit(self.ground_surf, (0, 300))

    def runtime_frame(self):
        now = pygame.time.get_ticks()

        time_pass = now - self.start #+ 83000

        if time_pass < 4000:
            y = (time_pass)//10
            self.game.screen.blit(self.sky_surf, (0, y-400))
        else:
            if not self.sky_is_over and self.game.mask_sprite.dash_status != 'active':
                self.game.screen.blit(self.sky_surf, (0, 0))

        if time_pass > 14990 and time_pass < 20000:
            self.change_color(0)
            self.change_mask('rooster')
            self.maskless_enemies = False
            self.score = 29


        elif time_pass > 42990 and time_pass < 45000:
            self.change_color(1)
            self.change_mask('bear')
            self.score = 69  # nice

        elif time_pass > 69990 and time_pass < 73000:
            self.change_mask('tiger')
            self.score = 89

        elif time_pass > 84990 and time_pass < 88000:
            self.change_color(0, True)
            self.change_mask('zebra')

        elif time_pass > 97990 and time_pass < 100000:
            pass
            # self.change_mask('zebra')

        elif time_pass > 109690 and time_pass < 111000:
            if not self.game.enemy_spawn:
                self.game.mask_sprite.culmination = True
                # list(type, spawn time, spawn location, spawn speed, args)
                # TODO: fix difficulty & timings, make speed a variable for easier tinkering
                self.game.enemy_spawn = [['fly', 111900, 140, -750, 0], ['fly', 112300, 140, -720, 0],
                                         ['snail', 112900, 300, -680, 0], ['bat', 113400, 130, -680, 20],
                                         ['snail', 113800, 300, -680, 0], ['bat', 114300, 130, -680, 20],
                                         ['snail', 114600, 300, -680, 0], ['bat', 115100, 130, -680, 20],
                                         ['snail', 115600, 300, -680, 0],# ['fly', 116100, 50, -680, 20],
                                         ['snail', 116100, 300, -680, 0], ['snail', 116400, 300, -680, 20],
                                         ['snail', 117300, 150, -680, 20], ['bat', 117800, 130, -680, 20],
                                         ['snail', 118100, 150, -680, 20], ['bat', 118600, 130, -680, 20],
                                         ['snail', 119000, 150, -680, 20],# ['fly', 119500, 50, -680, 20],
                                         ['snail', 119500, 300, -680, 0], ['snail', 119900, 300, -680, 20],

                                         ['snail', 120700, 300, -680, 0], ['bat', 121200, 130, -680, 20],
                                         ['snail', 121600, 300, -680, 0], ['bat', 122100, 130, -680, 20],
                                         ['snail', 122500, 300, -680, 0], #['fly', 123000, 50, -680, 20],
                                         ['snail', 122300, 300, -680, 0], ['snail', 122680, 300, -680, 20],
                                         ['snail', 123400, 150, -680, 20], ['bat', 123900, 130, -680, 20],
                                         ['snail', 124200, 150, -680, 20], ['bat', 124700, 130, -680, 20],
                                         #['snail', 125100, 150, -680, 20], #['bat', 125600, 130, -680, 20],
                                         ['fly', 125600, 100, -760, 0], ['fly', 125700, 140, -755, 0],
                                         ['fly', 125800, 70, -750, 0], ['fly', 125900, 120, -745, 0],
                                         ['fly', 126000, 80, -740, 0], ['fly', 126050, 60, -735, 0],
                                         ['snail', 126100, 150, -420, 20],

                                         ['leaf', 126700, 670, 0, 7], ['leaf', 126900, 270, 0, 5],
                                         ['leaf', 126600, 134, 0, 0], ['leaf', 127500, 534, 0, 1],
                                         ['leaf', 127800, 400, 0, 2], ['leaf', 128200, 600, 0, 3],
                                         ['leaf', 128500, 730, 0, 4], ['leaf', 128800, 470, 0, 6],
                                         ]

        elif time_pass > 110990 and time_pass < 111390:
            self.change_color(1)
            self.sky_is_over = True
            self.score = 110

        elif time_pass > 125990 and time_pass < 129000:
            self.change_color(0)
            self.change_mask('tiger')  # TODO: do this on collision with spin girl
            self.score = 115

        elif time_pass > 166790 and time_pass < 170000:
            self.change_color(1)
            self.change_mask('bear')
            self.score = 137

        elif time_pass > 180990 and time_pass < 185000:
            self.change_color(0)
            self.sky_is_over = False
            self.change_mask('rooster')
            self.score = 90

        elif time_pass > 194990 and time_pass < 198000:
            self.change_color(1)
            self.score = 95

        elif time_pass > 209990 and time_pass < 212000:
            self.change_color(0)
            self.sky_is_over = True
            self.change_mask('None')
            self.score = 137

        if self.sky_is_over or self.game.mask_sprite.dash_status == 'active':
            self.game.screen.blit(self.foreground, (0, 0))

        if time_pass > 14990 or time_pass < 14490:
            self.game.player.update()
            self.game.player_attachments.update()

            self.game.enemy_group.update()
            self.game.enemy_attachments.update()

            self.game.pickups.update()

        self.game.player.draw(self.game.screen)
        self.game.player_attachments.draw(self.game.screen)

        self.game.enemy_group.draw(self.game.screen)
        self.game.enemy_attachments.draw(self.game.screen)

        self.leaves_sprites.update()
        self.leaves_sprites.draw(self.game.screen)

        self.game.pickups.draw(self.game.screen)

        self.draw_overlay(time_pass=time_pass, transition_time=110990)

        self.draw_subtitles(time_pass)

        self.game.weapon_collision()

        self.spawn_new_enemy(time_pass)

        self.difficulty_scaling()

        self.draw_shot_after_image()

        self.draw_spec_abilities()
        self.draw_out_of_bounds_marker()
        self.draw_ammo_count()
        self.draw_jumps_count()



        if (time_pass <= 110200 and not (time_pass > 84990 and time_pass < 86490)) or time_pass >= 113000:
            if self.game.mask_sprite.dash_status != 'active' \
                    and not (self.game.mask_sprite.dash_status == 'cooldown' and self.game.player_sprite.is_airborne()) \
                    and self.game.enemy_collision():
                if self.game.mask_sprite.deflect:
                    self.game.mask_sprite.deflect = False
                    self.game.mask_sprite.deflect_ability()
                else:
                    self.game.game_state = self.game.GameState.DEFAULT_MENU
                    # self.game.music_handler.music_stop(500)
                    self.game.enemy_spawn = list()
                    pygame.mixer_music.stop()

        self.game.game_over()

    # TODO: dont be lazy, add alpha channel and a-channel restoration on mask set-up
    # TODO: better UI placement
    def draw_spec_abilities(self):
        if self.game.mask_sprite.bear_activation_time is not None:
            _alpha = int(255 * math.sin(1 + (600 - self.game.mask_sprite.bear_activation_time)/300))
            self.ability_icon = self.no_surf
            self.game.mask_sprite.bear_banner.set_alpha(_alpha)
            self.game.mask_sprite.bear_activation_time -= self.game.delta_time
            self.game.screen.blit(self.game.mask_sprite.bear_banner, (0, 0))
            if self.game.mask_sprite.bear_activation_time < 0:
                self.game.mask_sprite.bear_activation_time = None
        else:
            self.game.mask_sprite.bear_activation_time = None

        self.game.screen.blit(self.ability_icon, (390, 10))

        if self.game.mask_sprite.type_ == 'zebra':
            _dash_cd_text = ''
            if self.game.mask_sprite.dash_status != 'ready':
                _dash_cd_text = str(round(self.game.mask_sprite.dash_cd()/1000, 1))
            _dash_cd_surf = self.game.text_to_surface_mf(_dash_cd_text, True, ['Black', 'White'][self.color], size=50)
            _dash_cd_rect = _dash_cd_surf.get_rect(center=(380, 40))
            self.game.screen.blit(self.dash_icon[self.color], (420, 10))
            self.game.screen.blit(_dash_cd_surf, _dash_cd_rect)

        if self.game.mask_sprite.type_ == 'tiger' and self.game.player_sprite.weapon is None:
            _punch_cd_text = ''
            if self.game.mask_sprite.punch_status != 'ready':
                _punch_cd_text = str(round(self.game.mask_sprite.punch_cd()/1000, 1))
            _punch_cd_surf = self.game.text_to_surface_mf(_punch_cd_text, True, ['Black', 'White'][self.color], size=50)
            _punch_cd_rect = _punch_cd_surf.get_rect(center=(380, 40))
            self.game.screen.blit(self.punch_icon[self.color], (420, 10))
            self.game.screen.blit(_punch_cd_surf, _punch_cd_rect)

    def draw_overlay(self, time_pass=None, transition_time=None):
        if time_pass > 110200 and time_pass < 113000:
            _alpha = int(pygame.math.clamp((255 - (255/700)*abs(transition_time - time_pass)), 0, 255))
            self.overlay.set_alpha(_alpha)
            if _alpha:
                self.game.screen.blit(self.overlay, (0, 0))

    def draw_subtitles(self, time_pass):
        if self.subtitles is None or self.subtitles == []:
            return
        current_subtitle = self.subtitles[0]
        if time_pass > current_subtitle[0] and not self.sub_drawn: # pora
            self.sub_drawn = True
            jap_text_surf = self.game.text_to_surface_jf(current_subtitle[2], True, ['White', 'Black'][self.color], size=26)
            eng_text_surf = self.game.text_to_surface_mf(current_subtitle[3], True, ['White', 'Black'][self.color], size=36)
            _alpha = 255

            if current_subtitle[1] == 129990 and time_pass - current_subtitle[0] < 800:
                _alpha = pygame.math.clamp((time_pass - current_subtitle[0]) * 255 // 800, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
                self.game.screen.blit(self.ground_surf, (0, 300))
                self.sub_drawn = False
            if current_subtitle[1] in [110990, 209000] and current_subtitle[1] - time_pass < 1200:
                _alpha = pygame.math.clamp((current_subtitle[1] - time_pass) * 255 // 1200, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
                self.game.screen.blit(self.ground_surf, (0, 300))
                self.sub_drawn = False
            jap_text_rect = jap_text_surf.get_rect(center=(400, 330))
            eng_text_rect = eng_text_surf.get_rect(center=(400, 370))
            self.game.screen.blit(jap_text_surf, jap_text_rect)
            self.game.screen.blit(eng_text_surf, eng_text_rect)
        if time_pass > current_subtitle[1]:
            self.subtitles.pop(0)
            self.sub_drawn = False
            self.game.screen.blit(self.ground_surf, (0, 300))

    def draw_shot_after_image(self):
        for index, i in enumerate(self.game.gunshot_afterimage):
            if i[1] > 0.0:
                pygame.draw.line(self.game.screen, ['Black', 'White'][self.color], (self.game.player_sprite.weapon.rect.midright[0]-8, self.game.player_sprite.weapon.rect.midright[1]-4), i[0],
                             width=int(6 * math.sin(i[1]*math.pi/100.0)))
                i[1] -= 1 + (2 * self.game.delta_time) // 3
            else:
                self.game.gunshot_afterimage.pop(index)

    def draw_out_of_bounds_marker(self):
        if self.game.player_sprite.rect.bottom < -10:
            oob_marker_surf = pygame.transform.scale(self.oob_pointer[self.color], (40, 20))
            oob_marker_rect = oob_marker_surf.get_rect(midtop=(self.game.player_sprite.rect.centerx, 5))

            oob_text_surf = self.game.text_to_surface_mf(f'{-(self.game.player_sprite.rect.bottom - 10)//48}m',
                                                    True, ['Black', 'White'][self.color], size=32)
            oob_text_rect = oob_text_surf.get_rect(midtop=[oob_marker_rect.centerx, oob_marker_rect.bottom + 3])

            self.game.screen.blit(oob_marker_surf, oob_marker_rect)
            self.game.screen.blit(oob_text_surf, oob_text_rect)

    def draw_ammo_count(self):
        if self.game.player_sprite.weapon:
            color = ['Black', 'White'][self.color]
            ammo = self.game.player_sprite.weapon.ammo
            if ammo < 10:
                ammo = f' {ammo}'
            else:
                ammo = str(ammo)
            ammo_count_surf = self.game.text_to_surface_mf(ammo, True, color, size=40)
            self.game.screen.blit(ammo_count_surf, (745, 10))
            self.game.screen.blit(self.ammo_icon[self.color], (770, 10))

    def draw_jumps_count(self):
        if self.game.player_sprite.max_jumps < 2:
            return None
        for i in range(self.game.player_sprite.max_jumps):
            if i < self.game.player_sprite.jumps:
                _image = self.jump_on_icon[self.color]
            else:
                _image = self.jump_off_icon[self.color]
            self.game.screen.blit(_image, (20 + i*40, 10))

    def change_color(self, new_color, include_overlay=False):
        if self.color == new_color:
            return

        self.color = new_color
        self.ground_surf.fill(['Black', 'White'][self.color])
        self.sky_surf.fill(['White', 'Black'][self.color])
        self.foreground.fill(['White', 'Black'][self.color])
        if include_overlay:
            self.overlay.fill(['White', 'Black'][self.color])
        self.game.screen.blit(self.ground_surf, (0, 300))

    def change_mask(self, new_mask):
        if self.game.mask_sprite.type_ == new_mask:
            return
        self.game.mask_sprite.kill()
        self.game.mask_sprite = CB_Mask(self.game.player_sprite, new_mask)
        self.game.player_attachments.add(self.game.mask_sprite)
        if self.game.player_sprite.weapon:
            self.game.player_sprite.weapon.kill()
        self.game.player_sprite.weapon = None
        if new_mask in ['rooster', 'bear']:
            self.game.player_sprite.pick_up_weapon(CB_Weapon(self))
        # TODO: add alpha channel restoration
        if new_mask == 'bear':
            self.ability_icon = self.shield_icon[1]
        else:
            self.ability_icon = self.no_surf

    def spawn_new_enemy(self, time_spent=None):
        if not self.game.enemy_spawn and time_spent is None:
            if random.randint(1, 5) <= 2:
                if self.sky_is_over and random.randint(1, 2) == 1:
                    a = CB_Bat(self)
                    a.rect.bottomleft = (
                    random.randint(self.game.enemy_placement_range[0], self.game.enemy_placement_range[1] + 100),
                    150)
                    a.set_speed(v_x=-1 * random.randint(self.game.fly_speed_range[0] - 50, self.game.fly_speed_range[1] - 50))
                    a.set_difficulty((int(self.score) - 99) // 10)
                    self.game.enemy_group.add(a)
                    del a
                else:
                    a = CB_Fly(self)
                    a.rect.bottomleft = (
                    random.randint(self.game.enemy_placement_range[0], self.game.enemy_placement_range[1]),
                    random.randint(self.game.fly_y_range[0], self.game.fly_y_range[1]))
                    a.set_speed(v_x=-1 * random.randint(self.game.fly_speed_range[0], self.game.fly_speed_range[1]))
                    self.game.enemy_group.add(a)
                    del a
            else:
                a = CB_Snail(self)
                a.rect.bottomleft = (
                random.randint(self.game.enemy_placement_range[0], self.game.enemy_placement_range[1]), 300)
                a.set_speed(v_x=-1 * random.randint(self.game.snail_speed_range[0], self.game.snail_speed_range[1]))

                self.game.enemy_group.add(a)
                del a
            pygame.time.set_timer(self.game.enemy_spawn_timer, self.game.enemy_spawn_interval, 1)
            return

        elif not self.game.enemy_spawn:
            return

        next_enemy = self.game.enemy_spawn[0]  # list(type, spawn time, spawn location, args)
        if next_enemy[1] < time_spent:
            a = 0
            match next_enemy[0]:
                case 'fly':
                    a = CB_Fly(self)
                    a.rect.bottomleft = (800, next_enemy[2])
                    a.set_speed(v_x=next_enemy[3], v_y=next_enemy[4])
                    self.game.enemy_group.add(a)
                case 'bat':
                    a = CB_Bat(self)
                    a.rect.bottomleft = (800, next_enemy[2])
                    a.set_speed(v_x=next_enemy[3], v_y=next_enemy[4])
                    self.game.enemy_group.add(a)
                case 'snail':
                    a = CB_Snail(self)
                    a.rect.bottomleft = (800, 300)
                    a.set_speed(v_x=next_enemy[3], v_y=next_enemy[4])
                    self.game.enemy_group.add(a)
                case 'leaf':
                    a = CB_Leaf(self, next_enemy[4], next_enemy[2])
            self.game.enemy_spawn.pop(0)
            if not self.game.enemy_spawn:
                pygame.time.set_timer(self.game.enemy_spawn_timer, self.game.enemy_spawn_interval, 1)
            del a

    def difficulty_scaling(self):
        if int(self.score) != self.last_rescale_score:
            self.game.player_sprite.max_jumps = 1 + int(self.score)//(30 + 5*self.game.mask_sprite.stomps)

            self.game.max_ammo = MAX_AMMO_CAPACITY - int(self.score)//6

            self.game.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 7 * int(self.score)

            self.game.enemy_placement_range = [ENEMY_PLACEMENT_RANGE[0], ENEMY_PLACEMENT_RANGE[1] - int(self.score)]
            self.game.fly_y_range = [FLY_Y_RANGE[0] - int(self.score)//2, FLY_Y_RANGE[1] + int(self.score)]
            self.game.snail_speed_range = [SNAIL_SPEED_RANGE[0] + 50 + int(self.score), SNAIL_SPEED_RANGE[1] + 2*int(self.score)]
            self.game.fly_speed_range = [FLY_SPEED_RANGE[0] + 50 + int(self.score), FLY_SPEED_RANGE[1] + 2*int(self.score)]

            self.last_rescale_score = int(self.score)
