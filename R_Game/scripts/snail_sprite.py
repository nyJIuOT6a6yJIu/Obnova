import math
import random

import pygame

from R_Game.scripts.player_sprite import Weapon


class Snail(pygame.sprite.Sprite):
    def __init__(self, game, direct_init=True):
        super().__init__()
        self.game = game
        if direct_init:
            self.anim_frames = [game.snail_1, game.snail_2]
            self.anim_index = 0
            self.image = self.anim_frames[self.anim_index]
            self.rect = self.image.get_rect()
            self.center = [0.0, 0.0]
            self.speed = [0, 0]


            if self.game.game_state == self.game.GameState.FIRST_GAME:
                self.mask_bool = False
            else:
                self.mask_bool = True
            self.mask = DogMask(self)
            self.game.enemy_attachments.add(self.mask)

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.rect.centerx = int(self.center[0])
        if self.rect.right < -10:
            self.game.score_add('pass')
            self.mask.kill()
            self.kill()

    def _animate(self):
        self.anim_index += 3.6 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        if self.game.game_state not in [self.game.GameState.NUKE_START, self.game.GameState.NO_KILL_START]:
            self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'snail'

    def kill(self):
        if self.rect.left > 100 and self.rect.right < 700 and len(self.game.pickups) < 3 and random.randint(1, 100) <= self.game.pickup_rate:
            self.game.pickups.add(Weapon(self.game, self.rect.midbottom))
        super().kill()


class DogMask(pygame.sprite.Sprite):
    def __init__(self, _body, direct_init=True):
        super().__init__()
        if direct_init:
            self.image = pygame.transform.scale(_body.game.snail_mask, (35, 45))
            self.rect = self.image.get_rect()
            self.body = _body

    def update(self):
        if self.body.mask_bool:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        self.rect.bottomleft = (self.body.rect.bottomleft[0] - 5, self.body.rect.bottomleft[1])


class Cham(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.anim_frames = [game.cham_1, game.cham_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect()
        self.center = [0.0, 0.0]
        self.speed = [0, 0]
        self._alpha = 140 - min(137, self.game.score)
        self.t = 500

        if self.game.game_state == self.game.GameState.FIRST_GAME:
            self.mask_bool = False
        else:
            self.mask_bool = True

        self.mask = ChamMask(self)
        self.game.enemy_attachments.add(self.mask)

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.rect.centerx = int(self.center[0])
        if self.rect.right < -10:
            self.game.score_add('pass')
            self.mask.kill()
            self.kill()

    def _animate(self):
        self.anim_index += 3.6 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]
        _alpha = self._alpha + 15*math.cos(self.t*math.pi/1000)
        self.image.set_alpha(_alpha)
        self.mask.image.set_alpha(_alpha)
        self.t = (self.t + self.game.delta_time)%2000

    def update(self):
        if self.game.game_state not in [self.game.GameState.NUKE_START, self.game.GameState.NO_KILL_START]:
            self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'snail'

    def kill(self):
        if self.rect.left > 100 and self.rect.right < 700 and len(self.game.pickups) < 3 and random.randint(1, 100) <= self.game.pickup_rate:
            self.game.pickups.add(Weapon(self.game, self.rect.midbottom))
        super().kill()


class ChamMask(pygame.sprite.Sprite):
    def __init__(self, _body):
        super().__init__()

        self.image = pygame.transform.scale(_body.game.cham_mask, (35, 45))
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.rect.bottomleft = (self.body.rect.bottomleft[0] - 5, self.body.rect.bottomleft[1])


class Toad(pygame.sprite.Sprite):
    def __init__(self, game, direct_init=True):
        super().__init__()
        self.game = game
        if direct_init:
            self.anim_frames = [game.snail_1, game.snail_2]
            self.anim_index = 0
            self.image = self.anim_frames[self.anim_index]
            self.rect = self.image.get_rect()
            self.center = [0.0, 0.0]
            self.speed = [0, 0]

            self.jump_point = random.randint(625, 750)
            self.jumped = False

            if self.game.game_state == self.game.GameState.FIRST_GAME:
                self.mask_bool = False
            else:
                self.mask_bool = True
            self.mask = ToadMask(self)
            self.game.enemy_attachments.add(self.mask)

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        gravity_acc = self.game.gravity_acceleration

        if abs(self.rect.centerx - self.center[0]) > 2:
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2:
            self.center[1] = self.rect.centery

        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.center[1] += self.speed[1] * self.game.delta_time / 1000

        self.rect.center = [int(self.center[0]), int(self.center[1])]

        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.speed[1] = 0
        else:
            self.speed[1] += gravity_acc * self.game.delta_time / 2000

        self.rect.centerx = int(self.center[0])
        if self.rect.right < -10:
            self.game.score_add('pass')
            self.mask.kill()
            self.kill()

        if not self.jumped and self.rect.centerx <= self.jump_point:
            if random.randint(1, 5) == 1:
                self.speed = [-750, -650]
                self.game.jump_sound.play()
            self.jumped = True

    def _animate(self):
        if self.rect.bottom == 300:
            self.anim_index += 3.6 * self.game.delta_time / 1000
            if self.anim_index >= 2:
                self.anim_index = 0
            self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        if self.game.game_state not in [self.game.GameState.NUKE_START, self.game.GameState.NO_KILL_START]:
            self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'toad'


class ToadMask(pygame.sprite.Sprite):
    def __init__(self, _body):
        super().__init__()
        image = pygame.transform.scale(_body.game.frog_mask, (51, 45))
        image = pygame.transform.flip(surface=image, flip_x=True, flip_y=False)
        self.image = image
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        self.rect.bottomleft = (self.body.rect.bottomleft[0] - 13, self.body.rect.bottomleft[1])

class Stomped_Snail(pygame.sprite.Sprite):
    def __init__(self, game, pos):
        super().__init__()
        self.game = game
        self.pos = pos
        self.time = 4000
        self.ref_image = self.game.stomped_enemy
        self.image = pygame.transform.rotate(self.ref_image, 0.0)
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.image.set_alpha(int(pygame.math.clamp(self.time//10, 0, 255)))
        self.time -= self.game.delta_time
        if self.time < 0:
            self.kill()
