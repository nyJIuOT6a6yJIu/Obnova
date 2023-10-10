import pygame
from sys import exit

import math

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Obnova v0.0.0.1')
clock = pygame.time.Clock()
pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)

sun_surf = pygame.Surface((100, 100))
sky_surf = pygame.image.load('graphics/Sky.png')
ground_surf = pygame.image.load('graphics/ground.png')

label_surf = pixel_font.render('Pososi)))', True, 'Black')

t_red = 0
t_green = 0
t_blue = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    red = int((0.975 + 0.025*math.cos(t_red * math.pi / 60))*255)
    green = int((0.6 + 0.3*math.cos((t_green+2) * math.pi / 63)) * 255)
    blue = int((0.4 + 0.3*math.cos((t_blue+3) * math.pi / 57)) * 255)

    screen.blit(sky_surf, (0, 0))
    screen.blit(ground_surf, (0, 300))
    sun_surf.fill((red, green, blue))
    t_red = (t_red + 3) % 120
    t_green = (t_green + 2) % 126
    t_blue = (t_blue - 2) % 114
    screen.blit(sun_surf, (650, 30))

    screen.blit(label_surf, (300, 50))

    # in the end
    # it doesn't even matter
    pygame.display.update()
    clock.tick(60)