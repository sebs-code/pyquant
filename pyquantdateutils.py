# -*- coding: utf-8 -*-
import datetime as dt
import time as tm
import myLogger

# create logger
module_logger = myLogger.TLogger(__name__)

##
# Convert an Excel number (presumed to represent a date, a datetime or a time) into
# a Python datetime.datetime
# @param xldate The Excel number
# @param datemode 0: 1900-based, 1: 1904-based.
# <br>WARNING: when using this function to
# interpret the contents of a workbook, you should pass in the Book.datemode
# attribute of that workbook. Whether
# the workbook has ever been anywhere near a Macintosh is irrelevant.
# @return a datetime.datetime object, to the nearest_second.
# <br>Special case: if 0.0 <= xldate < 1.0, it is assumed to represent a time;
# a datetime.time object will be returned.
# <br>Note: 1904-01-01 is not regarded as a valid date in the datemode 1 system; its "serial number"
# is zero.
# @throws XLDateNegative xldate < 0.00
# @throws XLDateAmbiguous The 1900 leap-year problem (datemode == 0 and 1.0 <= xldate < 61.0)
# @throws XLDateTooLarge Gregorian year 10000 or later
# @throws XLDateBadDatemode datemode arg is neither 0 nor 1
# @throws XLDateError Covers the 4 specific errors

_XLDAYS_TOO_LARGE = 100000

def xldate_as_datetime(xldate, datemode=0):
    if datemode not in (0, 1):
        raise XLDateBadDatemode(datemode)
    if xldate == 0.00:
        return dt.datetime.time(0, 0, 0)
    if xldate < 0.00:
        raise XLDateNegative(xldate)
    xldays = int(xldate)
    frac = xldate - xldays
    seconds = int(round(frac * 86400.0))
    assert 0 <= seconds <= 86400
    if seconds == 86400:
        seconds = 0
        xldays += 1
    if xldays >= _XLDAYS_TOO_LARGE:
        raise XLDateTooLarge(xldate)

    if xldays == 0:
        # second = seconds % 60; minutes = seconds // 60
        minutes, second = divmod(seconds, 60)
        # minute = minutes % 60; hour    = minutes // 60
        hour, minute = divmod(minutes, 60)
        return dt.datetime.time(hour, minute, second)

    if xldays < 61 and datemode == 0:
        raise XLDateAmbiguous(xldate)

    return (
        dt.datetime.fromordinal(xldays + 693594 + 1462 * datemode)
        + dt.timedelta(seconds=seconds)
        )

def datetime_as_xldate(pydatetime):
    temp = dt.datetime(1899, 12, 31)
    delta = pydatetime - temp
    return float(delta.days) + (float(delta.seconds) / 86400)

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class XLDateBadDatemode(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr):
        self.expr = expr
        self.msg = "Datemode should be 0 or 1 for 1900 or 1904 mode."
        print self.msg
    
class XLDateNegative(Error):
    """Raised when a negative Excel date was passed."""
    def __init__(self, expr):
        self.expr = expr
        self.msg = "A negative Excel date was passed."
        print self.msg

class XLDateTooLarge(Error):
    """Raised when an extremely large Excel date was passed."""
    pass

class XLDateAmbiguous(Error):
    """Raised when an operation attempts a state transition that's not
    allowed."""
    pass

if __name__ == "__main__" :
    myxldate = xldate_as_datetime(40534)
    print myxldate
    #myxldate = xldate_as_datetime(40534,2)
    #myxldate = xldate_as_datetime(-40534)
    #print myxldate
    a = dt.datetime.now()
    print a
    b = datetime_as_xldate(a)
    print b
