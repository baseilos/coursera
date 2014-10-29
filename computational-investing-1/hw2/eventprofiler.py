'''
@author Jozef LANG
@contact
@summary Homework2 for Computational Investment I. 2014
'''

# Python imports
import sys
import copy

# QSTK imports
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import QSTK.qstkutil.qsdateutil as du

# 3rd-party imports
import pandas as pd
import numpy as np
import datetime as dt

class EventProfiler:
   
   def __init__(self, dt_start, dt_end, s_sapfile):
      self.dt_start = dt_start
      self.dt_end = dt_end
      self.d_data, self.lst_symbols = self.read_data_from_yahoo(s_sapfile)

   def read_data_from_yahoo(self, s_sapfile):
      lstdt_timestamps = du.getNYSEdays(self.dt_start, self.dt_end, dt.timedelta(hours=16))
      c_dataobj = da.DataAccess('Yahoo')#, cachestalltime=0)

      # Read symbols from file provided and add SPY symbol to include Market price
      lst_symbols = c_dataobj.get_symbols_from_list(s_sapfile)
      lst_symbols.append('SPY') 

      # Get data
      print 'Getting data ...'
      lst_keys = ['close', 'actual_close']
      lstdf_data = c_dataobj.get_data(lstdt_timestamps, lst_symbols, lst_keys)
      d_data = dict(zip(lst_keys, lstdf_data))
      print 'Data received!'

      # Clear data
      for s_key in lst_keys:
         d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
         d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
         d_data[s_key] = d_data[s_key].fillna(1.0)

      # Return data
      return d_data, lst_symbols

   def get_events(self, d_data, lst_symbols, lmbd_isEvent):
      df_data = d_data['actual_close']
      ts_market = df_data['SPY']
      
      # Copy data
      df_events = copy.deepcopy(df_data)
      df_events = df_events * np.NAN

      print 'Getting events ...'
      ldt_timestamps = df_data.index

      for s_symbol in lst_symbols:
         for i in range(1, len(ldt_timestamps)):
            f_priceToday = df_data[s_symbol].ix[ldt_timestamps[i]]
            f_priceYesterday = df_data[s_symbol].ix[ldt_timestamps[i-1]]

            # Call lambda named isEvent where the first parameter is yesterday's price and the second is today's price
            if lmbd_isEvent(f_priceYesterday, f_priceToday):
               df_events[s_symbol].ix[ldt_timestamps[i]] = 1
      
      print 'Events got!'
      return df_events

   def profile(self, lmbd_isEvent, s_reportName):
      df_events = self.get_events(self.d_data, self.lst_symbols, lmbd_isEvent)

      print 'Generating report to ', s_reportName

      ep.eventprofiler(df_events, self.d_data, i_lookback=20, i_lookforward=20,
                s_filename=s_reportName, b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

def get_function(i_type):
   if i_type == 1:
      'lambda yesterday, today: yesterday >= 5 and today < 5'
      return lambda yesterday, today: yesterday >= 5 and today < 5
   if i_type == 2:
      'lambda yesterday, today: yesterday >= 10 and today < 10'
      return lambda yesterday, today: yesterday >= 10 and today < 10
   if i_type == 3:
      'lambda yesterday, today: yesterday >= 9 and today < 9'
      return lambda yesterday, today: yesterday >= 9 and today < 9

if __name__ == '__main__':
   if len(sys.argv) < 9:
      print ('python eventprofiler.py startyear startmonth startday endyear endmonth endday eventtype data')
   else:
      lst_dateArgs, s_eventtype, s_data = sys.argv[1:7], sys.argv[7], sys.argv[8]
      i_startYear, i_startMonth, i_startDay, i_endYear, i_endMonth, i_endDay = map(int, lst_dateArgs)
      dt_startYear = dt.datetime(i_startYear, i_startMonth, i_startDay)
      dt_endYear = dt.datetime(i_endYear, i_endMonth, i_endDay)
      eventProfiler = EventProfiler(dt_startYear, dt_endYear, s_data)
      s_filename = '%s_%s.pdf' % (s_data, s_eventtype)
      eventProfiler.profile(get_function(int(s_eventtype)), s_filename)
