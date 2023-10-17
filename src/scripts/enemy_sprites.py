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
        self.speed = [0, 0]

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        self.rect.centerx += self.speed[0]
        self.rect.centery += self.speed[1]
        if self.rect.right < 0:
            self.kill()

    def _animate(self):
        self.anim_index += 0.08
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
        self.speed = [0, 0]

    def set_speed(self, v_x=None, v_y=None):
        if v_x:
            self.speed[0] = v_x
        if v_y:
            self.speed[1] = v_y

    def _movement(self):
        self.rect.centerx += self.speed[0]
        self.rect.centery += self.speed[1]
        if self.rect.right < 0:
            self.kill()

    def _animate(self):
        self.anim_index += 0.06
        if self.anim_index >= 2:
            self.anim_index = 0
        self.image = self.anim_frames[int(self.anim_index)]

    def update(self):
        self._movement()
        self._animate()

    @staticmethod
    def get_type():
        return 'snail'
