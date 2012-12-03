"""#extend pandas BDay class to incorporate various
stock exchange holidays"""

from  pandas.tseries.offsets import *
from datetime import date, datetime, timedelta
import pandas as pd
import myLogger

# create logger
module_logger = myLogger.TLogger(__name__)

#gives names to calendar numbers for readability and to use globally within module
Monday      = 1
Tuesday     = 2
Wednesday   = 3
Thursday    = 4
Friday      = 5
Saturday    = 6
Sunday      = 7

January     = 1
February    = 2
March       = 3
April       = 4
May         = 5
June        = 6
July        = 7
August      = 8
September   = 9
October     = 10
November    = 11
December    = 12

class Singleton(type):
    """Need a Singleton class to make all HolidayProfiles singletons.
       Each HolidayProfile can only bee instantiated once.
       HolidayProfile defines a metaclass that uses this SIngleton class."""
    
    def __call__(self, *args, **kwargs):
        if 'instance' not in self.__dict__:
            self.instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.instance

class HolidayProfile(object):

    """HolidayProfile is the superclass for all calendars. Per default Saturday and Sunday are weekends and are not business days. 
       This needs to be overwritten for Arabic countries where Friday and Saturday are weekends.
       No national holidays are declared in this base class. These can be added in subclass by overwriting the isHoliday() function.
       Contains a function to calculate Easter for a given year. This is often needed for Western calendars and was put in the base class
       so that all subclasses inherit the function.
       It also contains a function to calculate the Vernal and Autumn Equinox which is needed for Asian calendars.

       >>> h = HolidayProfile()
       >>> HolyNight_Tuesday = datetime(2008, 12, 24)
       >>> h.isWeekend(HolyNight_Tuesday)
       False
       >>> h.isHoliday(HolyNight_Tuesday)
       False
       >>> h.isBusinessDay(HolyNight_Tuesday)
       True
       >>> NewYear_Sunday = datetime(2012, 1, 1)
       >>> h.isWeekend(NewYear_Sunday)
       True
       >>> h.isHoliday(NewYear_Sunday)
       False
       >>> h.isBusinessDay(NewYear_Sunday)
       False
       >>> IndependenceDay_Wednesday = datetime(2012, 7, 4)
       >>> h.isWeekend(IndependenceDay_Wednesday)
       False
       >>> h.isHoliday(IndependenceDay_Wednesday)
       False
       >>> h.isBusinessDay(IndependenceDay_Wednesday)
       True
       >>> h.EasterSunday(2012)
       datetime.date(2012, 4, 8)
    """

    __metaclass__ = Singleton # see http://stackoverflow.com/questions/100003/what-is-a-metaclass-in-python

    def __init__(self):
        self.logger = myLogger.TLogger(self.__class__.__name__)
        self.logger.debug("Creating holiday profile: {}".format(self.__class__.__name__))
        
    def isWeekend(self, date):
        """In this base class Weekend is defined as Saturday and Sunday. For differen weekends, e.g. Saudi Arabia this method needs to be overwritten. """
        return date.isoweekday() > Friday

    def isHoliday(self, date):
        """No holidays defined in the base class. Returns falls for all dates."""
        return False
        
    def isBusinessDay(self, date):
        """If not weekend or holiday it's a business day."""
        return not(self.isWeekend(date) or self.isHoliday(date))
        
    def EasterSunday(self, year):
        """Returns Easter as a date object.
        Uses the Butcher alogrithm. The date for Easter is needed for most Western calendars."""
        a = year % 19
        b = year // 100
        c = year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        month = f // 31
        day = f % 31 + 1
        return date(year, month, day)
        
    def VernalEquinox(self, year):
        """Returns vernal equinox as date object.
        Needed for some Eastern calendars."""
        exact_vernal_equinox_time = 20.69115
        ve = self.__Equinox(exact_vernal_equinox_time, year)
        return ve
        
    def AutumnalEquinox(self,year):
        """Returns autunal equinox as date object.
        Needed for some Eastern calendars."""
        exact_autumnal_equinox_time = 23.09
        ae = self.__Equinox(exact_autumnal_equinox_time, year)
        return ae
        
    def __Equinox(self, equinoxtime, y):
        diff_per_year = 0.242194;
        moving_amount = (y-2000)*diff_per_year
        number_of_leap_years = (y-2000)//4+(y-2000)//100-(y-2000)//400
        equinoxday = equinoxtime + moving_amount - number_of_leap_years
        return int(equinoxday)
        

