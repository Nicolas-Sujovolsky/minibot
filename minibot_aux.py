"""
Auxiliary classes for minibot.py
Author: Nicolas Sujovolsky
"""
import pyRofex
import numpy as np
from datetime import datetime

class Instrument():
    '''
    Instrument class
    '''  
    #Dictonary of instruments created
    inst_list = dict()    
      
    #Read transaction cost from a file
    transaction_cost = 10 
    
    #Entries we want to subscribe to
    entries = [pyRofex.MarketDataEntry.BIDS,
              pyRofex.MarketDataEntry.OFFERS,
              ]
    
    def __init__(self,symbol,ratio,name):
        self.symbol                 = symbol
        self.ratio                  = ratio
        self.name                   = name #company name
        self.future_market_data     = {'OF':None,'BI':None}
        self.stock_market_data      = {'OF':None,'BI':None}
        self.inst_list[self.symbol] = self
        try:
            self.maturity           = self.maturity()
        except:
            self.maturity           = None
    
    @property
    def future_market_data(self):
        return self._future_market_data
    
    @future_market_data.setter
    def future_market_data(self,value):
        try:
            value['OF'] = value['OF']
        except:
            value['OF'] = None
        try:
            value['BI'] = value['BI']
        except:
            value['BI'] = None
        self._future_market_data = value
    
    @property
    def stock_market_data(self):
        return self._stock_market_data
    
    @stock_market_data.setter
    def stock_market_data(self,info):
        value = {} 
        try:
            value['OF'] = info['ask'] 
        except:
            value['OF'] = None
        try:
            value['BI'] = info['bid'] 
        except:
            value['BI'] = None
        self._stock_market_data = value
        
    
    @property
    def maturity(self):
        return self._maturity
    
    @maturity.setter
    def maturity(self,value):
        try:
            self._maturity = value
        except:
            self._maturity = None
            
    @classmethod
    def get_all_symbols(cls):
        return [inst for inst in cls.inst_list.keys()]
        
    @classmethod
    def update_market_data(cls,msg):
        '''
        Updates the futures market data
        Parameters
        ----------
        msg : dict
            Contains the new market data
        Returns
        -------
        None.
        '''
        #print(msg)        
        symbol    = msg['instrumentId']['symbol']
        old_data  = cls.inst_list[symbol].future_market_data
        value = {'BI': msg['marketdata']['BI'][0]['price'],
                 'OF': msg['marketdata']['OF'][0]['price'],}
        cls.inst_list[symbol].future_market_data  = value
        # If market_data has changed
        if old_data != value:
            print('The short implied rate for {} is:{}'.format(symbol,cls.inst_list[symbol].implied_rate_short() ) )
            print('The long implied rate for {} is:{}'.format(symbol,cls.inst_list[symbol].implied_rate_long()  )  )
            arbitrage_check,arbitrage_data = cls.arbitrage_check()
            if arbitrage_check:
                long,short,size_short_sto,size_long_sto,size_short_fut,size_long_fut = arbitrage_data
                cls.arbitrage_excercise(long,short,size_short_sto,size_long_sto,size_short_fut,size_long_fut)
    
    def maturity(self):
        """Computes the days to maturity using pyRofex library"""
        maturity = pyRofex.get_instrument_details(ticker = self.symbol)['instrument']['maturityDate']
        year,month,day = int(maturity[:4]), int(maturity[4:6]), int(maturity[6:])
        maturity = datetime(year,month,day)
        time2maturity = (maturity - datetime.today()).days
        return time2maturity
       
    #Tasa tomadora
    def implied_rate_short(self):
        """ Returns the implied rate by shorting the stock and buying the future"""
        spot   = self.stock_market_data['BI']
        future = self.future_market_data['OF'] * self.ratio
        time   = self.maturity / 365  #actual/365 in years 
        try:
            return np.power(future/spot, 1./time) - 1
        except:
            return None        
    
    # Tasa colocadora 
    def implied_rate_long(self):
        """ Returns the implied rate by buying the stock and selling the future"""
        spot   = self.stock_market_data['OF']
        future = self.future_market_data['BI'] * self.ratio
        time   = self.maturity / 365  #actual/365 in years
        try:
            return np.power(future/spot, 1./time) - 1
        except:
            return None
    
    @classmethod
    def rates_comparison(cls):
        """returns the instruments with the higher long to short implied rates difference"""
        diff_old, diff_new = 0, 0
        long, short = None, None
        symbols = cls.get_all_symbols()
        for ins1 in symbols:
            for ins2 in symbols:
                try:
                    diff_new = cls.inst_list[ins1].implied_rate_long() - cls.inst_list[ins2].implied_rate_short()
                except:
                    diff_new = 0
                    
                if diff_new > diff_old and diff_new > 0:
                    diff_old = diff_new
                    long  = ins1
                    short = ins2
                    
        return long, short
                
                                 
    def send_order(self, action, size):
        '''
        Sends a buy or sell order to REMARKET
        
        Parameters
        ----------
        action : string
            'buy' or 'sell' instruction
        size : int
            Amount of instrument
        price : float
            Buy or Sell price
        
        Returns
        -------
        pyRofex.send_order status returned
        '''
        if action == 'buy':
            action = pyRofex.Side.BUY
            price  = self.future_market_data['OF'] 
        if action == 'sell':
            action = pyRofex.Side.SELL
            price = self.future_market_data['BI']

        status = pyRofex.send_order(ticker     = self.symbol, 
                                    size       = size,
                                    order_type = pyRofex.OrderType.LIMIT,
                                    side       = action,
                                    price      = price)
        return status
    
    @classmethod
    def arbitrage_check(cls):
        '''
    Checks if arbitrage is possible and excercise it if it is.
    
    Returns
    -------
    None.

    '''
        # Get the instrument with the best rate difference
        long, short = cls.rates_comparison()

        try:
            long, short = cls.inst_list[long], cls.inst_list[short]
        except:
            print('Arbitrage not possible')
            
        # Compute the amount of instruments to deal with
        # trying to aproximate the money in the short and the long position
        price_long  = long.future_market_data['BI'] * long.ratio
        price_short = short.future_market_data['OF'] * short.ratio
        
        if price_long > price_short:
            size_long_fut   = 1 * long.ratio
            size_short_fut  = max(round(price_long/price_short),1) * short.ratio 
        else:
            size_long_fut   = max(round(price_short/price_long),1) * long.ratio
            size_short_fut  = 1 * short.ratio
        
        size_long_sto   = round(size_long_fut / long.ratio)
        size_short_sto  = round(size_short_fut / short.ratio)
        
        #Net Result taking into account the transaction costs
        result   = size_short_sto * short.stock_market_data['BI'] 
        result  -= size_long_sto  * long.stock_market_data['OF']
        result  -= cls.transaction_cost
        print('At present time, the gain is ${}'.format(result))
        
        result -= size_short_fut * short.future_market_data['OF']
        result += size_long_fut  * long.future_market_data['BI']
        result -= cls.transaction_cost
        print('In {} days the gain is ${}'.format(long.maturity, result) )
        
        if result > 0:
            print('The net result is possitive, will implement arbitrage strategy')
            return True, (long,short,size_short_sto,size_long_sto,size_short_fut,size_long_fut)
        else:
            print('The result is negative, will not implement the arbitrage strategy')
            return False, ()
    
    @staticmethod
    def arbitrage_excercise(long,short,size_short_sto,size_long_sto,size_short_fut,size_long_fut):
        #Tasa tomadorac(short)
        print('Sell {} {} at price {}'.format(size_short_sto,short.symbol,short.stock_market_data['BI'] ))
        short.send_order('buy', size_short_fut)
    
        #Tasa colocadora (long)
        print('Buy {} {} at price {}'.format(size_long_sto,long.symbol,long.stock_market_data['OF'] ))
        long.send_order('sell',size_long_fut)
    
