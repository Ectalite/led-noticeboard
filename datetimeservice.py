import datetime
import time
from rgbmatrix import graphics
from utils import Utils


class DateTimeService(object):
    def __init__(self, matrix, font):
        self.matrix = matrix
        self.font = font
        self.color = graphics.Color(255, 0, 255)

    def process(self):
        #try:
            now = datetime.datetime.now()
            onOff = (time.mktime(now.timetuple()) %2 == 0)

            if onOff:
                current_time = now.strftime("%H:%M")
            else:
                current_time = now.strftime("%H %M")

            current_date = now.strftime("%a%d")

            Utils.draw_blank_image(self.matrix, 40, 0, 24, 8)  # Only clear time portion

            graphics.DrawText(self.matrix, self.font, 40, 7, self.color, current_time)
            graphics.DrawText(self.matrix, self.font, 40, 14, self.color, current_date)

        #except Exception as e:
         #   print(e)
