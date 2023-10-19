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

        self.mask_bool = True
        self.mask = FlyMask(self)
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
            self.game.score += 1
            self.mask.kill()
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

        self.mask_bool = True
        self.mask = SnailMask(self)
        self.game.enemy_attachments.add(self.mask)

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
        if self.rect.right < -10:
            self.game.score += 1
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


class FlyMask(pygame.sprite.Sprite):
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


class SnailMask(pygame.sprite.Sprite):
    def __init__(self, _body):
        super().__init__()

        self.image = pygame.transform.scale(_body.game.snail_mask, (35, 45))
        self.rect = self.image.get_rect()
        self.body = _body

    def update(self):
        if self.body.mask_bool:
            self.image.set_alpha(255)
        else:
            self.image.set_alpha(0)
        self.rect.bottomleft = (self.body.rect.bottomleft[0] - 5, self.body.rect.bottomleft[1])