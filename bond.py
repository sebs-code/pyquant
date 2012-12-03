# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd
from asset import Asset
import pandas.core.datetools as pdt
from cashflow import Cashflow
import myLogger


# create logger
module_logger = myLogger.TLogger(__name__)

class Bond(Asset):
    """
    This class generates a bond from some basic economic information
    and generates the corresponding cashflow.
    If no price is given the bond is assumed to be 100.
    Offset and coupon dates are a bit rudimentary and need to be improved.
    e.g. Daycount conventions, rolling, etc.
       
    Example:
    
    >>> startdate = dt.datetime(2012, 1, 1)
    >>> maturitydate = dt.datetime(2015, 1, 1)
    >>> bd = Bond(startdate = startdate, maturitydate = maturitydate, couponrate = 0.05, frequency_per_anno  = 2, businessdayconvention, calendar)
    >>> bd.price
    100.0
    >>> bd.couponrate
    0.05
    >>> bd.frequency
    2
    >>> bd.startdate
    datetime.datetime(2012, 1, 2, 0, 0)
    >>> bd.maturitydate
    datetime.datetime(2015, 1, 2, 0, 0)
    >>> bd
    """
    
    def __init__ (self, maturitydate, couponrate, frequency_per_anno, price = 100.0, startdate=dt.datetime.utcnow(), businessdayconvention, calendar, daycounter):
        self.logger = myLogger.TLogger(__name__)
        super(Bond, self).__init__()
        self.description = str(maturitydate.strftime("%d/%m/%y")) + "_" + str(couponrate)
        self.logger.info("Generating bond {}".format(self.description))
        self.price = price        
        self.startdate = startdate
        self.maturitydate = maturitydate
        self.couponrate = couponrate
        self.frequency = frequency_per_anno
        self.cf = self._generateCashflow()
        self.businessdayconvention = businessdayconvention
        self.calendar = calendar
        self.daycounter = daycounter
        
    def _generateCashflow(self):
        monthly_offset = 12 /  self.frequency       
        #offset = int(365.2425/self.frequency)
        dr = pd.DateRange(self.startdate, self.maturitydate, offset = pdt.DateOffset(months=monthly_offset))#bday *   offset)      
        cf = Cashflow(cf_times=dr, cf_amounts=self.couponrate * 100/self.frequency )
        cf.cf[0] = -self.price
        cf.cf[cf.cf.count()-1] +=  100.0   
        return cf
        
    def __repr__(self):
        return "Bond(startdate= {}, maturitydate= {}, couponrate= {}, frequency_per_anno  = {}, price = {} ".format(self.startdate, self.maturitydate, self.couponrate,       self.frequency, self.price) 
      
    def __str__(self):
        return """
            Bond descriptor:  {}
            id:               {}
            startdate:        {}
            maturitydate:     {}
            price:            {}
            coupon:           {}
            coupon frequency: {}
            cashflows:        {}
            """.format(
            self.description, self.id, self.startdate, self.maturitydate, self.price, self.couponrate, self.frequency, self.cf)
        
if __name__ == "__main__" :
    module_logger.info('Running Bond main')
    import doctest
    doctest.testmod(verbose=True) 

