'''
@author Jozef LANG
@contact
@summary Homework1 for Computational Investment I. 2014
'''

# Python imports
import sys
import math

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class Optimizer:

   # Square root of the number of trading days in a year
   SHARPE_CONSTANT = math.sqrt(252)

   def __init__(self, dt_start, dt_end, lst_symbols):
      self.dt_start = dt_start
      self.dt_end = dt_end
      self.lst_symbols = lst_symbols

      # Init shared data, quotes are stored as numpy array
      a_quotes = self.read_data_from_yahoo()

      # Normalize quotes to the first day
      self.a_normalizedQuotes = a_quotes / a_quotes[0][:]

   def read_data_from_yahoo(self):
      dt_timeofday = dt.timedelta(hours=16)
      lstdt_timestamps = du.getNYSEdays(self.dt_start, self.dt_end, dt_timeofday)
      c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
      lst_keys = ['close'] # Adjusted close

      # Get data
      lstdf_data = c_dataobj.get_data(lstdt_timestamps, lst_symbols, lst_keys)
      d_data = dict(zip(lst_keys, lstdf_data))

      # Return data as NumPy array
      return d_data['close'].values

   def simulate(self, lst_weights):
      lst_dailyPortfolioPerformance = (self.a_normalizedQuotes * lst_weights).sum(axis=1)
      lst_dailyPortfolioReturns = np.diff(lst_dailyPortfolioPerformance)

      stdOfReturn = np.std(lst_dailyPortfolioReturns)
      meanReturn = np.mean(lst_dailyPortfolioReturns)
      cumsum = np.cumsum(lst_dailyPortfolioReturns)[-1] + 1
      sharpeRatio = (meanReturn / stdOfReturn) * self.SHARPE_CONSTANT
   
      return sharpeRatio

   def optimize(self):
      maxSharpe = 0
      maxAllocs = [0,0,0,0]
      for p1 in range(-100, 100, 10):
         for p2 in range(-100, 100, 10):
            for p3 in range(-100, 100, 10):
               for p4 in range(-100, 100, 10):
                  if abs(p1) + abs(p2) + abs(p3) + abs(p4) != 100:
                     continue
                  allocs = [p1/100.0, p2/100.0, p3/100.0, p4/100.0]
                  sharpe = self.simulate(allocs)
                  if sharpe > maxSharpe:
                     maxSharpe = sharpe
                     maxAllocs = allocs

      return maxSharpe, maxAllocs

if __name__ == '__main__':
   if len(sys.argv) < 11:
      print ('python optimizer.py startyear startmonth startday endyear endmonth endday symbol1 symbol2 symbol3 symbol4')
   else:
      lst_dateArgs = sys.argv[1:7]
      lst_symbols = sys.argv[7:]
      i_startYear, i_startMonth, i_startDay, i_endYear, i_endMonth, i_endDay = map(int, lst_dateArgs)
      optimizer = Optimizer(dt.datetime(i_startYear, i_startMonth, i_startDay), dt.datetime(i_endYear, i_endMonth, i_endDay), lst_symbols)
      sharpe, allocs = optimizer.optimize()
      print "Sharpe:", sharpe, "allocs:", allocs
   