class NYSE(HolidayProfile):

    """ Holiday Profile for the New York Stock Exchange.
    
        >>> h = NYSE()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> IndependenceDay_Wednesday = datetime(2012, 7, 4)
        >>> h.isWeekend(IndependenceDay_Wednesday)
        False
        >>> h.isHoliday(IndependenceDay_Wednesday)
        True
        >>> h.isBusinessDay(IndependenceDay_Wednesday)
        False
    """

    def isHoliday(self, date):
        
        self.logger.debug("Calculating holiday for {}".format(date))
        #split date into components for easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # Presidential election days
            (y % 4 == 0 and m == November and d <= 7 and w == Tuesday)
            # New Year's Day (possibly moved to Monday if on Sunday)
            or ((d == 1 or (d == 2 and w == Monday)) and m == January)
            # Washington's birthday (third Monday in February)
            or ((d >= 15 and d <= 21) and w == Monday and m == February)
            # Good Friday
            or (date == es- 2 * dayoffset)
            # Memorial Day (last Monday in May)
            or (d >= 25 and w == Monday and m == May)
            # Independence Day (Monday if Sunday or Friday if Saturday)
            or ((d == 4 or (d == 5 and w == Monday) or
            (d == 3 and w == Friday)) and m == July)
            # Labor Day (first Monday in September)
            or (d <= 7 and w == Monday and m == September)
            # Thanksgiving Day (fourth Thursday in November)
            or ((d >= 22 and d <= 28) and w == Thursday and m == November)
            # Christmas (Monday if Sunday or Friday if Saturday)
            or ((d == 25 or (d == 26 and w == Monday) or
            (d == 24 and w == Friday)) and m == December)
            # Martin Luther King's birthday (third Monday in January)
            or ((d >= 15 and d <= 21) and w == Monday and m == January)
            # President Reagan's funeral
            or (y == 2004 and m == June and d == 11)
            #September 11, 2001
            or (y == 2001 and m == September and (11 <= d and d <= 14))
            # President Ford's funeral
            or (y == 2007 and m == January and d == 2)
            #1977 Blackout
            or (y == 1977 and m == July and d == 14)
            #Funeral of former President Lyndon B. Johnson.
            or (y == 1973 and m == January and d == 25)
            # Funeral of former President Harry S. Truman
            or (y == 1972 and m == December and d == 28)
            # National Day of Participation for the lunar exploration.
            or (y == 1969 and m == July and d == 21)
            # Funeral of former President Eisenhower.
            or (y == 1969 and m == March and d == 31)
            # Closed all day - heavy snow.
            or (y == 1969 and m == February and d == 10)
            # Day after Independence Day.
            or (y == 1968 and m == July and d == 5)
            #June 12-Dec. 31, 1968
            # Four day week (closed on Wednesdays) - Paperwork Crisis
            or (y == 1968 and dd >= 163 and w == Wednesday))

        return holiday


