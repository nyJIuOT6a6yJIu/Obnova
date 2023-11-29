import random

import math

import pygame


class Fly(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.anim_frames = [game.fly_1,
                            game.fly_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect()
        self.center = [0.0, 0.0]
        self.speed = [0, 0]

        if self.game.game_state == self.game.GameState.FIRST_GAME:
            self.mask_bool = False
        else:
            self.mask_bool = True
        self.mask = OwlMask(self)
        self.game.enemy_attachments.add(self.mask)

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        if abs(self.rect.centerx - self.center[0]) > 2: # ???
            self.center[0] = self.rect.centerx
        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.rect.centerx = int(self.center[0])
        if self.rect.right < -10:
            self.game.score_add('pass')
            self.mask.kill()
            self.kill()

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        if self.game.game_state not in [self.game.GameState.NUKE_START, self.game.GameState.NO_KILL_START]:
            self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'fly'


class Bat(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.anim_frames = [game.fly_1,
                            game.fly_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect()
        self.center = [0.0, 0.0]
        self.speed = [0, 0]
        self.t = random.randint(1, 500)
        self.difficulty = 3
        self.phase_1 = random.randint(1, 250)
        self.phase_2 = random.randint(1, 125)

        if self.game.game_state == self.game.GameState.FIRST_GAME:
            self.mask_bool = False
        else:
            self.mask_bool = True

        self.mask = BatMask(self)
        self.game.enemy_attachments.add(self.mask)

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def set_difficulty(self, arg):
        self.difficulty = arg

    def _movement(self):
        if abs(self.rect.centerx - self.center[0]) > 2: # ???
            self.center[0] = self.rect.centerx
        if abs(self.rect.centery - self.center[1]) > 2: # ???
            self.center[1] = self.rect.centery
        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.rect.centerx = int(self.center[0])

        self.rect.bottom = 125 + 35 * math.cos(self.t * math.pi / 500) \
                               + bool(self.difficulty > 1) * 25 * math.cos((self.phase_1+self.t) * math.pi / 250) \
                               + bool(self.difficulty > 2) * 10 * math.cos((self.phase_2+self.t) * math.pi / 125)
        self.t = (self.t + self.game.delta_time) % 1000


        if self.rect.right < -10:
            self.game.score_add('pass')
            self.mask.kill()
            self.kill()

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        if self.game.game_state not in [self.game.GameState.NUKE_START, self.game.GameState.NO_KILL_START]:
            self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'fly'


class OwlMask(pygame.sprite.Sprite):
    def __init__(self, _body):
        super().__init__()

        self.image = pygame.transform.scale(_body.game.fly_mask, (35, 45))
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        if self.body.mask_bool:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        self.rect.center = (self.body.rect.center[0] - 5, self.body.rect.center[1])

class BatMask(pygame.sprite.Sprite):
    def __init__(self, _body):
        super().__init__()

        self.image = pygame.transform.scale(_body.game.bat_mask, (55, 55))
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        if self.body.mask_bool:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        self.rect.center = (self.body.rect.center[0] - 5, self.body.rect.center[1])

