import math
import random
from enum import Enum, auto

import pygame

from R_Game.config.config import DISPLAY_CAPTION
from S_Game.config.config import SRALKER_SCREEN_RESOLUTION

from S_Game.scripts.player_sprite import Player

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

        self.player_walk_1 = pygame.image.load('R_Game/graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('R_Game/graphics/Player/player_walk_2.png').convert_alpha()
        self.player_stand = pygame.image.load('R_Game/graphics/Player/player_stand.png').convert_alpha()

        self.player = pygame.sprite.GroupSingle()
        self.player_sprite = Player(self)
        self.player.add(self.player_sprite)

        self.obstacles = pygame.sprite.Group()
        obs = pygame.sprite.Sprite()
        obs.image = pygame.Surface([12, 12])
        obs.rect = obs.image.get_rect(center=[50, 50])
        self.obstacles.add(obs)
        obs = pygame.sprite.Sprite()
        obs.image = pygame.Surface([20, 80])
        obs.rect = obs.image.get_rect(center=[500, 350])
        self.obstacles.add(obs)
        obs = pygame.sprite.Sprite()
        obs.image = pygame.Surface([100, 120])
        obs.rect = obs.image.get_rect(center=[700, 500])
        self.obstacles.add(obs)

        self.delta_time = 0

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

            # players controls

            if event.type == pygame.KEYDOWN:
                self.player_sprite.player_input(event.key, False)
            if event.type == pygame.KEYUP:
                self.player_sprite.player_input(event.key, True)

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.player_sprite.player_input(event.button, False, event.pos)

    def mainframe(self):
        self.screen.fill([130, 240, 170])
        self.player.update()
        self.player.draw(self.screen)

        self.obstacles.update()
        self.obstacles.draw(self.screen)
