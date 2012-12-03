import sys
import logging
import colorstreamhandler

class TLogger(logging.Logger):
	"""Create a loggger subclass which gets  
	   a logger with the name of the module that calls it.
	   
	   >>> mylog = TLogger("myLogger module testlogger")
	   >>> mylog.info("I am a logger info.") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
	   >>> mylog.warn("I am a logger warning.") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
	   >>> mylog.error("I am a logger error.") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
	   >>> mylog.critical("I am a logger critical error.") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
	"""
	
	def __init__(self, moduleName, logLevel = logging.DEBUG, logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' ):
		# create logger
		super(TLogger, self).__init__(moduleName)
		self.setLevel(logLevel)

		# create console handler and set level to debug
		ch = colorstreamhandler.ColorizingStreamHandler()
		#ch = logging.StreamHandler(sys.stdout) #see http://www.daniweb.com/software-development/python/threads/142823/doctest-logging
		ch.setLevel(logLevel)

		# create formatter
		formatter = logging.Formatter(logFormat)

		# add formatter to ch
		ch.setFormatter(formatter)

		# add ch to logger
		self.addHandler(ch) 
		

if __name__ == "__main__":
    import doctest
    doctest.testmod()
