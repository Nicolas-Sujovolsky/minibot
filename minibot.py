"""
Created on Sat Jan 1 2022
Author: Nicolas Sujovolsky
"""
# Proyecto AlmaFintech
# Mini trading bot that arbitrages the 
# USD/ARS market with futures on CEDEARs

import pyRofex
import yfinance as yf
from minibot_aux import Instrument

#initialize the RENARKET enviorment with my credentials
myUser     = "nicolassujovolsky6642"
myPassword = "vxqcdQ7#"
myAccount  = "REM6642"
pyRofex.initialize(user=myUser,
                   password=myPassword,
                   account=myAccount,
                   environment=pyRofex.Environment.REMARKET)


############ Make the list of Stocks/Futures to arbitrage ############
stocks_pyRofex  = ('GGAL','YPFD','PAMP')
rofex2yahoo     = {'GGAL':'GGAL','YPFD': 'YPF','PAMP':'PAM'}
ratios = {'GGAL':10,'YPFD':1,'PAMP':25} #conversion ratios CEDEARS to NASDAQ 

############ Create the instrument objects ############
instList = pyRofex.get_all_instruments()
futures = {}
for instruments in instList['instruments']:
    for stock in stocks_pyRofex:
        if stock+'/' in instruments['instrumentId']['symbol']:
            Instrument(instruments['instrumentId']['symbol'],ratios[stock],stock)

############ Get stock's spot data with yfinance ############
symbols = Instrument.get_all_symbols()
for symbol in symbols:
    name_y = rofex2yahoo[symbol[:4]]
    info = yf.Ticker(name_y).info
    Instrument.inst_list[symbol].stock_market_data = info

#Dolar instrument
Instrument('DLR/ABR22',1,'DOLR')
Instrument.inst_list['DLR/ABR22'].stock_market_data = {'ask': 1, 'bid':1}

############ Get stock's future data with pyRofex ############
# Subscrition to market data and set trading strategy to work
pyRofex.add_websocket_market_data_handler(Instrument.update_market_data)
pyRofex.market_data_subscription(tickers=symbols, entries=Instrument.entries)