# LED Weather Station

![LED Matrix](photos/LEDMatrix.jpg?raw=true "LED Matrix")

Beautiful LED Matrix to display the weather! Powered by the Raspberry Pi and Adafruit RGB Matrix Hat.

### Hardware
  1. Raspberry Pi with internet connection
  2. Adafruit RGB Matrix Hat
  3. LED Matrix

### Software
  1. Sign up for API key at http://openweathermap.org/api
  2. Clone this repo to RPi and navigate to the directory
  3. Install [rpi-rgb-led-matrix python bindings](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/bindings/python/README.md)
  4. Install required Python packages
  ```
  $ sudo apt-get install python3-dev
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install google-api-python-client pillow google_auth_oauthlib
  ```
  5. Edit `config.json` and enter your location and API key
  6. Run the Weather Station with `$ python3 noticeboard.py &`

### Author
* **Joe Samela** - *Initial work* - [josephsamela.github.io](https://josephsamela.github.io/)