class LSE(HolidayProfile):

    """ Holiday Profile fand the London Stock Exchange.
        >>> h = LSE()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        #  split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # New Year's Day (possibly moved to Monday)
            ((d == 1 or ((d == 2 or d == 3) and w == Monday)) and m == January)
            #Good Friday
            or (date == es - 2*dayoffset)
            #Easter Monday
            or (date == es + dayoffset)
            #first Monday of May (Early May Bank Holiday)
            or (d <= 7 and w == Monday and m == May)
            #last Monday of May (Spring Bank Holiday)
            or (d >= 25 and w == Monday and m == May and y != 2002)
            #last Monday of August (Summer Bank Holiday)
            or (d >= 25 and w == Monday and m == August)
            # Christmas (possibly moved to Monday and Tuesday)
            or ((d == 25 or (d == 27 and (w == Monday or w == Tuesday))) and m == December)
            #Boxing Day (possibly moved to Monday and Tuesday)
            or ((d == 26 or (d == 28 and (w == Monday or w == Tuesday))) and m == December)
            #June 3rd, 2002 only (Golden Jubilee Bank Holiday)
            #June 4rd, 2002 only (special Spring Bank Holiday)
            or ((d == 3 or d == 4) and m == June and y == 2002)
            #June 5th, 2012 only (Diamond Jubilee Bank Holiday)
            or (d == 5 and m == June and y == 2012)
            #December 31st, 1999 only
            or (d == 31 and m == December and y == 1999))
            
        return holiday


class LME(HolidayProfile):

    """ Holiday Profile fand the London Metal Exchange.
        >>> h = LME()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # New Year's Day (possibly moved to Monday)
            ((d == 1 or ((d == 2 or d == 3) and w == Monday)) and m == January)
            #Good Friday
            or (date == es - 2*dayoffset)
            #Easter Monday
            or (date == es + dayoffset)
            # first Monday of May (Early May Bank Holiday)
            or (d <= 7 and w == Monday and m == May)
            # last Monday of May (Spring Bank Holiday)
            or (d >= 25 and w == Monday and m == May and y != 2002)
            # last Monday of August (Summer Bank Holiday)
            or (d >= 25 and w == Monday and m == August)
            # Christmas (possibly moved to Monday and Tuesday)
            or ((d == 25 or (d == 27 and (w == Monday or w == Tuesday))) and m == December)
            # Boxing Day (possibly moved to Monday and Tuesday)
            or ((d == 26 or (d == 28 and (w == Monday or w == Tuesday))) and m == December)
            # June 3rd, 2002 only (Golden Jubilee Bank Holiday)
            # June 4rd, 2002 only (special Spring Bank Holiday)
            or ((d == 3 or d == 4) and m == June and y == 2002)
            #June 5th, 2012 only (Diamond Jubilee Bank Holiday)
            or (d == 5 and m == June and y == 2012)
            # December 31st, 1999 only
            or (d == 31 and m == December and y == 1999))

        return holiday


class BOVESPA(HolidayProfile):
    """ Holiday Profile fand the Sao Paolo Stock Exchange (Bovespa) and the Brazilian Mercantile and Futures Exchange (BM&F).
        >>> h = LME()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
    
            # New Year's Day
            (d == 1 and m == January)
            # Sao Paulo City Day
            or (d == 25 and m == January)
            # Tiradentes Day
            or (d == 21 and m == April)
            # Labor Day
            or (d == 1 and m == May)
            # Revolution Day
            or (d == 9 and m == July)
            # Independence Day
            or (d == 7 and m == September)
            # Nossa Sra. Aparecida Day
            or (d == 12 and m == October)
            # All Souls Day
            or (d == 2 and m == November)
            # Republic Day
            or (d == 15 and m == November)
            # Black Consciousness Day
            or (d == 20 and m == November and y >= 2007)
            # Christmas
            or (d == 25 and m == December)
            # Passion of Christ
            #TODO: change this
            or (date == es-2 * dayoffset )
            # Carnival
            or (date == es-49 * dayoffset or date == es-48 * dayoffset)
            # Corpus Christi
            or (date== es + 59 * dayoffset)
            # last business day of the year
            or (m == December and (d == 31 or (d >= 29 and w == Friday)))
            )

        return holiday
    
class ASX(HolidayProfile):
    
    """ Holiday Profile for the Australian Stock Exchange (ASX).
        >>> h = LME()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
    
            # New Year's Day (possibly moved to Monday)
            (d == 1  and m == January)
            # Australia Day, January 26th (possibly moved to Monday)
            or ((d == 26 or ((d == 27 or d == 28) and w == Monday)) and m == January)
            #Good Friday
            or (date == es - 2*dayoffset)
            #Easter Monday
            or (date == es + dayoffset)
            # ANZAC Day, April 25th (possibly moved to Monday)
            or ((d == 25 or (d == 26 and w == Monday)) and m == April)
            # Queen's Birthday, second Monday in June
            or ((d > 7 and d <= 14) and w == Monday and m == June)
            # Bank Holiday, first Monday in August
            or (d <= 7 and w == Monday and m == August)
            # Labour Day, first Monday in October
            or (d <= 7 and w == Monday and m == October)
            # Christmas, December 25th (possibly Monday or Tuesday)
            or ((d == 25 or (d == 27 and (w == Monday or w == Tuesday))) and m == December)
            # Boxing Day, December 26th (possibly Monday or Tuesday)
            or ((d == 26 or (d == 28 and (w == Monday or w == Tuesday))) and m == December)
            )

        return holiday

