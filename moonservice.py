import datetime
import decimal
import random
from rgbmatrix import graphics
import moonphase

class MoonService():
    def __init__(self, font):
        self.font = font
        self.color = graphics.Color(255, 100, 255)
        self.star_tracker = []
        self.sky = []

    def process(self, matrix, force_update):
        if force_update:
            self.update(matrix)

        self.animate_stars(matrix)

    def update(self, matrix):
        pos = moonphase.position()
        print("Moon phase "+str(pos))
        self.phase = moonphase.phase_short(pos)

        width, height = 38, 26
        a, b = 18, 12
        r = 12.5
        d = decimal.Decimal(r*2)

        if pos <= 0.5:
            diff = -(d*2) * pos
        else:
            diff = (d*2) * (1 - pos)

        self.sky = []
        matrix.Clear()

        for y in range(height):
            for x in range(width):
                in_circle = (x-a)**2 + (y-b)**2 < r**2
                not_in_dark = (x-a-diff)**2 + (y-b)**2 > r**2

                if in_circle and not_in_dark:
                    matrix.SetPixel(x, y, 235, 200, 21)
                else:
                    self.sky.append((x, y))

        print("Sky positions: "+str(len(self.sky)))
        graphics.DrawText(matrix, self.font, 40, 21, self.color, self.phase)

    def animate_stars(self, matrix):
        new = random.randint(0, 20)
        if new == 0:
            new_star = random.choice(self.sky)
            self.star_tracker.append(new_star)

            if len(self.star_tracker) > 20:
                old_star = self.star_tracker.pop(0)
                matrix.SetPixel(old_star[0], old_star[1], 0, 0, 0)

        for star in self.star_tracker:
            twinkle = random.randint(0, 4)
            if twinkle == 0:
                matrix.SetPixel(star[0], star[1], 200, 200, 200)
            else:
                matrix.SetPixel(star[0], star[1], 255, 255, 255)
