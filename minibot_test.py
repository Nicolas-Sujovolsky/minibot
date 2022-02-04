"""
unittest for minibot_aux.py
Author: Nicolas Sujovolsky
"""
import unittest
from minibot_aux import Instrument

#Create instrument list 
Instrument('DLR/ABR22',1,'DOLR')
Instrument.inst_list['DLR/ABR22'].stock_market_data  = {'ask': 108, 'bid':107}
Instrument.inst_list['DLR/ABR22'].future_market_data = {'OF': 110, 'BI':109}
Instrument.inst_list['DLR/ABR22'].maturity = 30

Instrument('GGAL/ABR22',10,'GGAL')
Instrument.inst_list['GGAL/ABR22'].stock_market_data  = {'ask': 2200, 'bid':2188}
Instrument.inst_list['GGAL/ABR22'].future_market_data = {'OF':226 , 'BI':224}
Instrument.inst_list['GGAL/ABR22'].maturity = 30

Instrument('YPFD/ABR22',1,'YPFD')
Instrument.inst_list['YPFD/ABR22'].stock_market_data  = {'ask': 1030.0, 'bid':1025.0}
Instrument.inst_list['YPFD/ABR22'].future_market_data = {'OF':1050 , 'BI':1060 }
Instrument.inst_list['YPFD/ABR22'].maturity = 30

Instrument('PAMP/ABR22',25,'PAMP')
Instrument.inst_list['PAMP/ABR22'].stock_market_data  = {'ask':4272.7, 'bid':4257.3}
Instrument.inst_list['PAMP/ABR22'].future_market_data = {'OF':173 , 'BI': 170 }
Instrument.inst_list['PAMP/ABR22'].maturity = 30

Instrument.transaction_cost = 10 

class TestMinibotMethods(unittest.TestCase):
    
    def test_implied_rate_short(self):
        value = {'DLR/ABR22':0.399936620494,
                 'GGAL/ABR22':0.48278088265,
                 'YPFD/ABR22':0.34069331249,
                 'PAMP/ABR22':0.21161393763, }
        symbols = Instrument.get_all_symbols()
        for sym in symbols:
            inst = Instrument.inst_list[sym]
            self.assertAlmostEqual(inst.implied_rate_short(), value[sym])

    def test_implied_rate_long(self):
        value = {'DLR/ABR22' :0.118664955674,
                 'GGAL/ABR22':0.245111582355,
                 'YPFD/ABR22':0.418083466115,
                 'PAMP/ABR22':-0.06275577298, }
        symbols = Instrument.get_all_symbols()
        for sym in symbols:
            inst = Instrument.inst_list[sym]
            self.assertAlmostEqual(inst.implied_rate_long(), value[sym])
        
    def test_arbitrage_existance(self):
        arbitrage_check,arbitrage_data = Instrument.arbitrage_check()
        self.assertEqual(arbitrage_check, True)
        long,short,size_short_sto,size_long_sto,size_short_fut,size_long_fut = arbitrage_data
        self.assertEqual(long.symbol,  'YPFD/ABR22')
        self.assertEqual(short.symbol, 'PAMP/ABR22')
        #self.assertEqual(size_short_sto, 1)
        #self.assertEqual(size_long_sto, 4)
        #self.assertEqual(size_short_fut, 25)
        #self.assertEqual(size_long_fut, 4)

if __name__ == '__main__':
    unittest.main()
