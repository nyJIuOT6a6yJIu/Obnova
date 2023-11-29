import math

class ColorSine:

    def __repr__(self):
        return str(self.return_color())

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

    def convert_from_abs(self, color):  # TODO: Add slamp
        self.phases[0] = math.acos((color[0]/255 - self.statics[0]) / self.ampls[0])
        self.phases[1] = math.acos((color[1]/255 - self.statics[1]) / self.ampls[1])
        self.phases[2] = math.acos((color[2]/255 - self.statics[2]) / self.ampls[2])
        self.red, self.green, self.blue = 0, 0, 0

    def return_color(self) -> tuple:
        red = int((self.statics[0] + self.ampls[0] * math.cos(self.phases[0] + (self.red * self.freqs[0] * math.pi / 180))) * 255)
        green = int((self.statics[1] + self.ampls[1] * math.cos(self.phases[1] + (self.green * self.freqs[1] * math.pi / 180))) * 255)
        blue = int((self.statics[2] + self.ampls[2] * math.cos(self.phases[2] + (self.blue * self.freqs[2] * math.pi / 180))) * 255)
        return max(red, 0), max(green, 0),  max(blue, 0)

    def increment(self, inc=1.0):
        if self.freqs[0]:
            self.red = round((self.red + inc) % (360 / self.freqs[0]), 3)
        if self.freqs[1]:
            self.green = round((self.green + inc) % (360 / self.freqs[1]), 3)
        if self.freqs[2]:
            self.blue = round((self.blue + inc) % (360 / self.freqs[2]), 3)

# a = ColorSine([0, 0, 0], [1, 1, 1], statics=[0.5, 0.5, 0.5], ampls=[0.5, 0.5, 0.5])
# print(a)
# a.convert_from_abs((45, 145, 0))
# print(a)
