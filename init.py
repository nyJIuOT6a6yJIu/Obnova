import pygame

from R_Game.main import HMGame

from R_Game.config.config import SCREEN_RESOLUTION, DISPLAY_CAPTION

from some_function import load, save


def main():
    progress = load()

    screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.display.set_caption(DISPLAY_CAPTION)
    screen.blit(pygame.image.load('R_Game/graphics/banners/loading_1.png'), (0, 0))
    pygame.display.update()

    game = HMGame(screen, progress)

    new_save = game.start_game()

    save(new_save)


if __name__ == '__main__':
    main()
    