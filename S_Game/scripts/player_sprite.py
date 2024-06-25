import math
import random
from operator import add

import pygame

from R_Game.config.config import STOMP_SPEED


class Player(pygame.sprite.Sprite):
    def __init__(self, game, pos=None):
        super().__init__()

        self.game = game

        self.speed = pygame.math.Vector2(0, 0)
        # self.speed_change = [0, 0]

        self.w_pressed = False
        self.a_pressed = False
        self.s_pressed = False
        self.d_pressed = False  # Ну я ))))))

        self.anim_frames = [self.game.player_walk_1,
                            self.game.player_walk_2,
                            self.game.player_stand]
        self.anim_index = 2
        self.mirrored = False

        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))
        self.center = pos or [0.0, 0.0]

        self.mask = None
        self.weapon = None

    def player_input(self, key_pressed, released=False, event_pos=None):
        if (key_pressed == pygame.K_w or key_pressed == pygame.K_UP) and not released:
            self.w_pressed = True
        if (key_pressed == pygame.K_a or key_pressed == pygame.K_LEFT) and not released:
            self.a_pressed = True
        if (key_pressed == pygame.K_s or key_pressed == pygame.K_DOWN) and not released:
            self.s_pressed = True
        if (key_pressed == pygame.K_d or key_pressed == pygame.K_RIGHT) and not released:
            self.d_pressed = True
        if (key_pressed == pygame.K_w or key_pressed == pygame.K_UP) and released:
            self.w_pressed = False
        if (key_pressed == pygame.K_a or key_pressed == pygame.K_LEFT) and released:
            self.a_pressed = False
        if (key_pressed == pygame.K_s or key_pressed == pygame.K_DOWN) and released:
            self.s_pressed = False
        if (key_pressed == pygame.K_d or key_pressed == pygame.K_RIGHT) and released:
            self.d_pressed = False

        # if key_pressed == 1:  # LMB
        #     if self.weapon:
        #         shot = self.game.shoot_at_enemy(event_pos)
        #         self.weapon.shoot_at(shot)
        #     else:
        #         if self.mask.punch_status == 'ready':
        #             self.mask.punch_status = 'active'
        #             self.mask.punch_used = pygame.time.get_ticks()
        #             self.game.swing_sound.play()

        # elif key_pressed == 3:  # RMB
        #     pickups = pygame.sprite.spritecollide(self, self.game.pickups, dokill=False)
        #     if pickups:
        #         self.pick_up_weapon(pickups[0], event_pos)
        #     else:
        #         self.drop_weapon(event_pos)

    def is_out_of_bounds(self):
        return_value = [False, False, False, False]  # L R U D
        if self.rect.left < 0:
            # self.rect.left = 0
            return_value[0] = True
        if self.rect.right > 800:
            # self.rect.right = 800
            return_value[1] = True
        if self.rect.top < 0:
            # self.rect.top = 0
            return_value[2] = True
        if self.rect.bottom > 600:
            # self.rect.bottom = 600
            return_value[3] = True
        return return_value

    # @staticmethod
    # def collision_direction(sprite_1, sprite_2):
    #     rect_1 = [sprite_1.rect.left, sprite_1.rect.left+sprite_1.rect.width,
    #               sprite_1.rect.top, sprite_1.rect.top + sprite_1.rect.height]
    #     rect_2 = [sprite_2.rect.left, sprite_2.rect.left+sprite_2.rect.width,
    #               sprite_2.rect.top, sprite_2.rect.top + sprite_2.rect.height]
    #     return_value = [False, False, False, False]
    #     # TODO: collision
    #
    # def obstacle_collision(self):
    #     return_value = [False, False, False, False]
    #     # for obs in pygame.sprite.spritecollide(self, self.game.obstacles, False):
    #
    #     return return_value

    def _movement(self):

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        old_center = [i for i in self.center]
        self.center[0] += self.speed.x * self.game.delta_time / 1000
        self.rect.center = [int(self.center[0]), int(self.center[1])]

        oob = self.is_out_of_bounds()

        if True in oob or pygame.sprite.spritecollide(self, self.game.obstacles, False):
            self.center = old_center
            self.rect.center = [int(i) for i in self.center]

        old_center = [i for i in self.center]
        self.center[1] += self.speed.y * self.game.delta_time / 1000
        self.rect.center = [int(self.center[0]), int(self.center[1])]

        oob = self.is_out_of_bounds()

        if True in oob or pygame.sprite.spritecollide(self, self.game.obstacles, False):
            self.center = old_center
            self.rect.center = [int(i) for i in self.center]

        self.speed.x = -375*bool(self.a_pressed) + 375*bool(self.d_pressed)
        self.speed.y = -375*bool(self.w_pressed) + 375*bool(self.s_pressed)

        if self.speed.x < 0:
            self.mirrored = True
        elif self.speed.x > 0:
            self.mirrored = False

        # now = pygame.time.get_ticks()

    # def pick_up_weapon(self, weapon, event_pos=None):
    #     if event_pos is not None and self.weapon:
    #         self.drop_weapon(event_pos)
    #     self.weapon = weapon
    #     self.game.pickups.remove(weapon)
    #     self.game.player_attachments.add(weapon)
    #     weapon.set_body(self)
    #     self.game.gun_pickup_sound.play()

    # def drop_weapon(self, event_pos):
    #     if self.weapon:
    #         self.weapon.body = None
    #         speed_x = event_pos[0] - self.rect.centerx
    #         speed_y = event_pos[1] - self.rect.centery
    #         speed = pygame.math.Vector2((speed_x, speed_y))
    #         speed = speed.normalize()
    #         speed_x = speed.x * 30
    #         speed_y = speed.y * 30
    #         self.weapon.speed = [speed_x, speed_y]
    #         self.weapon = None
    #         self.game.throw_sound.play()

    def _animate(self):
        prev_index = self.anim_index
        if self.speed.magnitude() >= 50:
            self.anim_index += 9 * self.game.delta_time / 1000
            if self.anim_index >= 2:
                self.anim_index = 0
        else:
            self.anim_index = 2
        if self.mirrored and self.anim_index != 2:
            self.image = pygame.transform.flip(self.anim_frames[int(self.anim_index)], flip_x=True, flip_y=False)
        else:
            self.image = self.anim_frames[int(self.anim_index)]
        if int(self.anim_index != prev_index):
            self.rect = self.image.get_rect(center=self.center)

    def update(self):
        self._movement()
        self._animate()


class Mask(pygame.sprite.Sprite):
    def __init__(self, _player):
        super().__init__()

        self.image = pygame.transform.scale(_player.game.gas_mask, (90, 95))

        self.rect = self.image.get_rect()
        self.body = _player
        _player.mask = self

    def update(self):
        # TODO: flip condition, body.mirrored attribute
        self.rect.center = (self.body.rect.midtop[0] + 7, self.body.rect.midtop[1] + 23)


class Weapon(pygame.sprite.Sprite):
    def __init__(self, game, body=None):
        super().__init__()
        self.game = game

        self.og_image = pygame.transform.scale(game.weapon_ak, (120, 60))
        self.image = self.og_image
        self.rect = self.image.get_rect()

        self.set_body(body)

    def set_body(self, _body):
        _body.weapon = self
        self.body = _body

    def update(self):  # TODO: holster weapon
        self.rect.center = (self.body.rect.centerx + 30, self.body.rect.centery + 15)
