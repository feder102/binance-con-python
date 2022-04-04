import numpy as np
import datetime
from pprint import pprint

import pandas_ta as ta
import pandas as pd
from matplotlib.pyplot import axis
import talib as tv

import config
from binance import Client
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
#list_of_tickers = client.get_all_tickers()
tickers = client.get_ticker()
high = []
low = []
close = []
volume = []

klines = client.get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_4HOUR, "1 year ago UTC")
klines    = pd.DataFrame(klines,columns=['open_time','open','high','low','close','volume','close_time',
                                        'quote_asset_volum','number_of_trade','taker_buy_base','take_buy_quote','ignore'])

ema_10  = ta.ema(klines.loc[:,"close"], length=10)
ema_55  = ta.ema(klines.loc[:,"close"], length=55)

high = klines["high"].astype(float)
low = klines["low"].astype(float)
close = klines["close"].astype(float)
adx     = ta.adx(high, low, close)['ADX_14']

squeeze = ta.squeeze(high,low,close,lazybear=True)['SQZ_20_2.0_20_1.5_LB']

# Comienza la estrategia
#Aca comienza el metodo de validacion

if(squeeze.iloc[-1] >= squeeze.iloc[-2] and squeeze.iloc[-1] >= squeeze.iloc[-3] and adx.iloc[-1] >= adx.iloc[-2]):
    distancia_mayor_ema_10 = ema_10.iloc[-1] * 1.02
    distancia_menor_ema_10 = close.iloc[-1] - (ema_10.iloc[-1] * 0.02)
    distancia_mayor_ema_55 = ema_55.iloc[-1] * 1.02
    distancia_menor_ema_55 = close.iloc[-1] - (ema_55.iloc[-1] * 0.02)
    if(close.iloc[-1] <= distancia_mayor_ema_55 and close.iloc[-1] >= distancia_menor_ema_55):
        pprint("Aprueba la media de 55")
        if(close.iloc[-1] <= distancia_mayor_ema_10 and close.iloc[-1] >= distancia_menor_ema_10):
            pprint("Aprueba la media de 10")
            pprint("ACA COMPRO UN POCO")
else :
    if(squeeze.iloc[-1] >= squeeze.iloc[-2] and squeeze.iloc[-1] >= squeeze.iloc[-3] and adx.iloc[-1] >= adx.iloc[-2]):
        distancia_mayor_ema_10 = ema_10.iloc[-1] * 1.02
        distancia_menor_ema_10 = close.iloc[-1] - (ema_10.iloc[-1] * 0.02)
        distancia_mayor_ema_55 = ema_55.iloc[-1] * 1.02
        distancia_menor_ema_55 = close.iloc[-1] - (ema_55.iloc[-1] * 0.02)
        if(close.iloc[-1] >= distancia_mayor_ema_55 and close.iloc[-1] <= distancia_menor_ema_55):
            pprint("Aprueba la media de 55")
            if(close.iloc[-1] >= distancia_mayor_ema_10 and close.iloc[-1] <= distancia_menor_ema_10):
                pprint("Aprueba la media de 10")
                pprint("ACA VENDO UN POCO")

        

print("*****************************************")
pprint("PRECIO  : " + str(close.iloc[-1]))
pprint("EMA_10  : " + str(ema_10.iloc[-1]))
pprint("EMA_55  : " + str(ema_55.iloc[-1]))
pprint("ADX     : " + str(adx.iloc[-1]))
pprint("SQUEEZE : " + str(squeeze.iloc[-1]))
date = datetime.datetime.fromtimestamp(int(klines['close_time'].iloc[-1]/1000))
pprint("FECHA   : " + str(datetime.datetime.strftime(date, '%d/%m/%Y')))
print("*****************************************")