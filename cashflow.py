# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from scipy.optimize import bisect
import myLogger
from globalsconstants import *

# create logger
module_logger = myLogger.TLogger(__name__)

#TODO
#PV is inconsitent with cashflows starting at 0 and starting at 1
#very bad quick fix in duration function adds back t0 cashflow to PV
#new pandas series changes in time handling need to be reviewed

class Cashflow(object):
    """Represents a stream of future payments.
        cf_amounts  are the payment amounts and cf_times are the 
        time or period when the future payment occurs.
        Times can be dates in various formats, or periods.
        times_type sepcifies the type of date, e.g. Excel for dates in Excel
        format.
        
        >>> print "Precision is: " + str(PRECISION)
        Precision is: 8
        >>> cf_times = [1,2,3]
        >>> cf_amounts = [-100.0, 10.0, 110.0]
        >>> cf = Cashflow(cf_times, cf_amounts, time_type = "Annual")
        >>> print "{0:g}".format(cf.getIRR())
        0.1
        >>> print "{0:g}".format(cf.getMcAuleyDuration())
        1.90909
        >>> cf.getCouponPaymentSchedule()
        array([  0, 365, 730])
        >>> r = 0.05
        >>> cf.getDiscountFactors(r)
        array([ 1.        ,  0.95238095,  0.90702948])
        >>> cf.getDiscountedCashflows(r)
        array([-100.        ,    9.52380952,   99.77324263])
        >>> print "{0:g}".format(cf.getPV(r))
        9.29705
        >>> print "{0:g}".format(cf.getDuration(r))
        1.91286
    """    
    def __init__(self, cf_times, cf_amounts, time_type = "Excel"):
        self.logger = myLogger.TLogger(__name__)
        self.logger.warning("Generating cashflow")
        self.cf = pd.Series( data=cf_amounts, index = cf_times)
        self.logger.info(self.cf)
        self.time_type = time_type
        self.cf_times = cf_times
        self.cf_amounts = cf_amounts
        self.daily_payment_schedule = self.getCouponPaymentSchedule()
        self._IRR = None
        self._mcAuleyDuration = None
        
    def getCouponPaymentSchedule(self):
        """ Returns the days from the startdate of the cashflow"""
        if self.time_type == "Excel":
            days_from_startdate = np.array([(i - self.cf.idxmin()) for i in self.cf.index])   
        elif self.time_type == "Dates":
            days_from_startdate = np.array([(i - self.cf.idxmin()).days -1 for i in self.cf.index])     #-1 because interest does not accumulate on startdate
        elif self.time_type == "Annual":
            days_from_startdate = np.array([(i - self.cf.idxmin()) * 365 for i in self.cf.index])     
        days_from_startdate[0] = 0 #startdate is 0
        self.logger.debug("Coupon days from startdate: {}".format(days_from_startdate))
        return days_from_startdate
        
    def getPV(self, r):
        """Returns the present value (PV) for a cashflow given an interest rate (r)"""
        pv =sum(self.getDiscountedCashflows(r))
        self.logger.warn("Present value for r = " + str(r) + ": " + str(pv))
        return pv
    
    def getDiscountFactors(self, r):
        """Returns a list of discount factors for a cashflow given an interest rate (r)"""
        daily_r = (1+r)**(1.0/365.0) -1
        discountfactors = (1.0 + daily_r) ** - self.daily_payment_schedule
        #self.discountfactors = (1.0 + daily_r)        
        self.logger.debug("Discount factors for r = " + str(r) + ": " +     str(discountfactors))
        return discountfactors
        
    def getDiscountedCashflows(self, r):
        """Returns a list of discounted cashflows for a cashflow given an interest rate (r)"""
        discountedcashflows = self.getDiscountFactors(r) * self.cf.values
        self.logger.debug("Discounted cashflows for r = " + str(r) + ": " + str(discountedcashflows))
        return discountedcashflows
        
    def getIRR(self): 
        """Returns the internal rate of return (IRR) for a cashflow given an interest rate (r)"""
        if self.IRR == None: #IRR  already  calculated?
            lowerbound = 0.0
            upperbound = 0.5
            while self.getPV(upperbound) > 0.0:
                upperbound = upperbound*2
            IRR =  bisect(self.getPV,lowerbound, upperbound, xtol=1.0e-8, maxiter = 100)
            self._IRR = _IRR
        else:
            pass
        self.logger.debug("Internal rate of return is: " + str(self._IRR))
        return self._IRR
        
    def getDuration(self,r): 
        """Returns the duration in days for a cashflow given an interest rate (r)"""
        D = sum((self.daily_payment_schedule/365)  * self.getDiscountedCashflows(r))
        B = self.getPV(r) - self.cf_amounts[0]
        duration  = D/B
        self.logger.debug("Duration is for r = " + str(r) + ": " + str(duration))
        return duration
        
    def getMcAuleyDuration(self): 
        """Returns the McAuley-duration in days for a cashflow given an interest rate (r).
           McAuleyDuration uses the internal rate of return (IRR) as interest rate to calculate duration."""
        if self._mcAuleyDuration == None:
            IRR = self.getIRR()
            mcAuleyDuration = self.getDuration(IRR)
            self._mcAuleyDuration = mcAuleyDuration
        else:
            pass_
        self.logger.debug("McAuley duration is: " + str(self._mcAuleyDuration))
        return self._mcAuleyDuration
        
    def getModifiedDuration(self):
        """Returns Modified Duration in terms of internal rate of interest (yield to maturity).
           It measures the precentage change of the PV with regards to a change in the interest rate.""" 
        D = getMcAuleyDuration()
        ModifiedDuration = D/(1+IRR)
        self.logger.debug("Modified duration is: " + str(ModifiedDuration))
        return D/(1+IRR)
        
    def getConvexity(self, r):
        """ Measures the curvature in the relationship between PV and interest rate."""
        Cx =  sum((self.daily_payment_schedule/365)  * ((self.daily_payment_schedule/365) + 1) * self.getDiscountedCashflows(r))
        B = self.getPV(r) - self.cf_amounts[0]
        Convexity = (CX/((1+r)**2))/B
        self.logger.debug("Convexity is: " + str(Convexity)
        return Convexity
        
    def __repr__(self):
        return "Cashflow(cf_times={}, cf_amounts={}, time_type={})".format(self.cf_times, self.cf_amounts, self.time_type)
    
    def __str__(self):
        return str(self.cf)
        
 
class Perpetuity(object):
    """A perpetuity is a promise of a payment of a fixed amount X each
       period for the indefinite future for a fixed interest rate r.
       If growth > 0 this is a growing perpetuity, where the payment the
       first year is X and each consequent payment grows by a constant
       rate g, i.e, the time 2 payment is X(1 + g), the time 3 payment is
       X(1 + g)2 , and so on.    
    """
    def __init__(self, cf_amount, r, growth=0.0):
        self.logger = myLogger.TLogger(__name__)
        self.cf_amount = cf_amount
        self.r = r
        self.pv = cf_amount / (r - growth)
       
class Annuity(object):
    """An annuity is a sequence of cashflows for a given number of years,
       say T periods into the future. Consider an annuity paying a fixed 
       amount X each period. The interest rate is r.
       If growth > 0 this is a growing annuity, where the payment the
       first year is X and each consequent payment grows by a constant
       rate g
    """
    def __init__(self, cf_amount, r, no_periods, growth=0.0):
        self.logger = myLogger.TLogger(__name__)
        self.cf_amount = cf_amount
        self.r = r
        self.pv = cf_amount * (1.0/ (r - growth) -  (1.0/(r-growth)*((1.0+growth)/(1.0+r))**no_periods))

if __name__ == "__main__" :
    import doctest
    doctest.testmod()
    #cf_times = [1,2,3, 4]
    #cf_amounts = [-200, 100, 100, 100]
    #cf = Cashflow(cf_times, cf_amounts)
    #print (1.1) **  cf.cf.index
    #print cf.discountfactors(0.1)
    #cf.getPV(0.1)
    #cf.getIRR()
    #print cf.pv, cf.discountedcashflows, cf.discountedcashflows, cf.IRR
    #perpetuity
    #per = Perpetuity(100, 0.05)
    #print per.pv
    #growing perpetuity
    #perg = Perpetuity(75, 0.05, 0.02)
    #print perg.pv
    #annuity
    #ann = Annuity(90, 0.05, 10)
    #print ann.pv
    #growing annuity
    #anng = Annuity(85, 0.05, 10, 0.02)
    #print anng.pv
