import math
import random

import pygame


class CheckBox(pygame.sprite.Sprite):
    def __init__(self, game, text, pos):
        super().__init__()
        self.game = game
        # game.UI_group.add(self)
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
