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
    def process_scheduler(self):
        self.start_time = '06:00'
        self.stop_time = '22:00'
        
        try:
            print("Press CTRL-C to stop")
            self.process()
            
            scheduler1 = schedule.Scheduler()
            scheduler1.every().day.at(self.start_time).do(self.process)
            
            while True:
                #now = datetime.datetime.now()
                #today = datetime.date.today()
                #tomorrow_start = today + datetime.delta(days=1, hours=14, minutes=21)
                
                n = scheduler1.idle_seconds                
                print('Seconds till next start: '+str(n))
                if n > 0:
                    # sleep exactly the right amount
                    time.sleep(n)
                print('Run pending...')
                scheduler1.run_pending()
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

    def process(self):
        print('Process started')
        #schedule.clear('start_process') # schedule is singleton. We don't want it re-running this process in the loop below
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
        scheduler2 = schedule.Scheduler()
        scheduler2.every(5).minutes.do(self.run_threaded, weather_service.process)
        scheduler2.every(1).minutes.do(self.run_threaded, calendar_service.process)
        self.active = True;
        scheduler2.every().day.at(self.stop_time).do(self.stop_process)

        try:
            print("Press CTRL-C to stop")
            while self.active:
                scheduler2.run_pending()
                datetime_service.process()
                weather_service.animate_icon()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)

        #matrix = None
        #del matrix
        #schedule.clear('service_process')
        scheduler2.clear()  # The is necessary to release resources and stop the matrix running


    def run_threaded(self, job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()
        
    def stop_process(self):
        self.active = False


# Main function
if __name__ == "__main__":
    noticeboard = Noticeboard()
    noticeboard.process_scheduler()
