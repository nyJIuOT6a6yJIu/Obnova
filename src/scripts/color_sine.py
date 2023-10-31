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

        self.starting_color = None
        self.ms_pass = 0

    def return_color(self) -> tuple:
        red = int((self.statics[0] + self.ampls[0] * math.cos(self.phases[0] + (self.red * self.freqs[0] * math.pi / 180))) * 255)
        green = int((self.statics[1] + self.ampls[1] * math.cos(self.phases[1] + (self.green * self.freqs[1] * math.pi / 180))) * 255)
        blue = int((self.statics[2] + self.ampls[2] * math.cos(self.phases[2] + (self.blue * self.freqs[2] * math.pi / 180))) * 255)
        return red, green, blue

    def return_color_absolute(self) -> tuple:
        return self.red, self.green, self.blue

    def increment(self, inc=1.0):
        self.starting_color = None
        if self.freqs[0]:
            self.red = round((self.red + inc) % (360 / self.freqs[0]), 3)
        if self.freqs[1]:
            self.green = round((self.green + inc) % (360 / self.freqs[1]), 3)
        if self.freqs[2]:
            self.blue = round((self.blue + inc) % (360 / self.freqs[2]), 3)

    def settle_for(self, target_color, seconds, time_pass_ms): # TODO: fix for consecutive usage
        if self.starting_color is None:
            self.starting_color = self.return_color()
            # self.ms_pass = 0
        # self.ms_pass += delta_time
        if time_pass_ms > seconds * 1000:
            self.starting_color = None
            return True
        self.red = (self.starting_color[0]*(1000 * seconds - time_pass_ms) + target_color[0] * time_pass_ms)//(1000 * seconds)
        self.green = (self.starting_color[1]*(1000 * seconds - time_pass_ms) + target_color[1] * time_pass_ms)//(1000 * seconds)
        self.blue = (self.starting_color[2]*(1000 * seconds - time_pass_ms) + target_color[2] * time_pass_ms)//(1000 * seconds)
        # print(self.ms_pass, self.red, self.green, self.blue)
        return False
