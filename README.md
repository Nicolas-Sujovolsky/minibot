# minibot

# minibot is a python script that searches for implied rates arbitrage at the argentinian spot and futures market.
It works by loading the market data for future contracts from Rofex by means of the pyRofex library, as well as the stocks spot data from the yfinance library.
When an arbitrage opportunity presents itself, the minibot print the trade information in the screen. 

In each arbitrage opportunity, two stocks will be involved. Currently, the arbitrage strategy is configured to only buy/sell 1 stock of the most expensive one and as many stocks of the cheapest kind to spend a similar amount of money. 
