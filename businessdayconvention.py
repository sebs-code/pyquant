#BusinessDayConvention

class BusinessdayConvention:
    """"These conventions specify the algorithm used to adjust a date in case
    it is not a valid business day."""
    
    def __init__:
        self.Following = "Choose the first business day after the given holiday."
        self.ModifiedFollowing = "Choose the first business day after the given holiday unless it belongs to a different month, in which case choose the first business day before the holiday."
        self.Preceding = "Choose the first business day before the given holiday."
        self.ModifiedPreceding = "Choose the first business day before the given holiday unless it belongs to a different month, in which case choose the first business day after the holiday."
        self.Unadjusted  = "Do not adjust."
