import json
import schedule
import sys
import threading
import time

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from weatherservice import WeatherService
from datetimeservice import DateTimeService
from calendarservice import CalendarService


class Noticeboard(object):
    def process(self):
        # Weather settings held in file config.json
        # Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
        # Include app id generated when you make you account at: http://openweathermap.org/api
        with open('config.json') as json_file:
            config = json.load(json_file)
            weather_config = config['weather']
            calendar_config = config['calendar']

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

        font = graphics.Font()
        font.LoadFont('fonts/5x7.bdf')

        weather_service = WeatherService(weather_config, matrix, font)
        datetime_service = DateTimeService(matrix, font)
        calendar_service = CalendarService(calendar_config, matrix)

        weather_service.process()
        calendar_service.process()
        schedule.every(5).minutes.do(self.run_threaded, weather_service.process)
        schedule.every(1).minutes.do(self.run_threaded, calendar_service.process)

        try:
            print("Press CTRL-C to stop")
            while True:
                schedule.run_pending()
                datetime_service.process()
                weather_service.animate_icon()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

    def run_threaded(self, job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()


# Main function
if __name__ == "__main__":
    noticeboard = Noticeboard()
    noticeboard.process()
