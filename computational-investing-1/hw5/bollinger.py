'''
@author Jozef LANG
@contact
@summary Homework5 for Computational Investment I. 2014
'''

# Python imports
import sys
import copy
import math

# QSTK imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import QSTK.qstkutil.qsdateutil as du

# 3rd-party imports
import pandas as pd
import numpy as np
import datetime as dt
import csv as csv
import matplotlib.pyplot as plt
from sets import Set

class Bollinger:
   
   def __init__(self, dt_startDate, dt_endDate, s_symbol, i_lookback):
      self.dt_startDate = dt_startDate
      self.dt_endDate = dt_endDate
      self.s_symbol = s_symbol
      self.i_lookback = i_lookback
      self.lstdt_timestamps, self.df_prices = self.read_values_from_yahoo(dt_startDate, dt_endDate, s_symbol)
      self.df_rollingMean, self.df_std, self.df_upperBand, self.df_lowerBand =  self.get_bollinger()

   def read_values_from_yahoo(self, dt_startDate, dt_endDate, s_symbol):
      dt_timeofday = dt.timedelta(hours=16)
      lstdt_timestamps = du.getNYSEdays(dt_startDate, dt_endDate, dt_timeofday)
      c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
      lst_keys = ['close'] # Adjusted close

      # Get data
      lstdf_data = c_dataobj.get_data(lstdt_timestamps, [s_symbol], lst_keys)
      d_data = dict(zip(lst_keys, lstdf_data))

      # Return data as NumPy array normalized to the first day
      return lstdt_timestamps, d_data['close'] / d_data['close'].values[0][:]

   def get_bollinger(self):
     df_stddev = pd.rolling_std(self.df_prices, self.i_lookback)
     df_rollingMean = pd.rolling_mean(self.df_prices, self.i_lookback)
     return df_rollingMean, df_stddev, df_rollingMean + df_stddev, df_rollingMean - df_stddev

   def to_list(self, dt_data):
      return [v[0] for v in dt_data.values.tolist()]      

   def plot_graph(self, s_filename):
      plt.clf()
      fig = plt.figure()
      fig.add_subplot(111)
      plt.plot(self.lstdt_timestamps, self.to_list(self.df_prices))
      plt.plot(self.lstdt_timestamps, self.to_list(self.df_upperBand)) 
      plt.plot(self.lstdt_timestamps, self.to_list(self.df_lowerBand))
      plt.ylabel('Adjucsted close')
      plt.xlabel('Date')
      fig.autofmt_xdate(rotation=45)
      plt.savefig(s_filename, format='pdf')      
      print 'Bollinger bands plotted to {0}'.format(s_filename)

   def bollinger_value(self, index): 
      return (self.df_prices.iloc[index] - self.df_rollingMean.iloc[index]) / self.df_std.iloc[index]

   def print_bollinger_values(self):
      for index in xrange(0, len(self.lstdt_timestamps)):
         print self.lstdt_timestamps[index], self.df_lowerBand.iloc[index].values, self.df_upperBand.iloc[index].values, self.bollinger_value(index).values

if __name__ == '__main__':
   if len(sys.argv) < 3:
      print ('python bollinger.py startDate endDate symbol lookback')
   else:
      s_datePattern = '%Y%m%d'
      dt_startDate, dt_endDate, s_symbol, i_lookback = dt.datetime.strptime(sys.argv[1], s_datePattern), dt.datetime.strptime(sys.argv[2], s_datePattern), sys.argv[3], int(sys.argv[4])
      obj_bollinger = Bollinger(dt_startDate, dt_endDate, s_symbol, i_lookback)
      obj_bollinger.plot_graph('bollinger.pdf')
      obj_bollinger.print_bollinger_values()
