import pygame
import traceback

from R_Game.config.config import DISPLAY_CAPTION

from R_Game.main import HMGame
from S_Game.main import SGame
from error_window import show_error_window
from switch_window import SwitchWindow

from some_function import load, save


def main():
    pygame.init()

    progress = load()
    # progress['sralker_opened'] = False

    pygame.display.set_caption(DISPLAY_CAPTION)

    try:
        new_save = progress
        if progress.get("sralker_opened", False):
            window = SwitchWindow()
            command = window.show_window()
        else:
            command = "launch_runner"
        while command is not None:
            if command == "launch_sralker":
                sralker_game = SGame(new_save)
                new_save, command = sralker_game.start_game()
            elif command == "launch_runner":
                runner_game = HMGame(new_save)
                new_save, command = runner_game.start_game()
            save(new_save)
    except Exception as e:
        error_text = f'Error type: {e}\n\n{traceback.format_exc()}'
        with open('error_log.txt', 'w') as file:
            file.write(error_text)

        pygame.mixer.Sound('R_Game/audio/misc sounds/kill_run_init.mp3').play()
        show_error_window()
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
    