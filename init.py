import pygame
import traceback

from R_Game.main import HMGame
from R_Game.error_window import show_error_window

from R_Game.config.config import SCREEN_RESOLUTION, DISPLAY_CAPTION

from some_function import load, save


def main():
    progress = load()

    screen = pygame.display.set_mode(SCREEN_RESOLUTION)
    pygame.display.set_caption(DISPLAY_CAPTION)
    screen.blit(pygame.image.load('R_Game/graphics/banners/loading_1.png'), (0, 0))
    pygame.display.update()

    game = HMGame(screen, progress)

    try:
        new_save = game.start_game()
        save(new_save)
    except Exception as e:
        error_text = f'Error type: {e}\n\n{traceback.format_exc()}'
        with open('error_log.txt', 'w') as file:
            file.write(error_text)

        pygame.mixer.Sound('R_Game/audio/misc sounds/kill_run_init.mp3').play()
        show_error_window()


if __name__ == '__main__':
    main()
    