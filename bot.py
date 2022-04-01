from ast import For
import config
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
list_of_tickers = client.get_all_tickers()
print(len(list_of_tickers)) 
busd_balance = client.get_asset_balance(asset='BUSD')

print("Balance: {}".format(busd_balance))

