from distutils.command.config import config
from hmac import new
from pprint import pprint

from matplotlib.pyplot import axis

from TradingLatino import TradingLatino

list_of_tickers = ['BTCUSDT','ETHUSDT','ADAUSDT','LTCUSDT','THETAUSDT','BNBUSDT','CAKEUSDT']
# list_of_tickers = ['BTCUSDT']
for tick in list_of_tickers:
    trade   = TradingLatino(simbolo=tick)
    pprint(tick)