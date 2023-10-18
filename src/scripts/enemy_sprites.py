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
        if self.rect.right < 0:
            self.kill()

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'fly'


class Snail(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.anim_frames = [game.snail_1, game.snail_2]
        self.anim_index = 0
        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect()
        self.center = [0.0, 0.0]
        self.speed = [0, 0]

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        if abs(self.rect.centerx - self.center[0]) > 2:  # ???
            self.center[0] = self.rect.centerx
        self.center[0] += self.speed[0] * self.game.delta_time / 1000
        self.rect.centerx = int(self.center[0])
        if self.rect.right < 0:
            self.kill()

    def _animate(self):
        self.anim_index += 3.6 * self.game.delta_time / 1000
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'snail'
