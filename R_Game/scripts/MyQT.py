import math
import random

import pygame


class CheckBox(pygame.sprite.Sprite):
    def __init__(self, game, text, pos):
        super().__init__()
        self.game = game
        self.state = False
        self.text = text
        self.image = game.text_to_surface_mf(text, True, 'Red', size=38)
        self.rect = self.image.get_rect(center=pos)

    def collide(self, pos):
        if self.rect.left - 16 < pos[0] and \
           self.rect.right > pos[0] and \
           self.rect.top < pos[1] and \
           self.rect.bottom > pos[1]:
            return True
        return False

    def on_click(self):
        self.state = not self.state

    def update(self):
        pos = (self.rect.left - 10, self.rect.centery - 3)
        pygame.draw.circle(self.game.screen, 'Red', pos, 8, 3)
        if self.state:
            pygame.draw.circle(self.game.screen, 'Red', pos, 7)


class CB_CheckBox(CheckBox):
    def __init__(self, game, text, pos):
        super().__init__(game, text, pos)
        if game.progress.get('sralker_unlocked', False):
            self.text = " Colorblind mode (beaten)"
            self.image = game.text_to_surface_mf(self.text, True, 'Red', size=38)
            self.rect = self.image.get_rect(midleft=self.rect.midleft)

    def on_click(self):
        super().on_click()
        if self.state == True:
            self.game.UI_endless.sprites()[0].state = False

    def update(self):
        super().update()
        if self.game.progress.get('sralker_unlocked', False) and not self.text.endswith('(beaten)'):
            self.text = " Colorblind mode (beaten)"
            self.image = self.game.text_to_surface_mf(self.text, True, 'Red', size=38)
            self.rect = self.image.get_rect(midleft=self.rect.midleft)


class EndlessMode_CheckBox(CheckBox):
    def __init__(self, game, text, pos):
        super().__init__(game, text, pos)
        self.hiscore = game.progress.get('endless_highscore', 0)
        if self.hiscore > 0:
            self.text = f" Endless mode ({self.hiscore} pts)"
            self.image = game.text_to_surface_mf(self.text, True, 'Red', size=38)
            self.rect = self.image.get_rect(midleft=self.rect.midleft)
            self.rect.right = 790

    def on_click(self):
        super().on_click()
        if self.state == True:
            self.game.UI_colorblind.sprites()[0].state = False

    def update(self):
        super().update()

        if self.hiscore != self.game.progress.get('endless_highscore', 0):
            self.hiscore = self.game.progress.get('endless_highscore', 0)
            self.text = f" Endless mode ({self.hiscore} pts)"
            self.image = self.game.text_to_surface_mf(self.text, True, 'Red', size=38)
            self.rect = self.image.get_rect(midleft=self.rect.midleft)

        self.rect.right = 790


class Epilepsy_CheckBox(CheckBox):
    def __init__(self, game, text, pos):
        super().__init__(game, text, pos)
        self.state = game.progress.get('epilepsy_setting', False)

    def on_click(self):
        super().on_click()
        self.game.progress['epilepsy_setting'] = self.state
        self.game.no_epilepsy = self.state

    def update(self):
        super().update()

        self.rect.right = 790