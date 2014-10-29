#!/bin/sh

echo "python eventprofiler.py 2008 1 1 2009 12 31 5 sp5002012 && python marketsim.py 50000 orders.csv results.csv && python analyze.py results.csv \$SPX"
python eventprofiler.py 2008 1 1 2009 12 31 5 sp5002012 && python marketsim.py 50000 orders.csv results.csv && python analyze.py results.csv     \$SPX
