#coding=utf-8
from PIL import Image
from PIL import ImageDraw
import schedule
import time
import json
import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import datetime

# Weather settings held in file weather-data.json
# Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
# Include app id generated when you make you account at: http://openweathermap.org/api
with open('weather-data.json') as json_file:
    data = json.load(json_file)
    location = data['location']
    appid = data ['appid']

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


weatherJob()
schedule.every(5).minutes.do(weatherJob)

while True:
    schedule.run_pending()
    timeJob()
    time.sleep(1)
