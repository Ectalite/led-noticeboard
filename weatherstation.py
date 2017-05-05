import Image
import ImageDraw
import schedule
import time
import json
import requests
from rgbmatrix import Adafruit_RGBmatrix

#Enter Location code found at: http://openweathermap.org/help/city_list.txt
location = '4954380' #Waltham, MA
#location = '4835654' #Hamden, CT

#Include app id generated when you make you account at: http://openweathermap.org/api
appid = '26d71701f80249205ff46efa3570822f'

#Define Matrix Dimensions
matrix=Adafruit_RGBmatrix(32,1)

def job():
    try:
        response = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+location+'&mode=json&cnt=10&appid='+appid)
    except requests.exceptions.RequestException as e:
        matrix.Clear()  
        image = Image.open('weathericons/' + 'error' + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)
    
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
    matrix.Clear()
    
    if Conditions == 900:
        image = Image.open('weathericons/' + 'tornado' + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)
    elif Conditions == 901 or Conditions == 902:
        image = Image.open('weathericons/' + 'hurricane' + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)
    elif Conditions == 906 or Conditions == 611 or Conditions == 612:
        image = Image.open('weathericons/' + 'hail' + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)
    elif Conditions == 600 or Conditions == 601 or Conditions == 602:
        image = Image.open('weathericons/' + 'snow' + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)
    else: 
        image = Image.open('weathericons/' + icon + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 1)

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
        image = Image.open('numbericons/' + str(TempComponents[0]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 11, 16)

        image = Image.open('numbericons/' + 'F' + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 17, 16)

    if TempLength == 2:
        image = Image.open('numbericons/' + str(TempComponents[0]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 7, 16)

        image = Image.open('numbericons/' + str(TempComponents[1]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 13, 16)

        image = Image.open('numbericons/' + 'F' + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 19, 16)

    if TempLength == 3:
        image = Image.open('numbericons/' + str(TempComponents[0]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 5, 16)

        image = Image.open('numbericons/' + str(TempComponents[1]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 9, 16)

        image = Image.open('numbericons/' + str(TempComponents[2]) + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 15, 16)

        image = Image.open('numbericons/' + 'F' + TempColor + '.png')
        image.load()
        matrix.SetImage(image.im.id, 21, 16)


    print('Current Temp: '+str(temp)+' Icon Code: '+str(icon))

job()
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
