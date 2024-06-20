import pygame
import math

from R_Game.scripts.color_sine import ColorSine


class PushButton(pygame.sprite.Sprite):
    def __init__(self, parent, pos):
        super().__init__()

        self.parent = parent
        self.pos = pos

        self.return_value = None
        self.text = ""

        self.hover_images = []
        self.unhover_images = []

        # self.hover_rect = self.hover_image.get_rect(center=pos)
        # self.unhover_rect = self.unhover_image.get_rect(center=pos)

        self.hover_sound = None

        self.image = pygame.Surface((1, 1))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect(center=pos)

        self.color = "White"
        self.border_color = "Black"

        self.hovered = False

        self.min_size = 200
        self.max_size = 225

        self.size = self.min_size
        self.alpha_hover = 0

    def collide(self, pos):

        if self.pos[0] - self.size/2 < pos[0] < self.pos[0] + self.size/2 and \
           self.pos[1] - self.size/2 < pos[1] < self.pos[1] + self.size/2:
            return True
        return False

    def draw_central_image(self):
        pass

    def update(self):
        prev_status = self.hovered
        self.hovered = self.collide(pygame.mouse.get_pos())
        color = self.parent.bg_color.return_color()
        self.color = [pygame.math.clamp(190-i/2, 0, 255) for i in color]
        self.border_color = [pygame.math.clamp(305-i, 0, 255) for i in color]

        if prev_status != self.hovered and self.hovered and self.hover_sound:
            self.hover_sound.play()

        if self.hovered:
            delta_time = self.parent.delta_time
            if self.size != self.max_size:
                self.size = min(self.max_size, self.size + 100*delta_time/1000)
            if self.alpha_hover != 255:
                self.alpha_hover = min(255, self.alpha_hover + delta_time)
        elif not self.hovered:
            delta_time = self.parent.delta_time
            if self.size != self.min_size:
                self.size = max(self.min_size, self.size - 70 * delta_time / 1000)
            if self.alpha_hover != 0:
                self.alpha_hover = max(0, self.alpha_hover - delta_time)
        int_size = int(self.size)
        pygame.draw.rect(self.parent.screen, rect=pygame.Rect(self.pos[0] - int_size / 2,
                                                              self.pos[1] - int_size / 2,
                                                              int_size,
                                                              int_size),
                                             color=self.color, border_radius=20)

        if self.hovered:
            pygame.draw.rect(self.parent.screen, rect=pygame.Rect(self.pos[0] - int_size / 2,
                                                                  self.pos[1] - int_size / 2,
                                                                  int_size,
                                                                  int_size),
                             color=self.border_color, width=10, border_radius=20)

        for i in self.hover_images:
            i.set_alpha(self.alpha_hover)
        for i in self.unhover_images:
            i.set_alpha(255-self.alpha_hover)

        self.draw_central_image()

        label = self.parent.font.render(self.text, True, "Red")
        label_rect = label.get_rect(center=[self.pos[0], self.pos[1] + self.size//2 - 20])
        self.parent.screen.blit(label, label_rect)


class SralkerButton(PushButton):
    def __init__(self, parent, pos):
        super().__init__(parent, pos)

        self.return_value = "launch_sralker"
        self.text = "Sralker"

        self.images = [
            pygame.image.load('R_Game/graphics/Player/player_stand.png').convert_alpha(),
            pygame.image.load('R_Game/graphics/Player/player_walk_1.png').convert_alpha(),
            pygame.image.load('S_Game/graphics/equipment/gas_mask.png').convert_alpha(),
            pygame.image.load('R_Game/graphics/Player/GUN.png').convert_alpha()
        ]

        self.hover_images = [pygame.transform.scale(self.images[1], (95, 122)),
                             pygame.transform.scale(self.images[2], (120, 115)),
                             pygame.transform.scale(self.images[3], (190, 95))
                             ]

        self.unhover_images = [pygame.transform.scale(self.images[0], (90, 105)),
                               pygame.transform.scale(self.images[2], (105, 100)),
                               pygame.transform.scale(self.images[3], (140, 100))
                              ]
        self.unhover_images[2] = pygame.transform.rotate(self.unhover_images[2], 87)

        self.hover_sound = pygame.mixer.Sound('R_Game/audio/misc sounds/gun_pickup.mp3')
        self.hover_sound.set_volume(1.0)

    def draw_central_image(self):
        player_rect_hover = self.hover_images[0].get_rect(center=[self.pos[0]+5, self.pos[1]])
        gas_mask_rect_hover = self.hover_images[1].get_rect(center=[self.pos[0]+12, self.pos[1]-9])
        gun_rect_hover = self.hover_images[2].get_rect(center=[self.pos[0]+12, self.pos[1]+20])
        self.parent.screen.blit(self.hover_images[0], player_rect_hover)
        self.parent.screen.blit(self.hover_images[1], gas_mask_rect_hover)
        self.parent.screen.blit(self.hover_images[2], gun_rect_hover)

        player_rect_unhover = self.unhover_images[0].get_rect(center=[self.pos[0]+5, self.pos[1]])
        gas_mask_rect_unhover = self.unhover_images[1].get_rect(midtop=[player_rect_unhover.centerx+3,
                                                                        player_rect_unhover.top])
        gun_rect_unhover = self.unhover_images[2].get_rect(center=[self.pos[0]-25, self.pos[1]-20])
        self.parent.screen.blit(self.unhover_images[2], gun_rect_unhover)
        self.parent.screen.blit(self.unhover_images[0], player_rect_unhover)
        self.parent.screen.blit(self.unhover_images[1], gas_mask_rect_unhover)


class RunnerButton(PushButton):
    def __init__(self, parent, pos):
        super().__init__(parent, pos)

        self.return_value = "launch_runner"
        self.text = "Runner"

        self.images = [
            pygame.image.load('R_Game/graphics/Player/player_stand.png').convert_alpha(),
            pygame.image.load('R_Game/graphics/Player/jump.png').convert_alpha(),
            pygame.image.load('R_Game/graphics/Player/rooster.png').convert_alpha()
        ]

        self.hover_images = [pygame.transform.scale(self.images[1], (95, 122)),
                             pygame.transform.scale(self.images[2], (130, 120)),
                             ]
        #
        self.unhover_images = [pygame.transform.scale(self.images[0], (90, 105)),
                               pygame.transform.scale(self.images[2], (115, 108))
                              ]

        self.hover_sound = pygame.mixer.Sound('R_Game/audio/misc sounds/jump.mp3')
        self.hover_sound.set_volume(1.0)

    def draw_central_image(self):  # 370, 125
        player_rect_hover = self.hover_images[0].get_rect(center=[self.pos[0]+5, self.pos[1]])
        mask_rect_hover = self.hover_images[1].get_rect(midtop=[player_rect_hover.centerx+3,
                                                                player_rect_hover.top-15])
        self.parent.screen.blit(self.hover_images[0], player_rect_hover)
        self.parent.screen.blit(self.hover_images[1], mask_rect_hover)

        player_rect_unhover = self.unhover_images[0].get_rect(center=[self.pos[0]+5, self.pos[1]])
        mask_rect_unhover = self.unhover_images[1].get_rect(midtop=[player_rect_unhover.centerx+3,
                                                                        player_rect_unhover.top-15])
        self.parent.screen.blit(self.unhover_images[0], player_rect_unhover)
        self.parent.screen.blit(self.unhover_images[1], mask_rect_unhover)


class SwitchWindow:
    def __init__(self):
        self.return_value = None

        self.screen = pygame.display.set_mode((500, 250))
        pygame.display.set_icon(pygame.image.load('R_Game/graphics/Player/rooster.png').convert_alpha())
        pygame.display.set_caption('Choose your destiny')
        self.font = pygame.font.Font('R_Game/font/Pixeltype.ttf', 40)

        self.bg_color = ColorSine(phases= [math.pi, math.pi * 0.7, math.pi * 0.5],
                                   freqs=  [1.1,           0.2,           1.0],
                                   statics=[0.5,           0.7,           0.7],
                                   ampls=  [0.5,           0.3,           0.3])

        self.delta_time = 0

        self.button_group = pygame.sprite.Group()
        self.s_button = SralkerButton(self, [130, 125])
        self.r_button = RunnerButton(self, [370, 125])
        self.button_group.add([self.s_button, self.r_button])

    def show_window(self):
        while self.return_value is None:
            last_time_frame = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i in self.button_group:
                        if i.hovered:
                            self.return_value = i.return_value
                            pygame.mixer.Sound('R_Game/audio/misc sounds/kill_run_init.mp3').play()
                            break

            sky_color = self.bg_color.return_color()
            # inc = self.delta_time * 25 / 1000
            inc = self.delta_time / 40

            self.screen.fill(sky_color)
            self.bg_color.increment(inc)

            self.button_group.update()
            self.button_group.draw(self.screen)

            pygame.display.update()
            self.delta_time = (pygame.time.get_ticks() - last_time_frame)
        return self.return_value
