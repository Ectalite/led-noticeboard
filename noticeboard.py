#coding=utf-8
from PIL import Image
from PIL import ImageDraw
import schedule
import time
import json
import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import datetime
import pickle
import os.path
from googleapiclient.discovery import build

# Weather settings held in file weather-data.json
# Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
# Include app id generated when you make you account at: http://openweathermap.org/api
with open('config.json') as json_file:
    config = json.load(json_file)
    weather_config = config['weather']
    location = weather_config['location']
    appid = weather_config['appid']
    calendar_config = config['calendar']
    calendarId = calendar_config['calendarId']

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.panel_type = 'FM6126A'
matrix = RGBMatrix(options = options)

font = graphics.Font()
font.LoadFont('fonts/5x7.bdf')

smallFont = graphics.Font()
smallFont.LoadFont("fonts/tom-thumb.bdf")
        

def drawimage(path, x, y):
    image = Image.open(path).convert('RGB')
    image.load()
    matrix.SetImage(image, x, y)

def weatherJob():
    # Clear matrix
    #matrix.Clear()

    # Pull fresh weather data
    try:
        response = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&units=metric&cnt=10&appid='+appid)

        data = json.loads(response.text)
        print('Weather data: ' + str(data))
        main = data['main']

        #Get Current Conditions
        temp = main['temp']
        temp = int(round(temp))

        weather = data['weather']
        weather = weather[0]
        icon = weather['icon']

        Conditions = weather['id']

        #Draw weather icon
        if Conditions == 900:
            icon = 'tornado'
        elif Conditions == 901 or Conditions == 902:
            icon = 'hurricane'
        elif Conditions == 906 or Conditions == 611 or Conditions == 612:
            icon = 'hail'
        elif Conditions == 600 or Conditions == 601 or Conditions == 602:
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

        drawimage('weathericons/' + icon + '.png', 0, 0)

        # Clear current temp
        image = Image.new('RGB', (24, 15))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 23, 14), fill=(0, 0, 0), outline=(0, 0, 0))
        matrix.SetImage(image, 16, 0)

        graphics.DrawText(matrix, font, 17, 7, tempColor, tempFormatted)


    except requests.exceptions.RequestException as e:
        drawimage('weathericons/' + 'error' + '.png', 0, 0)


def timeJob():
    #try:
        color = graphics.Color(255, 0, 255)

        now = datetime.datetime.now()
        onOff = (time.mktime(now.timetuple()) %2 == 0)

        if onOff:
            current_time = now.strftime("%H:%M")
        else:
            current_time = now.strftime("%H %M")

        current_date = now.strftime("%a%d")

        image = Image.new('RGB', (24, 15))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 23, 14), fill=(0, 0, 0), outline=(0, 0, 0))
        matrix.SetImage(image, 40, 0)

        graphics.DrawText(matrix, font, 40, 7, color, current_time)
        graphics.DrawText(matrix, font, 40, 14, color, current_date)

    #except Exception as e:
     #   print(e)
     

def calendarJob():
    try:
        
        # If modifying these scopes, delete the file token.pickle.
        #SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            print('invalid creds. run the quickstart')

        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        toDate = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() + 'T00:00:00Z'
        print('Getting the upcoming events')
        print('From: '+now)
        print('To: '+toDate)
        events_result = service.events().list(calendarId=calendarId,
                                            timeMin=now, timeMax=toDate, maxResults=3, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')

        # Clear previous list
        image = Image.new('RGB', (64, 17))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 63, 16), fill=(0, 0, 0), outline=(0, 0, 0))
        matrix.SetImage(image, 0, 15)

        color = graphics.Color(255, 255, 51)       
        pos = 20
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event['summary']
            print(start, summary)
            graphics.DrawText(matrix, smallFont, 0, pos, color, summary)
            pos+=6


    except Exception as e:
        print(e)


weatherJob()
calendarJob()
schedule.every(5).minutes.do(weatherJob)
schedule.every(1).minutes.do(calendarJob)

while True:
    schedule.run_pending()
    timeJob()
    time.sleep(1)
