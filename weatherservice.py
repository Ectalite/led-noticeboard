#coding=utf-8
import datetime
import json
import requests
import threading

from PIL import Image
from rgbmatrix import graphics

from utils import Utils


class WeatherService():
    def __init__(self, config, font):
        self.gif_lock = threading.Lock()
        self.font = font

        #location = config['location']
        lat = config['lat']
        lon = config['lon']
        appid = config['appid']

        #weather_url = 'http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&units=metric&cnt=10&appid='+appid
        self.weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=minutely,daily,alerts&appid={appid}'.format(
            lat=lat, lon=lon, appid=appid)

        self.last_run = datetime.datetime(2000, 1, 1)

    def process(self, matrix, interval_minutes):
        now = datetime.datetime.now()
        if (now - self.last_run).seconds >= interval_minutes*60:
            self.last_run = now
            job_thread = threading.Thread(target=self.update, args=(matrix,))
            job_thread.start()

        self.animate_icon(matrix)

    def update(self, matrix):
        # Clear matrix
        #matrix.Clear()

        # Pull fresh weather data
        try:
            response = requests.get(self.weather_url)
            data = json.loads(response.text)
            #print('Weather data: ' + str(data))

            #current = data['main']
            current = data['current']

            #Get Current Conditions
            temp = current['temp']
            temp = int(round(temp))

            #weather = data['weather']
            weather = current['weather']
            weather = weather[0]
            icon = weather['icon']

            conditions = weather['id']

            #Get rain forecast
            forecastHour = data['hourly'][1];
            rainProb = forecastHour['pop']
            timestamp = forecastHour['dt']
            dt_object = datetime.datetime.fromtimestamp(timestamp)

            #Draw weather icon
            if conditions == 900:
                icon = 'tornado'
            elif conditions == 901 or conditions == 902:
                icon = 'hurricane'
            elif conditions == 906 or conditions == 611 or conditions == 612:
                icon = 'hail'
            elif conditions == 600 or conditions == 601 or conditions == 602:
                icon = 'snow'

            print('Forecast time: {0}, Current Temp: {1}, Icon Code: {2}'.format(dt_object, temp, icon))

            #Draw temperature
            # Sets Temperature Color
            if temp >= 20:
                tempColor = graphics.Color(255, 0, 0)
            elif temp >= 15:
                tempColor = graphics.Color(255, 128, 0)
            elif temp >= 10:
                tempColor = graphics.Color(255, 255, 0)
            elif temp >= 5:
                tempColor = graphics.Color(0, 255, 255)
            else:
                tempColor = graphics.Color(0, 0, 255)

            tempFormatted = str(temp) + "°C"
            rainFormatted = str(int(rainProb*100)) + '%'

            image_file = 'weathericons/' + icon + '.gif'

            with self.gif_lock:
                self.weather_image = Image.open(image_file)
                self.weather_image_frame = 0
                self.weather_image_max = self.weather_image.n_frames
                #print('Weather image frame count: '+str(self.weather_image_max))

            # Clear current temp
            Utils.draw_blank_image(matrix, 16, 0, 24, 15)

            graphics.DrawText(matrix, self.font, 17, 7, tempColor, tempFormatted)
            graphics.DrawText(matrix, self.font, 17, 14, tempColor, rainFormatted)

        except requests.exceptions.RequestException as e:
            graphics.DrawText(matrix, self.font, 17, 7, tempColor, '???')


    def animate_icon(self, matrix):
        with self.gif_lock:
            try:
                self.weather_image.seek(self.weather_image_frame)
                matrix.SetImage(self.weather_image.convert('RGB'))
                self.weather_image_frame += 1
                if self.weather_image_frame == self.weather_image_max:
                    self.weather_image_frame = 0
            except AttributeError:
                # catching error in case request hasn't completed and weather_image doesn't exist
                True

