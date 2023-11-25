from json import loads, dumps
import pygame

from src.main import HMGame

from src.config.config import SCREEN_RESOLUTION

try:
    with open('saves/save') as file:
        progress = loads(file.read())
except:  # ловлю всі ерори і мені похуй абсолютно
    progress = None

screen = pygame.display.set_mode(SCREEN_RESOLUTION)
screen.blit(pygame.image.load('src/graphics/loading_1.png'), (0, 0))
pygame.display.update()

game = HMGame(screen, progress)

new_save = game.start_game()
new_save = dumps(new_save)
with open('saves/save', mode='w') as file:
    file.write(new_save)
