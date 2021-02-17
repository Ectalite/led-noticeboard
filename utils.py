from PIL import Image
from PIL import ImageDraw
from rgbmatrix import graphics

class Utils(object):
    @staticmethod
    def draw_blank_image(matrix, x, y, w, h):
        image = Image.new('RGB', (w, h))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, w-1, h-1), fill=(0, 0, 0), outline=(0, 0, 0))
        matrix.SetImage(image, x, y)
