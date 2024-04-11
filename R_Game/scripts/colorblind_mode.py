import math
import random

import pygame

from R_Game.scripts.snail_sprite import Snail, DogMask
from R_Game.scripts.fly_sprite import Fly, OwlMask, Bat, BatMask

from R_Game.scripts.player_sprite import Player, Weapon, Stomp, Mask

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
        self.mask = CB_BatMask(self)
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
        self.angle += 2
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

        self.punch_group = pygame.sprite.GroupSingle()
        self.punch_sprite = CB_Punch(self)
        self.punch_group.add(self.punch_sprite)

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

    def update(self):
        super().update()
        self.punch_group.update()
        self.punch_group.draw(self.game.screen)

    def final_update(self, time_pass):
        gravity_acc = self.game.gravity_acceleration

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        self.speed[1] += gravity_acc * self.game.delta_time / 2000
        self.center[1] += self.speed[1] * self.game.delta_time / 1000

        self.rect.center = [int(self.center[0]), int(self.center[1])]

        if not self.is_airborne():
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        if time_pass > 216800:
            d_t = time_pass - 216800
            scale = (int(68 + 5*d_t), int(84 + 5*d_t))
            self.image = pygame.transform.scale(self.source.player_stand[self.source.color], scale)
            self.rect = self.image.get_rect(center=self.center)





class CB_Mask(Mask):
    def __init__(self, _player, _type):
        super().__init__(_player, _type, False)

        self.stomp_sprite = None
        self.stomps = 0

        self.bear_banner = pygame.Surface((800, 300))
        self.bear_banner.fill('White')

        self.punch_status = None
        self.punch_used = None

        if _type == 'rooster':
            self.images = _player.source.rooster_mask
            self.image = self.images[_player.source.color]
        elif _type == 'bear':
            _player.source.deflects += 1
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

    def dash_cd(self):
        return 1300 + self.dash_used - pygame.time.get_ticks() - 700 * bool(self.culmination)

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


class CB_Punch(pygame.sprite.Sprite):
    def __init__(self, body):
        super().__init__()

        self.default_image = pygame.surface.Surface((74, 84))
        self.default_image.set_alpha(0)
        self.image = self.default_image
        self.rect = self.image.get_rect()
        self.body = body

    def punch_process(self):
        if self.body.mask.type_ != 'tiger' or self.body.mask.punch_used is None:
            self.image = self.default_image
            return

        _now = pygame.time.get_ticks()
        _time_spent = _now - self.body.mask.punch_used
        _final = 160 + int(2.5 * self.body.source.score)
        _time_by_punch = _time_spent % 160

        if self.body.mask.punch_status != 'cooldown' and _time_by_punch < 40:
            self.image = self.body.source.punch_1[self.body.source.color]
        elif self.body.mask.punch_status != 'cooldown' and _time_by_punch < 60:
            self.image = self.body.source.punch_2[self.body.source.color]
        elif self.body.mask.punch_status != 'cooldown' and _time_by_punch < 100:
            self.image = self.body.source.punch_3[self.body.source.color]
        elif self.body.mask.punch_status != 'cooldown' and _time_by_punch < 120:
            self.image = self.body.source.punch_4[self.body.source.color]
        elif self.body.mask.punch_status != 'cooldown' and _time_by_punch < 160:
            self.image = self.body.source.punch_5[self.body.source.color]
        if _time_spent > _final:
            self.body.mask.punch_status = 'cooldown'
            self.image = self.default_image
        if self.body.mask.punch_cd() <= 0:
            self.body.mask.punch_status = 'ready'
            self.body.mask.punch_used = None

    def update(self):
        self.punch_process()
        self.rect.midleft = self.body.rect.midright


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


