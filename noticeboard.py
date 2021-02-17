#coding=utf-8
import schedule
import time
import json
import requests
import datetime
import pickle
import os.path
import sys
import threading
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Noticeboard(object):
    def process(self):
        # Weather settings held in file weather-data.json
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
        self.matrix = RGBMatrix(options = options)

        self.font = graphics.Font()
        self.font.LoadFont('fonts/5x7.bdf')

        self.smallFont = graphics.Font()
        self.smallFont.LoadFont("fonts/tom-thumb.bdf")

        gif_lock = threading.Lock()
        self.weatherJob(weather_config, gif_lock)
        self.calendarJob(calendar_config)
        schedule.every(5).minutes.do(self.run_threaded, self.weatherJob, (weather_config, gif_lock))
        schedule.every(1).minutes.do(self.run_threaded, self.calendarJob, (calendar_config,))

        try:
            print("Press CTRL-C to stop")
            while True:
                schedule.run_pending()
                self.timeJob()
                self.weatherIconJob(gif_lock)
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting\n")
            sys.exit(0)


    def drawimage(self, path, x, y):
        image = Image.open(path).convert('RGB')
        image.load()
        self.matrix.SetImage(image, x, y)

    def draw_blank_image(self, x, y, w, h):
        image = Image.new('RGB', (w, h))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, w-1, h-1), fill=(0, 0, 0), outline=(0, 0, 0))
        self.matrix.SetImage(image, x, y)

    def weatherJob(self, config, gif_lock):
        # Clear matrix
        #matrix.Clear()

        # Pull fresh weather data
        try:
            #location = config['location']
            lat = config['lat']
            lon = config['lon']
            appid = config['appid']

            #weather_url = 'http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&units=metric&cnt=10&appid='+appid
            weather_url = 'http://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units=metric&exclude=minutely,daily,alerts&appid={appid}'.format(
                lat=lat, lon=lon, appid=appid)

            response = requests.get(weather_url)
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
            forecastHour = data['hourly'][0];
            rainProb = forecastHour['pop']
            timestamp = forecastHour['dt']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            print('Forecast time: ' + str(dt_object))

            #Draw weather icon
            if conditions == 900:
                icon = 'tornado'
            elif conditions == 901 or conditions == 902:
                icon = 'hurricane'
            elif conditions == 906 or conditions == 611 or conditions == 612:
                icon = 'hail'
            elif conditions == 600 or conditions == 601 or conditions == 602:
                icon = 'snow'

            print('Current Temp: '+str(temp)+' Icon Code: '+str(icon))

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

            tempFormatted = unicode(str(temp), 'utf-8') + unicode('°C', 'utf-8')
            rainFormatted = str(int(rainProb*100)) + '%'

            #self.drawimage('weathericons/' + icon + '.png', 0, 0)
            image_file = 'weathericons/' + icon + '.gif'

            with gif_lock:
                self.weather_image = Image.open(image_file)
                self.weather_image_frame = 0
                self.weather_image_max = self.weather_image.n_frames
                print('Weather image frame count: '+str(self.weather_image_max))

            # Clear current temp
            self.draw_blank_image(16, 0, 24, 15)

            graphics.DrawText(self.matrix, self.font, 17, 7, tempColor, tempFormatted)
            graphics.DrawText(self.matrix, self.font, 17, 14, tempColor, rainFormatted)

        except requests.exceptions.RequestException as e:
            self.drawimage('weathericons/' + 'error' + '.png', 0, 0)


    def weatherIconJob(self, gif_lock):
        with gif_lock:
            self.weather_image.seek(self.weather_image_frame)
            self.matrix.SetImage(self.weather_image.convert('RGB'))
            self.weather_image_frame += 1
            if self.weather_image_frame == self.weather_image_max:
                self.weather_image_frame = 0


    def timeJob(self):
        #try:
            color = graphics.Color(255, 0, 255)

            now = datetime.datetime.now()
            onOff = (time.mktime(now.timetuple()) %2 == 0)

            if onOff:
                current_time = now.strftime("%H:%M")
            else:
                current_time = now.strftime("%H %M")

            current_date = now.strftime("%a%d")

            self.draw_blank_image(40, 0, 24, 15)

            graphics.DrawText(self.matrix, self.font, 40, 7, color, current_time)
            graphics.DrawText(self.matrix, self.font, 40, 14, color, current_date)

        #except Exception as e:
         #   print(e)


    def calendarJob(self, config):
        try:
            # If modifying these scopes, delete the file token.pickle.
            SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            toDate = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() + 'T00:00:00Z'
            print('Getting the upcoming events')
            print('From: '+now)
            print('To: '+toDate)
            calendarId = config['calendarId']
            events_result = service.events().list(calendarId=calendarId,
                                                timeMin=now, timeMax=toDate, maxResults=3, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')

            # Clear previous list
            self.draw_blank_image(0, 15, 64, 17)

            color = graphics.Color(255, 255, 51)
            pos = 20
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event['summary']
                print(start, summary)
                graphics.DrawText(self.matrix, self.smallFont, 0, pos, color, summary)
                pos+=6

        except Exception as e:
            print(e)

    def run_threaded(self, job_func, args):
        job_thread = threading.Thread(target=job_func, args=args)
        job_thread.start()


# Main function
if __name__ == "__main__":
    noticeboard = Noticeboard()
    noticeboard.process()
