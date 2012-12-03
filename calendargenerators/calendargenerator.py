# Create a google calendar
# according to specific rules

#https://developers.google.com/google-apps/calendar/v1/developers_guide_python#GettingStarted

import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time

class GoogleCalendarGenerator(object):

    def __init__(self):
        pass
    
    def connect(self):
        pass
        
    def authenticate(self):
        calendar_service = gdata.calendar.service.CalendarService()
        calendar_service.email = 'thomas.haederle@gmail.com'
        calendar_service.password = '!Tgtlse05'
        calendar_service.source = 'Google-Calendar_Python_Sample-1.0'
        calendar_service.ProgrammaticLogin()
        
    def createCalendar(self, title, summary, where, Color='#2952A3',timezone):
        # Create the calendar
        calendar = gdata.calendar.CalendarListEntry()
        calendar.title = atom.Title(text=title)
        calendar.summary = atom.Summary(text=summary)
        calendar.where = gdata.calendar.Where(value_string=where)
        calendar.color = gdata.calendar.Color(value=Color)
        calendar.timezone = gdata.calendar.Timezone(value=timezone)
        calendar.hidden = gdata.calendar.Hidden(value='false')
        new_calendar = calendar_service.InsertCalendar(new_calendar=calendar)
        

 class GoogleCalendarSubscriber(object)
 
    def __init__(self):
        pass
        
    def subsribe(self, id):
        calendar = gdata.calendar.CalendarListEntry()
        calendar.id = atom.Id(text=id)
        returned_calendar = calendar_service.InsertCalendarSubscription(calendar)
        
    


