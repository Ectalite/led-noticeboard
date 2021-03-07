import datetime
import os.path
import pickle
import threading

from rgbmatrix import graphics
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from utils import Utils

class CalendarService(object):
    def __init__(self, config):
        self.calendarId = config['calendarId']
        self.font = graphics.Font()
        self.font.LoadFont("fonts/tom-thumb.bdf")
        self.color = graphics.Color(255, 255, 51)
        self.last_run = datetime.datetime(2000, 1, 1)

    def process(self, matrix, interval_minutes, max_events):
        now = datetime.datetime.now()
        if (now - self.last_run).seconds >= interval_minutes*60:
            self.last_run = now
            job_thread = threading.Thread(target=self.update, args=(matrix,max_events))
            job_thread.start()

    def update(self, matrix, max_events):
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            toDate = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() + 'T00:00:00Z'
            print('Getting upcoming events, from {0}, to {1}'.format(now, toDate))

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
            calendarId = self.calendarId
            events_result = service.events().list(calendarId=calendarId,
                                                timeMin=now, timeMax=toDate, maxResults=max_events, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            if not events:
                print('No upcoming events found.')

            # Clear previous list
            y_offset = 6 * (3-max_events)
            Utils.draw_blank_image(matrix, 0, 15 + y_offset, 64, 17)

            pos = 20 + y_offset
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event['summary']
                print(start, summary)
                graphics.DrawText(matrix, self.font, 0, pos, self.color, summary)
                pos+=6

        except Exception as e:
            print(e)

