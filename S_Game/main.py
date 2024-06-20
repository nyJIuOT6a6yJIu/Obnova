import math
import random
from enum import Enum, auto

import pygame

from R_Game.config.config import DISPLAY_CAPTION
from S_Game.config.config import SRALKER_SCREEN_RESOLUTION

class SGame(object):
    # 48px = 1 meter

    class GameState(Enum):
        EXIT         = auto()
        LOADING      = auto()

        MAINFRAME    = auto()

    def __init__(self, progress=None):

        if progress is None:
            progress = dict()
        self.progress = progress

    def start_game(self):
        self.screen = pygame.display.set_mode(SRALKER_SCREEN_RESOLUTION)
        pygame.display.set_icon(pygame.image.load('R_Game/graphics/Player/rooster.png').convert_alpha())
        pygame.display.set_caption(DISPLAY_CAPTION)

        self.game_state = self.GameState.MAINFRAME
        self.last_time_frame = 0
        self.clock = pygame.time.Clock()

        return self.game_loop()

    def game_loop(self):
        while self.game_state != self.GameState.EXIT:
            self.last_time_frame = pygame.time.get_ticks()
            self.event_loop()
            match self.game_state:
                case self.GameState.MAINFRAME:
                    self.mainframe()
            if self.game_state != self.GameState.EXIT:
                pygame.display.update()
                self.clock.tick(60)
                self.delta_time = (pygame.time.get_ticks() - self.last_time_frame)
        return self.progress, None

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = self.GameState.EXIT

    def mainframe(self):
        pass
