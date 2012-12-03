#DayCounter class

class DayCounter(object):
    
    """"How many days are there between two dates"""

    def __init__(self, startdate, enddate):
        self.name = "Simple Daycounter"
        self.yearfraction = __calcyearfraction(startdate, enddate)
        
    def __calcyearfraction (self, startdate, enddate):
        return enddate - startdate / 360.0
            
            
class Actual360(DayCounter):
    
     """Actual/360 day count convention
        Actual/360 day count convention, also known as "Act/360", or "A/360"."""
    
    def __init__(self, startdate, enddate):
        self.name = "Actual/360"
        self.yearfraction = __calcyearfraction(startdate, enddate)
        
    def __calcyearfraction (self, startdate, enddate):
        return enddate - startdate / 360.0
            
class Thirty360(DayCounter):

        """30/360 day counters"""
    
    def __init__(self, startdate, enddate):
        self.name = "30/360"
        self.yearfraction = __calcyearfraction(startdate, enddate)
        
    def __calcyearfraction (self, startdate, enddate):
        return enddate - startdate / 360.0
            
class ActualActual(DayCounter):
    
    """Actual/Actual day count
        The day count can be calculated according to:
        - the ISDA convention, also known as "Actual/Actual (Historical)",
        "Actual/Actual", "Act/Act", and according to ISDA also "Actual/365",
        "Act/365", and "A/365";
        - the ISMA and US Treasury convention, also known as
        "Actual/Actual (Bond)";
        - the AFB convention, also known as "Actual/Actual (Euro)".
        For more details, refer to
        http://www.isda.org/publications/pdf/Day-Count-Fracation1999.pdf"""
    
    def __init__(self, startdate, enddate):
        self.name = "Actual/Actual"
        self.yearfraction = __calcyearfraction(startdate, enddate)
        
    def __calcyearfraction (self, startdate, enddate):
        return enddate - startdate / 360.0
