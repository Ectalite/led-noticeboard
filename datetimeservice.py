import datetime
import time
from rgbmatrix import graphics
from utils import Utils


class DateTimeService(object):
    def __init__(self, font):
        self.font = font
        self.color = graphics.Color(255, 255, 255)

    def process(self, matrix):
        #try:
            now = datetime.datetime.now()
            onOff = (time.mktime(now.timetuple()) %2 == 0)

            if onOff:
                current_time = now.strftime("%H:%M")
            else:
                current_time = now.strftime("%H %M")

            current_date = now.strftime("%a%d")

            Utils.draw_blank_image(matrix, 40, 0, 24, 15)

            graphics.DrawText(matrix, self.font, 40, 7, self.color, current_time)
            graphics.DrawText(matrix, self.font, 40, 14, self.color, current_date)

        #except Exception as e:
         #   print(e)
