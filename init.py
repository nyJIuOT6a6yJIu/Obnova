from json import loads, dumps
import pygame

from R_Game.main import HMGame

from R_Game.config.config import SCREEN_RESOLUTION, DISPLAY_CAPTION

try:
    with open('saves/save') as file:
        progress = loads(file.read())
except:  # ловлю всі ерори і мені похуй абсолютно
    progress = None

screen = pygame.display.set_mode(SCREEN_RESOLUTION)
pygame.display.set_caption(DISPLAY_CAPTION)
screen.blit(pygame.image.load('R_Game/graphics/banners/loading_1.png'), (0, 0))
pygame.display.update()

game = HMGame(screen, progress)

new_save = game.start_game()
new_save = dumps(new_save)
with open('saves/save', mode='w') as file:
    file.write(new_save)
