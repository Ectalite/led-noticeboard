import random
from PIL import Image, ImageDraw
from rgbmatrix import graphics
import moonphase

class MoonService():
    def __init__(self, matrix, font):
        self.matrix = matrix
        self.font = font
        self.color = graphics.Color(255, 100, 255)
        self.star_tracker = []

    def process(self):
        pos = moonphase.position()
        self.phase = moonphase.phase_short(pos)
        
        #16 18 20 22 24 26 good
        d = 24
        if pos <= 0.5:
            diff = -50 * pos
        else:
            diff = 50 * (1 - pos)

        self.image = Image.new('RGB', (25, 25))
        draw = ImageDraw.Draw(self.image)
        draw.ellipse((0, 0, d, d), fill=(235, 200, 21), outline=(235, 200, 21))
        draw.ellipse((0+diff, 0, d+diff, d), fill=(0, 0, 0), outline=(0, 0, 0,))

    def render(self):
        self.matrix.SetImage(self.image, 6, 0)
        graphics.DrawText(self.matrix, self.font, 40, 21, self.color, self.phase)

    def animate_stars(self):
        x = random.randint(0, 63)
        y = random.randint(0, 31)
        self.star_tracker.append((x, y))
        self.matrix.SetPixel(x, y, 255, 255, 255)
        
        if len(self.star_tracker) > 20:
            old_star = self.star_tracker.pop(0)
            self.matrix.SetPixel(old_star[0], old_star[1], 0, 0, 0)

