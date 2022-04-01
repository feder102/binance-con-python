from asyncio import constants
from matplotlib.pyplot import axis
import config
import datetime
from ast import For
from binance import Client
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
top_volumenes = []
list_of_tickers = client.get_all_tickers()
top_tickers_volume = []
tickers = client.get_ticker()
cantidad_monedas = 3

def get_volumen(tick):
    return tick.get('volume')

for tick in tickers:
    if(len(top_tickers_volume) == 0):
        top_tickers_volume.append(tick)

    # sort by name (Ascending order)
    top_tickers_volume.sort(key=get_volumen,reverse=True)
    if (len(top_tickers_volume) <= cantidad_monedas):
        if (float(top_tickers_volume[len(top_tickers_volume)-1]['volume']) <= float(tick['volume'])):
            if(len(top_tickers_volume) == 0):
                top_tickers_volume.append(tick)
            else:
                print("*****************************************")
                print(top_tickers_volume, end='\n\n')
                print(len(top_tickers_volume))
                print("*****************************************")                
                top_tickers_volume.append(tick)
                del top_tickers_volume[len(top_tickers_volume)-2]

print("*****************************************")
print(top_tickers_volume, end='\n\n')
print("*****************************************")
# for tick in list_of_tickers:
#     if (tick['symbol'][-4:] != 'USDT' and tick['symbol'][-4:] != 'BUSD'):
#         continue
    
#     # print(tick['symbol'][-4:])
#     klines = client.get_historical_klines(tick['symbol'],client.KLINE_INTERVAL_8HOUR,"1 Mar, 2021")
#     # print(len(klines))
#     if(len(klines) == 0):
#         continue
    
#     prevClosePrice = klines[0][4]
#     for i in range (1,len(klines)-1):
#         if (prevClosePrice > klines[i][4]):
#             prevClosePrice = klines[i][4]
#             timestamp = datetime.datetime.fromtimestamp(int(str(klines[i][0])[:-3]))
#     # print(prevClosePrice)
#     # print("MINIMO DE "+ tick['symbol'] + " ES "+ str(prevClosePrice)+ " DE LA FECHA "+ timestamp.strftime('%d-%m-%Y %H:%M:%S'))
    
#     for tick_2 in list_of_tickers:
#         if tick_2['symbol'] == tick['symbol']:
#             currentPrice_of_Symbol = float(tick_2['price'])
#     if currentPrice_of_Symbol < float(prevClosePrice) + float(prevClosePrice) * 0.05:
#         print("ESTE ESTA EN MINIMOS ANUALES --------------> "+ tick['symbol'])
#         MINIMOS.append(tick['symbol'])
       
