'''
@author Jozef LANG
@contact
@summary Homework3 for Computational Investment I. 2014
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

class Analyzer:
   
   # Square root of the number of trading days in a year
   SHARPE_CONSTANT = math.sqrt(252)

   def __init__(self, s_comparisonSymbol):
      self.s_comparisonSymbol = s_comparisonSymbol

   def read_values_from_csv(self, file_values):
      lst_values = []
      with open(file_values, 'r') as values:
         valuesReader = csv.reader(values, delimiter=',')
         for s_date, f_value in valuesReader:
            lst_values.append((dt.datetime.strptime(s_date, '%Y-%m-%d %H:%M:%S'), float(f_value)))
      return sorted(lst_values)

   def read_values_from_yahoo(self, dt_startDate, dt_endDate, s_symbol):
      dt_timeofday = dt.timedelta(hours=16)
      lstdt_timestamps = du.getNYSEdays(dt_startDate, dt_endDate, dt_timeofday)
      c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
      lst_keys = ['close'] # Adjusted close

      # Get data
      lstdf_data = c_dataobj.get_data(lstdt_timestamps, [s_symbol], lst_keys)
      d_data = dict(zip(lst_keys, lstdf_data))

      # Return data as NumPy array normalized to the first day
      return d_data['close'].values / d_data['close'].values[0][:]

   def get_normalized_values(self, lst_dateValues):
      a_values = np.array([v[1] for v in lst_dateValues])
      return a_values / a_values[0]

   # Returns sharpe, cumulative return, stddev, average return and list of cumsum values
   def get_statistic_values(self, a_dailyValues):
      lst_dailyPortfolioPerformance = a_dailyValues
      lst_dailyPortfolioReturns = np.diff(lst_dailyPortfolioPerformance)

      stdOfReturn = np.std(lst_dailyPortfolioReturns)
      meanReturn = np.mean(lst_dailyPortfolioReturns)
      lst_cumsum = np.cumsum(lst_dailyPortfolioReturns)
      cumsum = lst_cumsum[-1] + 1
      sharpeRatio = (meanReturn / stdOfReturn) * self.SHARPE_CONSTANT

      return stdOfReturn, meanReturn, cumsum, sharpeRatio, lst_cumsum

   def plot_data(self, file_plot, lstdt_dates, lst_comparisonSymbolValues, lst_fundValues):
      print len(lstdt_dates), len(lst_comparisonSymbolValues), len(lst_fundValues)
      plt.clf()
      fig = plt.figure()
      fig.add_subplot(111)
      plt.plot(lstdt_dates, lst_comparisonSymbolValues)
      plt.plot(lstdt_dates, lst_fundValues)
      lst_names = [self.s_comparisonSymbol, 'Fund']
      plt.legend(lst_names)
      plt.ylabel('Cumulative Returns')
      plt.xlabel('Date')
      fig.autofmt_xdate(rotation=45)
      plt.savefig(file_plot, format='pdf')

   def analyze(self, file_values, file_plot):
      lst_values = self.read_values_from_csv(file_values)
      f_finalValueOfPortfolio = lst_values[-1][1]      

      # Assumes that lst_values is ordered asc by date
      dt_startDate, dt_endDate = lst_values[0][0], lst_values[-1][0]

      a_performanceSymbolDailyValues = self.read_values_from_yahoo(dt_startDate, dt_endDate, self.s_comparisonSymbol)
      f_perfSymbolStdRet, f_perfSymbolMeanRet, f_perfSymbolCumsum, f_perfSymbolSharpe, lst_perfSymbolCumsum = self.get_statistic_values(a_performanceSymbolDailyValues.sum(axis=1))
      f_fundStdRet, f_fundMeanRet, f_fundCumsum, f_fundSharpe, lst_fundCumsum = self.get_statistic_values(self.get_normalized_values(lst_values))

      # Print results 
      print 'The final value of the portfolio using {0} file is {1}'.format(file_values, f_finalValueOfPortfolio)
      print
      print 'Portfolio date range is {0} - {1}'.format(dt_startDate, dt_endDate)
      print
      print 'Sharpe Ratio of Fund: {0}'.format(f_fundSharpe)
      print 'Sharpe Ratio of {0}: {1}'.format(self.s_comparisonSymbol, f_perfSymbolSharpe)
      print
      print 'Total Return of Fund: {0}'.format(f_fundCumsum)
      print 'Total Return of {0}: {1}'.format(self.s_comparisonSymbol, f_perfSymbolCumsum)
      print
      print 'Standard Deviation of Fund: {0}'.format(f_fundStdRet)
      print 'Standard Deviation of {0}: {1}'.format(self.s_comparisonSymbol, f_perfSymbolStdRet)
      print 
      print 'Average Daily Return of Fund: {0}'.format(f_fundMeanRet)
      print 'Average Daily Return of {0}: {1}'.format(self.s_comparisonSymbol, f_perfSymbolMeanRet)
      print
      #print 'Going to plot daily values to {0}'.format(file_plot)
      #self.plot_data(file_plot, [d[0] for d in lst_values], lst_perfSymbolCumsum, lst_fundCumsum)

if __name__ == '__main__':
   if len(sys.argv) < 3:
      print ('python analyze.py values symbol')
   else:
      file_values, s_symbol = sys.argv[1], sys.argv[2]
      obj_analyzer = Analyzer(s_symbol)
      obj_analyzer.analyze(file_values, 'plot.pdf')
