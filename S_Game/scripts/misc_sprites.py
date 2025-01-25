import pygame


class PlayingStalkers(pygame.sprite.Sprite):
    def __init__(self, game, pos=None):
        super().__init__()

        self.game = game

        self.alex_anim_frames = game.alex_anim_frames
        self.bob_anim_frames = game.bob_anim_frames
        self.vasya_anim_frames = game.vasya_anim_frames
        self.anim_index = 0

        self.image = pygame.Surface((200, 4))
        self.image.set_alpha(0)
        self.center = pos or [0.0, 0.0]
        self.rect = self.image.get_rect(center=self.center)
        self.refference_rect = pygame.Rect(0, 0, 200, 100)
        self.refference_rect.center = self.center

        self.alex_sprite = pygame.sprite.Sprite()
        self.alex_sprite.image = game.alex_anim_frames[0]
        self.alex_sprite.rect = self.refference_rect

        self.bob_sprite = pygame.sprite.Sprite()
        self.bob_sprite.image = game.bob_anim_frames[0]
        self.bob_sprite.rect = self.refference_rect

        self.vasya_sprite = pygame.sprite.Sprite()
        self.vasya_sprite.image = game.vasya_anim_frames[0]
        self.vasya_sprite.rect = self.refference_rect

        self.board_sprite = pygame.sprite.Sprite()
        self.board_sprite.image = game.board
        self.board_sprite.rect = self.refference_rect

        self.overlay = pygame.sprite.Group()
        self.underlay = pygame.sprite.Group()

        self.overlay.add([self.alex_sprite, self.bob_sprite, self.vasya_sprite, self.board_sprite])
        self.underlay.add([self.alex_sprite, self.bob_sprite, self.vasya_sprite, self.board_sprite])

    def _animate(self):
        self.anim_index += 4.8 * self.game.delta_time / 1000
        if self.anim_index >= 990:  # common cycle length 9*10*11
            self.anim_index = 0

        self.alex_sprite.image = self.alex_anim_frames[int(self.anim_index) % 9]
        self.bob_sprite.image = self.bob_anim_frames[int(self.anim_index/3) % 10]
        self.vasya_sprite.image = self.vasya_anim_frames[int(self.anim_index/3) % 11]

    def update(self):
        self._animate()
