# here will be sunray logic
import pygame
from pygame.sprite import Sprite, Group
import math
# from pygame.math import


class SunGroup(Group):
    def __init__(self, game):
        super().__init__()
        self.game = game
        # self.start_moment = start_moment
        self.add(SunRay(game, -105))
        self.add(SunRay(game, -65))
        self.add(SunRay(game, -25))
        self.add(SunRay(game, 15))
        self.add(SunRay(game, 55))
        self.add(SunRay(game, 95))
        self.add(SunRay(game, 135))
        self.add(SunRay(game, 175))
        self.add(SunRay(game, 215))

    def update(self, time_pass):
        angle = 7 * self.game.delta_time / 1000
        if time_pass > 8700:
            alpha = int(127.5*(1 - math.cos((time_pass - 8700)*math.pi/10000)))
        else:
            alpha = 0
        for i in self.sprites():
            i.update(angle, alpha)


class SunRay(Sprite):
    def __init__(self, game, init_angle):
        super().__init__()
        self.game = game
        self.ref_image = self.game.sun_ray
        self.angle = 0
        self.rotate_by(angle=init_angle)
        # TODO: dynamic angular velocity
        # self.image = self.game.sun_ray
        # self.rect = self.image.get_rect()

    def rotate_by(self, angle):  #=None):
        self.angle += angle
        self.image = pygame.transform.rotozoom(self.ref_image, self.angle, 1)
        new_center = (365+int(252*math.cos(self.angle*math.pi/180)),
                      170-int(252*math.sin(self.angle*math.pi/180)))
        self.rect = self.image.get_rect(center=new_center)

    def update(self, angle, alpha):
        self.rotate_by(angle)
        self.image.set_alpha(alpha)
        # if self.angle > 225:
        #     self.angle = -45
