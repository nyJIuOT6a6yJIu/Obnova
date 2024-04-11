import pygame
import math

from R_Game.scripts.color_sine import ColorSine


def show_error_window():
    _font = pygame.font.Font('R_Game/font/Pixeltype.ttf', 40)
    top_text = _font.render('Skill Issue.   Check error log', True, 'Red')
    top_text_rect = top_text.get_rect(midtop=(175, 10))

    screen = pygame.display.set_mode([350, 350])
    pygame.display.set_caption('Fatal Error')

    evil_poroh = pygame.transform.scale(pygame.image.load('R_Game/graphics/misc/poroh_V_ahui.png').convert_alpha(), (350, 350))
    evil_poroh_rect = evil_poroh.get_rect(midbottom=(175, 350))

    pygame.display.update()

    bg_color = ColorSine(phases= [math.pi * 0.5, math.pi * 0.7, 0.0],
                         freqs=  [1.1,           0.2,           1.0],
                         statics=[0.5,           0.7,           0.7],
                         ampls=  [0.5,           0.3,           0.3])

    exit = False

    delta_time = 0

    while not exit:
        last_time_frame = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit = True

        if exit:
            break

        sky_color = bg_color.return_color()
        inc = delta_time * 60 / 1000

        screen.fill(sky_color)
        bg_color.increment(inc)

        screen.blit(evil_poroh, evil_poroh_rect)
        screen.blit(top_text, top_text_rect)

        pygame.display.update()
        delta_time = (pygame.time.get_ticks() - last_time_frame)