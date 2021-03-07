import datetime
import json
import sys
import threading
import time

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from weatherservice import WeatherService
from datetimeservice import DateTimeService
from calendarservice import CalendarService
from moonservice import MoonService

class Noticeboard(object):
    def process(self):
        day_time = datetime.time(06, 00)
        evening_time = datetime.time(16, 30)
        night_time = datetime.time(20, 00)

        # Weather settings held in file config.json
        # Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
        # Include app id generated when you make you account at: http://openweathermap.org/api
        with open('config.json') as json_file:
            config = json.load(json_file)
            weather_config = config['weather']
            calendar_config = config['calendar']

        font = graphics.Font()
        font.LoadFont('fonts/5x7.bdf')

        weather_service = WeatherService(weather_config, font)
        datetime_service = DateTimeService(font)
        calendar_service = CalendarService(calendar_config)
        moon_service = MoonService(font)
        matrix = None
        day_mode = True

        try:
            print("Press CTRL-C to stop")

            while True:
                now = datetime.datetime.now()
                time_of_day = now.time()

                is_before = time_of_day < day_time
                is_after = time_of_day >= night_time

                if is_before or is_after:
                    matrix = None
                    start_time = datetime.datetime.combine(datetime.datetime.today(), day_time)
                    if is_after:
                        start_time = start_time + datetime.timedelta(days=1)

                    sleep_seconds = (start_time - now).seconds
                    print("Sleeping for seconds: " + str(sleep_seconds))
                    time.sleep(sleep_seconds)

                if matrix == None:
                    matrix = self.matrix()
                    time.sleep(1)   # Just allows the time to tick past the start time safely

                if time_of_day < evening_time:
                    weather_service.process(matrix, 5)
                    calendar_service.process(matrix, 1, 3)
                    day_mode = True
                elif time_of_day < night_time:
                    moon_service.process(matrix, day_mode)
                    calendar_service.process(matrix, 5, 1)
                    day_mode = False

                datetime_service.process(matrix)
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

    def matrix(self):
        # Configuration for the matrix
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.panel_type = 'FM6126A'
        #options.show_refresh_rate = 1
        #options.gpio_slowdown = 1
        #options.scan_mode = 1
        #options.limit_refresh_rate_hz = 100
        matrix = RGBMatrix(options = options)
        return matrix


# Main function
if __name__ == "__main__":
    noticeboard = Noticeboard()
    noticeboard.process()
