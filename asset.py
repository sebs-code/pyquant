# -*- coding: utf-8 -*-
from cashflow import *
import uuid
from globals import *
import myLogger

# create logger
module_logger = myLogger.TLogger(__name__)

class Asset(object):
    """ The asset class is  the superclass from which any financial asset is derived
        such as equity, bonds, etc.
        It provides a common interface such as a 
        present value, descriptor and identifier for the object.__class__
        
        >>> ast = Asset()
        >>> ast.pv
        >>> ast.price
        >>> ast.description   
        'No description given'
        """
        
    def __init__(self, pv = None, description="No description given", price= None):
        self.logger = myLogger.TLogger(__name__)
        self.pv = pv
        self.price = price
        self.description = description
        self.id = uuid.uuid1()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
