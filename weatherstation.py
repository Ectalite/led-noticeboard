from PIL import Image
from PIL import ImageDraw
import schedule
import time
import json
import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# Enter Location code found at: http://bulk.openweathermap.org/sample/city.list.json.gz
location = '2750065' #Nijkerk, NL
#location = '4954380' #Waltham, MA

# Include app id generated when you make you account at: http://openweathermap.org/api
appid = '26d71701f80249205ff46efa3570822f'

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
options.panel_type = 'FM6126A'
matrix = RGBMatrix(options = options)

def drawimage(path, x, y):
    image = Image.open(path).convert('RGB')
    image.load()
    matrix.SetImage(image, x, y)

def job():
    # Clear matrix
    matrix.Clear()

    # Pull fresh weather data
    try:
        response = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&cnt=10&appid='+appid)

        data = json.loads(response.text)
        main = data['main']

        #Get Current Conditions
        temp = main['temp']
        temp = ((temp-273.15)*(1.8)+32)
        temp = int(round(temp))

        weather = data['weather']
        weather = weather[0]
        icon = weather['icon']

        Conditions = weather['id']

        #Draw weather icon
        if Conditions == 900:
            drawimage('weathericons/' + 'tornado' + '.png', 9, 1)
        elif Conditions == 901 or Conditions == 902:
            drawimage('weathericons/' + 'hurricane' + '.png', 9, 1)
        elif Conditions == 906 or Conditions == 611 or Conditions == 612:
            drawimage('weathericons/' + 'hail' + '.png', 9, 1)
        elif Conditions == 600 or Conditions == 601 or Conditions == 602:
            drawimage('weathericons/' + 'snow' + '.png', 9, 1)
        else: 
            drawimage('weathericons/' + icon + '.png', 9, 1)

        #Draw temperature
        TempComponents = str(temp)
        TempLength = len(TempComponents)

        # Sets Temperature Color
        if temp <= 32:
            TempColor = 'b'
        elif temp > 90:
            TempColor = 'r'
        else:
            TempColor = 'w'

        if TempLength == 1:
            drawimage('numbericons/' + str(TempComponents[0]) + TempColor + '.png', 11, 16)
            drawimage('numbericons/' + 'F' + TempColor + '.png', 17, 16)

        if TempLength == 2:
            drawimage('numbericons/' + str(TempComponents[0]) + TempColor + '.png', 7, 16)
            drawimage('numbericons/' + str(TempComponents[1]) + TempColor + '.png', 13, 16)

            drawimage('numbericons/' + 'F' + TempColor + '.png', 19, 16)

        if TempLength == 3:
            drawimage('numbericons/' + str(TempComponents[0]) + TempColor + '.png', 5, 16)
            drawimage('numbericons/' + str(TempComponents[1]) + TempColor + '.png', 9, 16)
            drawimage('numbericons/' + str(TempComponents[2]) + TempColor + '.png', 15, 16)
            drawimage('numbericons/' + 'F' + TempColor + '.png', 21, 16)

        print('Current Temp: '+str(temp)+' Icon Code: '+str(icon))

    except requests.exceptions.RequestException as e:
        drawimage('weathericons/' + 'error' + '.png', 9, 1)

job()
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
