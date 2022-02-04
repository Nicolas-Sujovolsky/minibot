Welcome to minibot's Documentation
===================================

Overview
--------

*minibot.py* is a python script that searches for implied rates arbitrage at the argentinian spot and futures market.
It works by loading the market data for future contracts from Rofex by means of the pyRofex library, as well as the stocks spot data from the yfinance library.
When an arbitrage opportunity presents itself, the minibot print the trade information in the screen. 

Warnings
-------------
In each arbitrage opportunity, two stocks will be involved. Currently, the arbitrage strategy is configured to only buy/sell 1 stock of the most expensive one and as many stocks of the cheapest kind to spend a similar amount of money. 

*minobot.py* simulates trades of futures in Rofex with the pyRofex library and prints the relevant information of the spot trades. It is currently looking for trading strategies with GGAL, YPFD and PAMP and with DLR. The main script requires monthly updates on the dollar instrument.  

How to use it
-------------
Download all files, group them together and run the main script *minibot.py*
