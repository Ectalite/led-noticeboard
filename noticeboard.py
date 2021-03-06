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
    def process_scheduler(self):
        day_time = datetime.time(06, 00)
        evening_time = datetime.time(16, 30)
        night_time = datetime.time(20, 00)

        # Weather settings held in file config.json
        # Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
        # Include app id generated when you make you account at: http://openweathermap.org/api
        with open('config.json') as json_file:
            config = json.load(json_file)
            self.weather_config = config['weather']
            self.calendar_config = config['calendar']

        try:
            print("Press CTRL-C to stop")

            while True:
                time_of_day = datetime.datetime.now().time()
                sleep_seconds = 300

                if time_of_day < day_time:
                    #sleep_seconds = (start_time - time_of_day).seconds
                    print("Waiting to start")
                elif time_of_day < evening_time:
                    self.day_process(evening_time)
                elif time_of_day < night_time:
                    self.evening_process(night_time)
                elif time_of_day >= night_time:
                    #sleep_seconds = (datetime.time(23, 59, 59) - time_of_day + start_time_day).seconds
                    print("Waiting to start the next day")

                time.sleep(sleep_seconds)

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

    def day_process(self, stop_time):
        print('Day process started')

        matrix = self.matrix()

        font = graphics.Font()
        font.LoadFont('fonts/5x7.bdf')

        weather_service = WeatherService(self.weather_config, matrix, font)
        datetime_service = DateTimeService(matrix, font)
        calendar_service = CalendarService(self.calendar_config, matrix, 3)

        weather_last_run = datetime.datetime(2000, 1, 1)
        calendar_last_run = datetime.datetime(2000, 1, 1)

        try:
            print("Press CTRL-C to stop")
            while True:
                now = datetime.datetime.now()
                if now.time() >= stop_time:
                    break

                weather_last_run = self.run_threaded(weather_service.process, now, weather_last_run, 5)
                calendar_last_run = self.run_threaded(calendar_service.process, now, calendar_last_run, 1)

                datetime_service.process()
                weather_service.animate_icon()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        print("Day process stopped")

    def evening_process(self, stop_time):
        print('Evening process started')

        matrix = self.matrix()

        font = graphics.Font()
        font.LoadFont('fonts/5x7.bdf')

        moon_service = MoonService(matrix, font)
        datetime_service = DateTimeService(matrix, font)
        calendar_service = CalendarService(self.calendar_config, matrix, 1)

        calendar_last_run = datetime.datetime(2000, 1, 1)

        moon_service.process()

        try:
            print("Press CTRL-C to stop")
            while True:
                now = datetime.datetime.now()
                if now.time() >= stop_time:
                    break
                
                moon_service.animate_stars()
                moon_service.render()
                calendar_last_run = self.run_threaded(calendar_service.process, now, calendar_last_run, 5)
                datetime_service.process()
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        print("Evening process stopped")


    def run_threaded(self, job_func, now, last_run, minutes):
        if (now - last_run).seconds >= minutes*60:
            job_thread = threading.Thread(target=job_func)
            job_thread.start()
            return now

        return last_run


# Main function
if __name__ == "__main__":
    noticeboard = Noticeboard()
    noticeboard.process_scheduler()
