import pygame
from sys import exit
from scripts.color_sine import ColorSine
import math

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Obnova v0.0.0.1')
clock = pygame.time.Clock()
pixel_font = pygame.font.Font('font/Pixeltype.ttf', 50)

colorChange = ColorSine(phases= [math.pi*0.5, math.pi*0.7, 0],
                        freqs = [1.1, 0.2, 1],
                        statics=[0.5, 0.7, 0.7],
                        ampls = [0.5, 0.3, 0.3])

color_surf = pygame.Surface((800, 300))
sky_surf = pygame.image.load('graphics/Sky_miami.png').convert_alpha()

ground_surf = pygame.image.load('graphics/ground.png').convert()

score = 0
score_surf = pixel_font.render(f'Score: {score}', True, 'Black')
score_rect = score_surf.get_rect(center=(400, 50))

snail_surf = pygame.image.load('graphics/snail/snail1.png').convert_alpha()
snail_rect = snail_surf.get_rect(midbottom=(760, 300))

dog_surf = pygame.transform.scale(pygame.image.load('graphics/snail/dog.png').convert_alpha(), (35, 45))
dog_rect = dog_surf.get_rect(bottomleft=snail_rect.bottomleft)

player_surf = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
player_rect = player_surf.get_rect(midbottom=(80, 300))

rooster_surf = pygame.transform.scale(pygame.image.load('graphics/Player/rooster.png').convert_alpha(), (90, 95))
rooster_rect = rooster_surf.get_rect(center=player_rect.midtop)

gun_surf = pygame.transform.scale(pygame.image.load('graphics/GUN.png').convert_alpha(), (120, 60))
gun_rect = gun_surf.get_rect(midleft=(player_rect.left, player_rect.midleft[1]+15))

after_image = []

gun_sound = pygame.mixer.Sound('audio/gunshot.mp3')
gun_sound.set_volume(1.1)

bg_music = pygame.mixer.Sound('audio/miami.mp3')
bg_music.set_volume(0.3)
bg_music.play(loops = -1)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] and snail_rect.collidepoint(pygame.mouse.get_pos()):
                after_image.append([8, snail_rect.center])
                snail_rect.left = 800
                score += 1
                gun_sound.play()

    screen.blit(ground_surf, (0, 300))

    color = colorChange.return_color()
    color_surf.fill(color)

    screen.blit(color_surf, (0, 0))
    screen.blit(sky_surf, (0, 0))

    score_surf = pixel_font.render(f'Score: {score}', True, 'Black')
    screen.blit(score_surf, score_rect)

    screen.blit(player_surf, player_rect)
    rooster_rect.center=(player_rect.midtop[0]+7, player_rect.midtop[1]+23)
    screen.blit(rooster_surf, rooster_rect)
    gun_rect.midleft = (player_rect.left, player_rect.midleft[1] + 15)
    screen.blit(gun_surf, gun_rect)
    screen.blit(snail_surf, snail_rect)
    dog_rect.bottomleft = (snail_rect.bottomleft[0]-5, snail_rect.bottomleft[1])
    screen.blit(dog_surf, dog_rect)

    if snail_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.line(screen, "Red", (gun_rect.midright[0]-30, gun_rect.midright[1]-3), pygame.mouse.get_pos(),
                         width=2)

    for index, i in enumerate(after_image):
        if i[0] > 0:
            pygame.draw.line(screen, (255, 255, 100), (gun_rect.midright[0]-8, gun_rect.midright[1]-4), i[1],
                         width = int(6 * math.sin(i[0]*math.pi/8)))
            i[0] -= 1
        else:
            after_image.pop(index)

    colorChange.increment()
    snail_rect.left -= 4
    if snail_rect.right < 0: snail_rect.left = 800

    # in the end
    # it doesn't even matter
    pygame.display.update()
    clock.tick(60)
