'''
@author Jozef LANG
@contact
@summary Homework3 for Computational Investment I. 2014
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
import csv as csv
from sets import Set

class MarketSimulator:

   def read_orders(self, file_orders):
      lst_orders = []
      with open(file_orders, 'r') as ordersFile:
         ordersReader = csv.reader(ordersFile, delimiter=',')
         for order in ordersReader:
            lst_orders.append((dt.datetime(int(order[0]), int(order[1]), int(order[2])), order[3], order[4], int(order[5])))
      return lst_orders

   def get_min_max_date(self, lst_orders):
      min_date = lst_orders[0][0]
      max_date = lst_orders[0][0]
      for order in lst_orders[1:]:
         if order[0] < min_date:
            min_date = order[0]
         if max_date < order[0]:
            max_date = order[0]
      return min_date, max_date

   def get_symbol_list(self, lst_orders):
      lstSet_symbols = Set([])
      for date, symbol, op, amt in lst_orders:
         lstSet_symbols.add(symbol)
      return list(lstSet_symbols)

   def read_market_prices(self, lst_symbols, dt_start, dt_end):
      dt_timeofday = dt.timedelta(hours=16)
      lstdt_timestamps = du.getNYSEdays(dt_start, dt_end + dt.timedelta(days=1), dt_timeofday)
      c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
      lst_keys = ['close'] # Adjusted close

      # Get data
      lstdf_data = c_dataobj.get_data(lstdt_timestamps, lst_symbols, lst_keys)
      d_data = dict(zip(lst_keys, lstdf_data))

      # Return data as NumPy array
      return lstdt_timestamps, d_data['close'].values

   def orders_to_map_keyed_by_date(self, lst_orders):
      map_orders = {}
      for order in lst_orders:
         if order[0] not in map_orders:
            map_orders[order[0]] = []
         map_orders[order[0]].append(tuple(order[1:]))
      return map_orders

   def get_price(self, arr_prices, lst_symbols, symbol, lstdt_nysedays, dt_nyseday):
      return arr_prices[lstdt_nysedays.index(dt_nyseday)][lst_symbols.index(symbol)]
      

   def get_daily_portfolio_value(self, i_cash, lst_symbols, map_orders, lstdt_nysedays, arr_prices):
      map_bought_eqt = {}
      i_porfolio_cash = i_cash
     
      map_portfolio_values = {}
      i_dayNum = 0
      for dt_nyseday in lstdt_nysedays:
         dt_truncadedNYSEDay = dt.datetime(dt_nyseday.year, dt_nyseday.month, dt_nyseday.day)
         if dt_truncadedNYSEDay in map_orders:
            for symbol, op, amt in map_orders[dt_truncadedNYSEDay]:
               d_price = self.get_price(arr_prices, lst_symbols, symbol, lstdt_nysedays, dt_nyseday)
               if symbol not in map_bought_eqt:
                  map_bought_eqt[symbol] = 0
               if op == 'Buy':
                  map_bought_eqt[symbol] += amt
                  i_porfolio_cash -= d_price*amt
               else:
                  map_bought_eqt[symbol] -= amt
                  i_porfolio_cash += d_price*amt 
               
         # Calculate portfolio value
         map_portfolio_values[dt_truncadedNYSEDay] = i_porfolio_cash
         for symbol in map_bought_eqt:
            d_price = self.get_price(arr_prices, lst_symbols, symbol, lstdt_nysedays, dt_nyseday)
            map_portfolio_values[dt_truncadedNYSEDay] += map_bought_eqt[symbol] * d_price
      return map_portfolio_values

   def write_results_to_file(self, file_results, map_portfolio_values):
      with open(file_results,'w') as resultsFile:
         resultWriter = csv.writer(resultsFile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
         for dt_day in sorted(map_portfolio_values.keys()):
            resultWriter.writerow([dt_day, map_portfolio_values[dt_day]])       
      

   def simulate(self, i_cash, file_orders, file_results):
      lst_orders = self.read_orders(file_orders)
      dt_start, dt_end = self.get_min_max_date(lst_orders)
      lst_symbols = self.get_symbol_list(lst_orders)
      lstdt_nysedays, arr_prices = self.read_market_prices(lst_symbols, dt_start, dt_end)
      map_dailyresults = self.get_daily_portfolio_value(i_cash, lst_symbols, self.orders_to_map_keyed_by_date(lst_orders), lstdt_nysedays, arr_prices)
      self.write_results_to_file(file_results, map_dailyresults)

if __name__ == '__main__':
   if len(sys.argv) < 4:
      print ('python marketsim.py cash orders results')
   else:
      i_cash, file_orders, file_results = int(sys.argv[1]), sys.argv[2], sys.argv[3]
      print 'Generating simulation file: {0}'.format(file_results)
      marketSimulator = MarketSimulator()
      marketSimulator.simulate(i_cash, file_orders, file_results)