class TSX(HolidayProfile):
    
    """ Holiday Profile for the Toronto Stock Exchange (TSX).
        >>> h = LME()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # New Year's Day (possibly moved to Monday)
            ((d == 1 or (d == 2 and w == Monday)) and m == January)
            # Family Day (third Monday in February, since 2008)
            or ((d >= 15 and d <= 21) and w == Monday and m == February and y >= 2008)
            # Good Friday
            or (date == es-2 * dayoffset)
            # The Monday on or preceding 24 May (Victoria Day)
            or (d > 17 and d <= 24 and w == Monday and m == May)
            # July 1st, possibly moved to Monday (Canada Day)
            or ((d == 1 or ((d == 2 or d == 3) and w == Monday)) and m==July)
            # first Monday of August (Provincial Holiday)
            or (d <= 7 and w == Monday and m == August)
            # first Monday of September (Labor Day)
            or (d <= 7 and w == Monday and m == September)
            # second Monday of October (Thanksgiving Day)
            or (d > 7 and d <= 14 and w == Monday and m == October)
            # Christmas (possibly moved to Monday or Tuesday)
            or ((d == 25 or (d == 27 and (w == Monday or w == Tuesday))) and m == December)
            # Boxing Day (possibly moved to Monday or Tuesday)
            or ((d == 26 or (d == 28 and (w == Monday or w == Tuesday))) and m == December)
            )

        return holiday
        
class FSE(HolidayProfile):

    """ Holiday Profile fand the Frankfurt Stock Exchange.
        >>> h = FSE()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # New Year's Day
            (d == 1 and m == January)
            # Good Friday
            or (date== es-2*dayoffset)
            # Easter Monday
            or (date == es + dayoffset)
            # Labour Day
            or (d == 1 and m == May)
            # Christmas' Eve
            or (d == 24 and m == December)
            # Christmas
            or (d == 25 and m == December)
            # Christmas Day
            or (d == 26 and m == December)
            # New Year's Eve
            or (d == 31 and m == December))

        return holiday
        
