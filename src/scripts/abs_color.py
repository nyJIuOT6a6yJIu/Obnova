class ColorAbs:

    def __repr__(self):
        return str(self.return_color())

    def __init__(self, color):
        self.red, self.green, self.blue = color

        self.float_inc = 0.0

        self.starting_color = None

    def return_color(self) -> tuple:
        return max(self.red, 0), max(self.green, 0),  max(self.blue, 0)

    def settle_for(self, target_color, seconds, time_pass_ms):
        if time_pass_ms > seconds * 1000 or self.return_color() == target_color:
            self.starting_color = None
            return True

        if self.starting_color is None:
            self.starting_color = self.return_color()

        self.red = (self.starting_color[0]*(1000 * seconds - time_pass_ms) + target_color[0] * time_pass_ms)//(1000 * seconds)
        self.green = (self.starting_color[1]*(1000 * seconds - time_pass_ms) + target_color[1] * time_pass_ms)//(1000 * seconds)
        self.blue = (self.starting_color[2]*(1000 * seconds - time_pass_ms) + target_color[2] * time_pass_ms)//(1000 * seconds)
        return False
