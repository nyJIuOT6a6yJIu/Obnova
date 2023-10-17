import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.jumps = 1
        self.max_jumps = 1
        self.speed = [0, 0]
        self.a_pressed = False
        self.d_pressed = False  # Ну я ))))))

        self.anim_frames = [self.game.player_walk_1,
                            self.game.player_walk_2,
                            self.game.player_jump]
        self.anim_index = 0

        self.image = self.anim_frames[self.anim_index]
        self.rect = self.image.get_rect(midbottom=(80, 300))

        self.set_attachments()

    def player_input(self, key_pressed, released=False):
        if self.jumps and (key_pressed == pygame.K_SPACE or key_pressed == pygame.K_w) and not released:
            self.speed[1] = -20
            self.jumps -= 1
        if key_pressed == pygame.K_a and not released:
            self.a_pressed = True
        elif key_pressed == pygame.K_a and released:
            self.a_pressed = False
        if key_pressed == pygame.K_d and not released:
            self.d_pressed = True
        if key_pressed == pygame.K_d and released:
            self.d_pressed = False
        if self.a_pressed or self.d_pressed:
            self.speed[0] = 5*bool(self.d_pressed) - 5*bool(self.a_pressed)

    def _movement(self):
        gravity_acc = 1
        stiffness = 1

        self.rect.centerx += self.speed[0]
        self.rect.bottom += self.speed[1]
        self.speed[1] += gravity_acc

        if self.rect.bottom > 300:
            self.rect.bottom = 300
            self.speed[1] = 0
            self.jumps = self.max_jumps
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > 780:
            self.rect.right = 780
        if self.speed[0]:
            if not (self.a_pressed or self.d_pressed):
                self.speed[0] -= (abs(stiffness)) * (self.speed[0] / (abs(self.speed[0])))

    def set_attachments(self, mask: bool = True, weapon: bool = True):
        self.mask = mask
        self.weapon = weapon

    def _animate(self):
        if self.rect.bottom < 300:
            self.image = self.anim_frames[2]
        elif abs(self.speed[0]):
            self.anim_index += 0.15
            if self.anim_index >= 2:
                self.anim_index = 0
            self.image = self.anim_frames[int(self.anim_index)]
        else:
            self.anim_index = 0
            self.image = self.anim_frames[self.anim_index]

    def update(self):
        self._movement()
        # self.draw_attachments()
        self._animate()


class Mask(pygame.sprite.Sprite):
    def __init__(self, _player: Player):
        super().__init__()
        self.image = pygame.transform.scale(_player.game.rooster_mask, (90, 95))
        self.rect = self.image.get_rect()
        self.body = _player

    def update(self):
        if not self.body.mask:
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(0)
        self.rect.center = (self.body.rect.midtop[0] + 7, self.body.rect.midtop[1] + 23)


class Weapon(pygame.sprite.Sprite):
    def __init__(self, _player: Player):
        super().__init__()
        self.image = pygame.transform.scale(_player.game.weapon, (120, 60))
        self.rect = self.image.get_rect()
        self.body = _player

    def update(self):
        if not self.body.weapon:
            self.image.set_alpha(100)
        else:
            self.image.set_alpha(0)
        self.rect.midleft = (self.body.rect.left, self.body.rect.midleft[1] + 15)