class MIL(HolidayProfile):

    """ Holiday Profile fand the Mil Stock Exchange (Borsa Italiana).
        >>> h = MIL()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> NewYear_Sunday = datetime(2012, 1, 1)
        >>> h.isWeekend(NewYear_Sunday)
        True
        >>> h.isHoliday(NewYear_Sunday)
        True
        >>> h.isBusinessDay(NewYear_Sunday)
        False
        >>> DiamondJubilee_Tuesday = datetime(2012, 6, 5)
        >>> h.isWeekend(DiamondJubilee_Tuesday)
        False
        >>> h.isHoliday(DiamondJubilee_Tuesday)
        True
        >>> h.isBusinessDay(DiamondJubilee_Tuesday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday() #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day    #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        dayoffset = pd.offsets.Day(1)

        holiday =   (
            # New Year's Day
            (d == 1 and m == January)
            # Good Friday
            or (date== es-2*dayoffset)
            # Easter Monday
            or (date == es + dayoffset)
            # Labour Day
            or (d == 1 and m == May)
            # Assumption
            or (d == 15 and m == August)
            # Christmas' Eve
            or (d == 24 and m == December)
            # Christmas
            or (d == 25 and m == December)
            # St. Stephen
            or (d == 26 and m == December)
            # New Year's Eve
            or (d == 31 and m == December))

        return holiday

class TSE(HolidayProfile):

    """ Holiday Profile fand the Tokio Stock Exchange.
        >>> h = TSE()
        >>> HolyNight_Tuesday = datetime(2008, 12, 24)
        >>> h.isWeekend(HolyNight_Tuesday)
        False
        >>> h.isHoliday(HolyNight_Tuesday)
        False
        >>> h.isBusinessDay(HolyNight_Tuesday)
        True
        >>> AutumnalEuinoxDay_Wednesday = datetime(2009, 9, 23)
        >>> h.isWeekend(AutumnalEuinoxDay_Wednesday)
        False
        >>> h.isHoliday(AutumnalEuinoxDay_Wednesday)
        True
        >>> h.isBusinessDay(AutumnalEuinoxDay_Wednesday)
        False
        >>> VernalEquinoxDay_Tueday = datetime(2012, 3, 20)
        >>> h.isWeekend(VernalEquinoxDay_Tueday)
        False
        >>> h.isHoliday(VernalEquinoxDay_Tueday)
        True
        >>> h.isBusinessDay(VernalEquinoxDay_Tueday)
        False
    """

    def isHoliday(self, date):
        
        #split date into components fand easy readability in holiday rules below
        w = date.isoweekday()   #where Monday is 1 and Sunday is 7
        m = date.month          #Between 1 and 12 inclusive.
        d = date.day            #Between 1 and the number of days in the given month of the given year.
        y = date.year            #Between MINYEAR and MAXYEAR inclusive.
        es = self.EasterSunday(y)
        ve = self.VernalEquinox(y)
        ae = self.AutumnalEquinox(y)
        dayoffset = pd.offsets.Day(1)
        
        holiday =   (
            # New Year's Day
            (d == 1  and m == January)
            # Bank Holiday
            or (d == 2  and m == January)
            # Bank Holiday
            or (d == 3  and m == January)
            # Coming of Age Day (2nd Monday in January),
            # was January 15th until 2000
            or (w == Monday and (d >= 8 and d <= 14) and m == January and y >= 2000)
            or ((d == 15 or (d == 16 and w == Monday)) and m == January and y < 2000)
            # National Foundation Day
            or ((d == 11 or (d == 12 and w == Monday)) and m == February)
            # Vernal Equinox
            or ((d == ve or (d == ve+1 and w == Monday)) and m == March)
            # Greenery Day
            or ((d == 29 or (d == 30 and w == Monday)) and m == April)
            # Constitution Memandial Day
            or (d == 3  and m == May)
            # Holiday fand a Nation
            or (d == 4  and m == May)
            # Children's Day
            or (d == 5  and m == May)
            # any of the three above observed later if on Saturday and Sunday
            or (d == 6 and m == May and (w == Monday or w == Tuesday or w == Wednesday))
            # Marine Day (3rd Monday in July),
            # was July 20th until 2003, not a holiday befande 1996
            or (w == Monday and (d >= 15 and d <= 21) and m == July and y >= 2003)
            or ((d == 20 or (d == 21 and w == Monday)) and m == July and y >= 1996 and y < 2003)
            # Respect fand the Aged Day (3rd Monday in September),
            # was September 15th until 2003
            or (w == Monday and (d >= 15 and d <= 21) and m == September and y >= 2003)
            or ((d == 15 or (d == 16 and w == Monday)) and m == September and y < 2003)
            # If a single day falls between Respect fand the Aged Day
            # and the Autumnal Equinox, it is holiday
            or (w == Tuesday and d+1 == ae and d >= 16 and d <= 22 and m == September and y >= 2003)
            # Autumnal Equinox
            or ((d == ae or (d == ae+1 and w == Monday)) and m == September)
            # Health and Spandts Day (2nd Monday in October),
            # was October 10th until 2000
            or (w == Monday and (d >= 8 and d <= 14) and m == October and y >= 2000)
            or ((d == 10 or (d == 11 and w == Monday)) and m == October and y < 2000)
            # National Culture Day
            or ((d == 3  or (d == 4 and w == Monday)) and m == November)
            # Laband Thanksgiving Day
            or ((d == 23 or (d == 24 and w == Monday)) and m == November)
            # Emperand's Birthday
            or ((d == 23 or (d == 24 and w == Monday)) and m == December and y >= 1989)
            # Bank Holiday
            or (d == 31 and m == December)
            # one-shot holidays
            # Marriage of Prince Akihito
            or (d == 10 and m == April and y == 1959)
            # Rites of Imperial Funeral
            or (d == 24 and m == February and y == 1989)
            # Enthronement Ceremony
            or (d == 12 and m == November and y == 1990)
            # Marriage of Prince Naruhito
            or (d == 9 and m == June and y == 1993)
            )

        return holiday

class BusinessDayWithHolidays(BDay):
    """ Extends the pandas business day function with an holiday parameter
    in order to account for holidays to determine business days.
    A holiday profile class for that holiday calendar with the same name needs to exist.
    
    Pass a string for a holiday profile to create one or pass a holiday profile object to the function.
    
    """

    def __init__(self, n=1, **kwds):
        self.logger = myLogger.TLogger(__name__)
        super(BusinessDayWithHolidays, self).__init__(n, **kwds)
        self.holidays = kwds.get('holidays', "NYSE")
        
            #if string is passed instead of a HolidayProfile create the HolidayProfile from the string
        if isinstance(self.holidays, str):
            try:
                a = self.holidays
                self.holidays =  eval(a)()  # create a holiday profile from string
            except TypeError:
                print "Could not create a Holiday Profil    e for" + self.holidays + ". Does it exist?" 
        
        #this could be used to check if the object passed was a Holiday Profile, but that's non pythonic
        #if not isinstance(self.holidays, HolidayProfile):
        #    raise Exception (str(self.holidays) + " is not a Holiday Profile object.") 
        
    @property
    def rule_code(self):
        return 'BH'

    def apply(self, other):
            self.logger.debug("Apply was called with {}".format(other))
            if isinstance(other, datetime):
                n = self.n

                if n == 0 and not self.holidays.isBusinessDay(other):
                    n = 1

                result = other

                # avoid slowness below
                #if abs(n) > 5:
                #    k = n // 5
                #    result = result + timedelta(7 * k)
                #    n -= 5 * k

                while n != 0:
                    k = n // abs(n)
                    result = result + timedelta(k)
                    if self.holidays.isBusinessDay(result):
                        n -= k

                if self.normalize:
                    result = datetime(result.year, result.month, result.day)

                if self.offset:
                    result = result + self.offset

                return result

            elif isinstance(other, (timedelta, Tick)):
                return BDay(self.n, offset=self.offset + other,
                            normalize=self.normalize)
            else:
                raise Exception('Only know how to combine business day with '
                                'datetime or timedelta!')

    def onOffset(self, date):
        return self.holidays.isBusinessDay(date)

if __name__ == "__main__" :
    module_logger.info('Running EnhancedBDay main')
    #import doctest
    #doctest.testmod(verbose=True)
    day1 = datetime(2008, 12, 30)
    day2 = datetime(2008, 12, 24)
    print day1 - 2 * BDay()
    print day1 - 2 * BusinessDayWithHolidays()