class CB_SpinGirl(pygame.sprite.Sprite):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.image = pygame.surface.Surface((30, 300))
        self.rect = self.image.get_rect()
        self.girl_frame = source.girl[0]
        self.rect.center = (-100, 150)
        self.x = -100

    def update(self):
        self.x += 430 * self.source.game.delta_time / 1000
        self.rect.centerx = int(self.x)
        girl_index = min(max(self.rect.centerx // 27, 0), 29)
        girl_frame = self.source.girl[girl_index]
        girl_pos = (self.x - 120, 0)
        self.source.game.screen.blit(girl_frame, girl_pos)


class Touhou:
    def __init__(self, game):
        self.game = game
        self.load_images()
        self.music = ['R_Game/audio/misc music/color_blind.mp3', 1.0]
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

        self.shield_icon = [pygame.transform.scale(pygame.image.load(path + 'fumo_shield_black.png').convert_alpha(), (50, 50)),
                          pygame.transform.scale(pygame.image.load(path + 'fumo_shield_white.png').convert_alpha(), (50, 50))]

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

        self.ethe = pygame.image.load(f"{path}ethe.png").convert_alpha()

    def set_up_run(self):
        self.subtitles = list(i for i in SUBTITLES)
        self.sub_drawn = False

        self.sky_surf.fill('Black')
        self.ground_surf.fill('White')
        self.foreground.fill('Black')

        self.snow_list = []
        self.sun_flake = [[253, 300], 4]

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
        self.girl_sprite = None

        self.color = 1  # 0 - black character, 1 - white character

        self.foreground.set_alpha(45)

        self.score = 0
        self.last_rescale_score = None

        self.player_mask = None

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

        cb_deaths = self.game.progress.get('touhou deaths', 0)
        self.deflects = min(2, cb_deaths//4)

        self.game.screen.blit(self.ground_surf, (0, 300))

        self.game.music_handler.music_play(self.music)

        self.start = pygame.time.get_ticks()


    def runtime_frame(self):
        now = pygame.time.get_ticks()

        time_pass = now - self.start

        if time_pass < 4000:
            y = (time_pass)//10
            self.game.screen.blit(self.sky_surf, (0, y-400))
        else:
            if not self.sky_is_over and self.game.mask_sprite.dash_status != 'active':
                self.game.screen.blit(self.sky_surf, (0, 0))

        if 14990 <= time_pass < 20000:
            self.change_color(0)
            self.change_mask('rooster')
            self.maskless_enemies = False
            self.score = 29

        elif 42990 <= time_pass < 45000:
            self.change_color(1)
            self.change_mask('bear')
            self.score = 69  # nice

        elif 69990 <= time_pass < 73000:
            self.change_mask('tiger')
            self.score = 89

        elif 84990 <= time_pass < 88000:
            self.change_color(0, True)
            self.change_mask('zebra')

        elif 109690 <= time_pass < 111000:
            if not self.game.enemy_spawn:
                self.game.mask_sprite.culmination = True
                # list(type, spawn time, spawn location, spawn speed, args)
                speed = -700
                self.game.enemy_spawn = [['fly', 111900, 140, -750, 0],     ['fly', 112300, 140, -720, 0],
                                         ['snail', 112800, 300, speed, 0],  ['bat', 113300, 130, speed, 20],
                                         ['snail', 113650, 300, speed, 0],  ['bat', 114150, 130, speed, 20],
                                         ['snail', 114500, 300, speed, 0],  ['bat', 115000, 130, speed, 20],
                                         ['snail', 115350, 300, speed, 0],  ['snail', 115800, 300, speed, 0],
                                         ['snail', 116250, 300, speed, 20], ['bat', 116750, 130, speed, 20],
                                         ['snail', 117100, 150, speed, 20], ['bat', 117600, 130, speed, 20],
                                         ['snail', 117950, 150, speed, 20], ['bat', 118450, 130, speed, 20],
                                         ['snail', 118800, 150, speed, 20], ['snail', 119250, 300, speed, 0],
                                         ['snail', 119700, 300, speed, 20], ['bat', 120200, 130, speed, 20],

                                         ['snail', 120650, 300, speed, 0],  ['bat', 121150, 130, speed, 20],
                                         ['snail', 121500, 300, speed, 0],  ['bat', 122000, 130, speed, 20],
                                         ['snail', 122350, 300, speed, 0],  ['snail', 122800, 300, speed, 0],
                                         ['snail', 123250, 300, speed, 20], ['bat', 123750, 130, speed, 20],
                                         ['snail', 124100, 150, speed, 20], ['bat', 124600, 130, speed, 20],
                                         ['snail', 124950, 150, speed, 20],

                                         ['fly', 125600, 100, -760, 0],  ['fly', 125700, 140, -755, 0],
                                         ['fly', 125800, 70, -750, 0],   ['fly', 125900, 120, -745, 0],
                                         ['fly', 126000, 80, -740, 0],   ['fly', 126050, 60, -735, 0],

                                         ['leaf', 126250, 670, 0, 7], ['leaf', 126550, 270, 0, 5],
                                         ['leaf', 126750, 134, 0, 0], ['leaf', 127450, 534, 0, 1],
                                         ['leaf', 128150, 400, 0, 2], ['leaf', 128850, 290, 0, 3],
                                         ['leaf', 129550, 730, 0, 4], ['leaf', 129900, 470, 0, 6],
                                         ]

        elif 110990 <= time_pass < 111390:
            self.change_color(1)
            self.sky_is_over = True
            self.score = 110

        elif 125990 <= time_pass < 129000:
            self.change_color(0)
            self.score = 115

        elif 166900 <= time_pass < 170000:
            self.change_color(1, True)
            self.change_mask('bear')
            self.score = 137

        elif 180500 <= time_pass < 194990:
            self.change_color(0, True)
            self.sky_is_over = False
            self.change_mask('rooster')
            self.score = 90
            self.draw_snow(time_pass)

        elif 194990 <= time_pass < 209990:
            self.change_color(1)
            self.score = 95
            self.draw_snow(time_pass, False)

        elif 209990 <= time_pass < 212000:
            self.change_color(0)
            self.sky_is_over = True

            self.change_mask('None')
            self.maskless_enemies = True
            self.score = min(int(137 + 62 * (time_pass - 209990) / 2110), 199)

        elif time_pass >= 217700:
            self.game.game_state = self.game.GameState.DEFAULT_MENU
            self.game.progress['sralker_unlocked'] = True
            self.game.music_handler.music_stop()

        if self.sky_is_over or self.game.mask_sprite.dash_status == 'active':
            self.game.screen.blit(self.foreground, (0, 0))

        self.draw_sun(time_pass)

        if time_pass > 14890 or time_pass < 14490:
            if time_pass < 216000:
                self.game.player.update()
                self.game.player_attachments.update()
            else:
                self.game.player_sprite.final_update(time_pass)
            self.game.enemy_group.update()
            self.game.enemy_attachments.update()

            self.game.pickups.update()

        self.girl_handler(time_pass)

        self.game.player.draw(self.game.screen)
        self.game.player_attachments.draw(self.game.screen)

        self.game.enemy_group.draw(self.game.screen)
        self.game.enemy_attachments.draw(self.game.screen)

        self.leaves_sprites.update()
        self.leaves_sprites.draw(self.game.screen)

        self.game.pickups.draw(self.game.screen)

        self.draw_overlay(time_pass=time_pass, transition_time=110990, half_duration=700)
        self.draw_overlay(time_pass=time_pass, transition_time=180500, half_duration=500)
        self.draw_overlay(time_pass=time_pass, transition_time=194990, half_duration=500)

        self.draw_subtitles(time_pass)

        self.weapon_collision()

        self.spawn_new_enemy(time_pass)

        self.difficulty_scaling()

        self.draw_shot_after_image()

        if time_pass < 209000:
            self.draw_spec_abilities()
        self.draw_out_of_bounds_marker()
        self.draw_ammo_count()
        self.draw_jumps_count()

        if not ((84990 < time_pass < 86490)  or  # first from-tiger transition
               (167000 < time_pass < 168500) or  # second from-tiger transition
                         time_pass >= 209000):   # end sequence
            if self.game.mask_sprite.dash_status != 'active' \
                    and not (self.game.mask_sprite.dash_status == 'cooldown' and self.game.player_sprite.is_airborne()) \
                    and self.game.enemy_collision():
                if self.deflects:
                    self.deflects -= 1
                    self.game.mask_sprite.deflect_ability()
                else:
                    self.game.game_state = self.game.GameState.DEFAULT_MENU
                    self.game.enemy_spawn = list()
                    cb_deaths = self.game.progress.get('touhou deaths', 0)
                    cb_deaths += 1
                    self.game.progress['touhou deaths'] = cb_deaths
                    pygame.mixer_music.stop()

        if time_pass <= 217500:
            self.game.game_over()

    def girl_handler(self, time_pass):  # what a name lmao
        if self.girl_sprite is None and time_pass >= 131200:
            self.girl_sprite = CB_SpinGirl(self)
        elif self.girl_sprite is None or self.girl_sprite == 4:
            return
        else:
            self.girl_sprite.update()
            enemy_colision = pygame.sprite.spritecollide(self.girl_sprite, self.game.enemy_group, False)
            for i in enemy_colision:
                i.mask.kill()
                i.kill()
            pygame.sprite.spritecollide(self.girl_sprite, self.leaves_sprites, True)
            player_collision = pygame.sprite.spritecollide(self.girl_sprite, self.game.player, False)
            if self.game.mask_sprite.type_ != 'tiger' and player_collision:
                self.change_mask('tiger')

            if self.girl_sprite.rect.x > 1100:
                self.girl_sprite.kill()
                self.girl_sprite = 4  # because why not lmao

    def draw_spec_abilities(self):
        if self.game.mask_sprite.bear_activation_time is not None:
            _alpha = int(255 * math.sin(1 + (600 - self.game.mask_sprite.bear_activation_time)/300))
            self.game.mask_sprite.bear_banner.set_alpha(_alpha)
            self.game.mask_sprite.bear_activation_time -= self.game.delta_time
            self.game.screen.blit(self.game.mask_sprite.bear_banner, (0, 0))
            if self.game.mask_sprite.bear_activation_time < 0:
                self.game.mask_sprite.bear_activation_time = None
        else:
            self.game.mask_sprite.bear_activation_time = None

        for i in range(self.deflects):
            self.game.screen.blit(self.shield_icon[self.color], (490 + 56*i, 10))

        if self.deflects == 2:
            draw_top_right = bool(self.color == 0)
            draw_top_left = bool(self.color == 0)
            draw_bottom_left = bool(self.color == 1)
            draw_bottom_right = bool(self.color == 1)
            _color = ['Black', 'White'][self.color]
            pygame.draw.circle(self.game.screen, color=_color, center=(544, 70), radius=8.0, width=2,
                               draw_top_right=draw_top_right, draw_top_left=draw_top_left,
                               draw_bottom_left=draw_bottom_left, draw_bottom_right=draw_bottom_right)

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

    def draw_overlay(self, time_pass=None, transition_time=None, half_duration=700):
        if time_pass > transition_time - half_duration and time_pass < transition_time + half_duration:
            _alpha = int(pygame.math.clamp((255 - (255/half_duration)*abs(transition_time - time_pass)), 0, 255))
            self.overlay.set_alpha(_alpha)
            if _alpha:
                self.game.screen.blit(self.overlay, (0, 0))



    def draw_subtitles(self, time_pass):
        if self.subtitles is None or self.subtitles == []:
            return

        current_subtitle = self.subtitles[0]
        if time_pass > current_subtitle[0] and not self.sub_drawn:  # pora
            self.sub_drawn = True
            jap_text_surf = self.game.text_to_surface_jf(current_subtitle[2], True, ['White', 'Black'][self.color], size=26)
            eng_text_surf = self.game.text_to_surface_mf(current_subtitle[3], True, ['White', 'Black'][self.color], size=36)
            _alpha = 255

            if current_subtitle[1] == 129990 and time_pass - current_subtitle[0] < 800:
                _alpha = pygame.math.clamp((time_pass - current_subtitle[0]) * 255 // 800, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
                self.sub_drawn = False
            if current_subtitle[1] in [110990, 209000] and current_subtitle[1] - time_pass < 1200:
                _alpha = pygame.math.clamp((current_subtitle[1] - time_pass) * 255 // 1200, 0, 255)
                jap_text_surf.set_alpha(_alpha)
                eng_text_surf.set_alpha(_alpha)
                self.sub_drawn = False
            jap_text_rect = jap_text_surf.get_rect(center=(400, 330))
            eng_text_rect = eng_text_surf.get_rect(center=(400, 370))
            self.game.screen.blit(self.ground_surf, (0, 300))
            self.game.screen.blit(jap_text_surf, jap_text_rect)
            self.game.screen.blit(eng_text_surf, eng_text_rect)
        if time_pass > current_subtitle[1]:
            self.subtitles.pop(0)
            self.sub_drawn = False
            self.game.screen.blit(self.ground_surf, (0, 300))

    def draw_shot_after_image(self):
        for index, i in enumerate(self.game.gunshot_afterimage):
            if self.game.player_sprite.weapon and i[1] > 0.0:
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

    def draw_snow(self, time_pass, reverse=True):
        if len(self.snow_list) < min(80, (time_pass - 181000) // 250) and time_pass < 210000:
            self.snow_list.append([random.randint(30, 740), 300*bool(reverse)])  # init x, current y
        delete_snow = []
        for snow_flake in self.snow_list:
            if reverse:
                snow_flake[1] -= self.game.delta_time * 80 / 1000
            else:
                snow_flake[1] += self.game.delta_time * 80 / 1000
            y = int(snow_flake[1])

            if y <= -10 or y >= 310:
                delete_snow.append(snow_flake)
                continue

            x = int(snow_flake[0] + snow_flake[0] * 120 / (441 - y))

            if (y >= 300 and not reverse) or (y <= -10 and reverse):
                delete_snow.append(snow_flake)
                continue

            pygame.draw.circle(self.game.screen, ['Black', 'White'][self.color], (x, y), 4)

        for i in delete_snow:
            self.snow_list.remove(i)

    def draw_sun(self, time_pass):
        if time_pass < 192100:
            return
        x = 365
        if time_pass < 193400:
            self.sun_flake[0][1] = int(300 - (time_pass - 192100) / 10)
            self.sun_flake[0][0] = int(253 + 253 * 120 / (441 - self.sun_flake[0][1]))

        elif time_pass < 209990:
            self.sun_flake[1] = 4 + 9 * (time_pass - 193400) / 1000

        else:
            self.sun_flake[1] = 40 + 4 * (time_pass - 209990) / 1000

        if time_pass >= 209990:
            x = int(self.sun_flake[0][0])
            self.sun_flake[0][0] = self.sun_flake[0][0] + 1.3 * math.sin((time_pass - 209990) / 30)

        if not 194990 <= time_pass < 209990:
            pygame.draw.circle(self.game.screen, 'Black', (int(self.sun_flake[0][0]), int(self.sun_flake[0][1])) , int(self.sun_flake[1]))

            _value = (1 + math.sin(- math.pi / 2 + math.pi*(time_pass - 209990)/7710))
            _alpha = int(125 * _value)
            _angle = -500 * _value**2
            _image = pygame.transform.rotate(self.ethe, _angle)
            _image.set_alpha(_alpha)
            _rect = _image.get_rect(center=(x, 170))
            self.game.screen.blit(_image, _rect)


    def draw_jumps_count(self):
            if self.game.player_sprite.max_jumps < 2:
                return None
            for i in range(self.game.player_sprite.max_jumps):
                if i < self.game.player_sprite.jumps:
                    _image = self.jump_on_icon[self.color]
                else:
                    _image = self.jump_off_icon[self.color]
                self.game.screen.blit(_image, (20 + i*40, 10))

    def change_color(self, new_color, include_overlay=False, time_pass=None):
        if self.color == new_color:
            return

        self.color = new_color
        self.ground_surf.fill(['Black', 'White'][self.color])
        self.sky_surf.fill(['White', 'Black'][self.color])
        self.foreground.fill(['White', 'Black'][self.color])
        self.game.mask_sprite.bear_banner.fill(['White', 'Black'][self.color])
        if include_overlay:
            self.overlay.fill(['White', 'Black'][self.color])
        self.game.screen.blit(self.ground_surf, (0, 300))

        if time_pass is not None:
            self.sub_drawn = False
            self.draw_subtitles(time_pass)

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

    def weapon_collision(self):
        if self.game.mask_sprite.type_ == 'tiger' and self.game.mask_sprite.punch_status == 'active':
            collisions = pygame.sprite.spritecollide(self.game.player_sprite.punch_sprite, self.game.enemy_group, False)
            for i in collisions:
                i.mask.kill()
                i.kill()

        for weapon in self.game.player_attachments:

            if isinstance(weapon, CB_Stomp) and self.game.mask_sprite.type_ == 'tiger' and self.game.player_sprite.speed[1] > STOMP_SPEED:
                collisions = pygame.sprite.spritecollide(weapon, self.game.enemy_group, False)
                for i in collisions:
                    self.game.mask_sprite.punch_status = 'cooldown'
                    self.game.mask_sprite.punch_used = pygame.time.get_ticks() - 165 - int(2.5 * self.score)
                    i.mask.kill()
                    i.kill()

                    self.game.mask_sprite.stomps += 1

            if not isinstance(weapon, CB_Weapon):
                continue
            if weapon.speed == [0, 0]:
                continue
            collisions = pygame.sprite.spritecollide(weapon, self.game.enemy_group, False)
            for i in collisions:
                i.mask.kill()
                i.kill()

            if collisions:
                weapon.kill()


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
                    a.set_difficulty(2)
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
            if self.score > 138:
                self.game.player_sprite.max_jumps = 0
            else:
                self.game.player_sprite.max_jumps = 1 + int(self.score)//(30 + 5*self.game.mask_sprite.stomps)

            self.game.max_ammo = MAX_AMMO_CAPACITY - int(self.score)//6

            self.game.enemy_spawn_interval = ENEMY_SPAWN_INTERVAL_MS - 7 * int(self.score)

            self.game.enemy_placement_range = [ENEMY_PLACEMENT_RANGE[0], ENEMY_PLACEMENT_RANGE[1] - int(self.score)]
            self.game.fly_y_range = [FLY_Y_RANGE[0] - int(self.score)//2, FLY_Y_RANGE[1] + int(self.score)]
            self.game.snail_speed_range = [SNAIL_SPEED_RANGE[0] + 50 + int(self.score), SNAIL_SPEED_RANGE[1] + 2*int(self.score)]
            self.game.fly_speed_range = [FLY_SPEED_RANGE[0] + 50 + int(self.score), FLY_SPEED_RANGE[1] + 2*int(self.score)]

            self.last_rescale_score = int(self.score)
