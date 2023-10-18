import math

class ColorSine:
    def __init__(self, phases, freqs, statics=None, ampls=None):
        self.red, self.green, self.blue = 0, 0, 0
        self.phases = phases
        self.freqs = freqs
        if statics:
            self.statics = statics
        else:
            self.statics = [0.5, 0.5, 0.6]
        if ampls:
            self.ampls = ampls
        else:
            self.ampls = [0.4, 0.5, 0.25]

        self.float_inc = 0.0

    def return_color(self) -> tuple:
        red = int((self.statics[0] + self.ampls[0] * math.cos(self.phases[0] + (self.red * self.freqs[0] * math.pi / 180))) * 255)
        green = int((self.statics[1] + self.ampls[1] * math.cos(self.phases[1] + (self.green * self.freqs[1] * math.pi / 180))) * 255)
        blue = int((self.statics[2] + self.ampls[2] * math.cos(self.phases[2] + (self.blue * self.freqs[2] * math.pi / 180))) * 255)
        return red, green, blue

    def increment(self, inc=1.0):
        if self.freqs[0]:
            self.red = round((self.red + inc) % (360 / self.freqs[0]), 3)
        if self.freqs[1]:
            self.green = round((self.green + inc) % (360 / self.freqs[1]), 3)
        if self.freqs[2]:
            self.blue = round((self.blue + inc) % (360 / self.freqs[2]), 3)

