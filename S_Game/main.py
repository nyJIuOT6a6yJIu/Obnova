import math
import random
from enum import Enum, auto

import pygame

from R_Game.config.config import DISPLAY_CAPTION
from S_Game.config.config import SRALKER_SCREEN_RESOLUTION

from S_Game.scripts.player_sprite import Player
from S_Game.scripts.misc_sprites import PlayingStalkers

from R_Game.scripts.color_sine import ColorSine

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

        self.sky_color = ColorSine(phases=[math.pi * 0.5, math.pi * 0.7, 0.0],
                                   freqs=[1.1, 0.2, 1.0],
                                   statics=[0.5, 0.7, 0.7],
                                   ampls=[0.5, 0.3, 0.3])

        self.game_state = self.GameState.MAINFRAME
        self.last_time_frame = 0
        self.clock = pygame.time.Clock()

        self.load_images()

        self.player = pygame.sprite.GroupSingle()
        self.player_sprite = Player(self, pos=[300, 400])
        self.player.add(self.player_sprite)

        self.obstacles = pygame.sprite.Group()

        self.playing_stalkers = PlayingStalkers(self, [500, 150])
        self.obstacles.add(self.playing_stalkers)

        # obs = pygame.sprite.Sprite()
        # obs.image = pygame.Surface([20, 80])
        # obs.rect = obs.image.get_rect(center=[500, 350])
        # self.obstacles.add(obs)

        self.delta_time = 0

        return self.game_loop()

    def load_images(self):
        self.player_walk_1 = pygame.image.load('R_Game/graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('R_Game/graphics/Player/player_walk_2.png').convert_alpha()
        self.player_stand = pygame.image.load('R_Game/graphics/Player/player_stand.png').convert_alpha()

        self.alex_anim_frames = []

        _path = 'S_Game/graphics/playing_stalkers/alex_anim_frames/alex_frame_'
        for i in range(1, 10):
            _frame = pygame.image.load(f"{_path}{str(i)}.png").convert_alpha()
            self.alex_anim_frames.append(_frame)

        _idle_frame = pygame.image.load("S_Game/graphics/playing_stalkers/bob_anim_frames/bob_idle.png").convert_alpha()
        _idle_frame_2 = pygame.image.load("S_Game/graphics/playing_stalkers/bob_anim_frames/bob_idle_2.png").convert_alpha()
        _shuffle_frame = pygame.image.load("S_Game/graphics/playing_stalkers/bob_anim_frames/bob_shuffle.png").convert_alpha()
        _shuffle_frame_2 = pygame.image.load("S_Game/graphics/playing_stalkers/bob_anim_frames/bob_shuffle_2.png").convert_alpha()
        _throw_frame = pygame.image.load("S_Game/graphics/playing_stalkers/bob_anim_frames/bob_throw.png").convert_alpha()

        self.bob_anim_frames = [_idle_frame, _idle_frame_2, _idle_frame, _idle_frame_2, _idle_frame,
                                _shuffle_frame, _shuffle_frame_2, _shuffle_frame, _shuffle_frame_2,
                                _throw_frame]

        _inhale_frame = pygame.image.load("S_Game/graphics/playing_stalkers/vasya_anim_frames/vasya_inhale.png").convert_alpha()
        _intermediate_frame = pygame.image.load("S_Game/graphics/playing_stalkers/vasya_anim_frames/vasya_interm.png").convert_alpha()
        _exhale_frame = pygame.image.load("S_Game/graphics/playing_stalkers/vasya_anim_frames/vasya_exhale.png").convert_alpha()

        self.vasya_anim_frames = [_exhale_frame,
                                  _exhale_frame,
                                  _exhale_frame,
                                  _intermediate_frame,
                                  _inhale_frame,
                                  _inhale_frame,
                                  _inhale_frame,
                                  _inhale_frame,
                                  _intermediate_frame,
                                  _exhale_frame,
                                  _exhale_frame]

        self.board = pygame.image.load("S_Game/graphics/playing_stalkers/board.png").convert_alpha()

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
        # self.screen.fill("#00a000")#26e11e")
        self.screen.fill(self.sky_color.return_color())
        inc = self.delta_time * 3 / 100
        self.sky_color.increment(inc)

        self.player.update()

        _draw_underlay = bool(self.player_sprite.rect.centery > self.playing_stalkers.rect.centery)
        if _draw_underlay:
            self.playing_stalkers.underlay.draw(self.screen)
        self.player.draw(self.screen)
        if not _draw_underlay:
            self.playing_stalkers.overlay.draw(self.screen)

        self.obstacles.update()
        #self.obstacles.draw(self.screen)
