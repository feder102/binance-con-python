import numpy as np
import datetime
import time

import pandas_ta as ta
import pandas as pd

import config
from binance import Client
from binance.enums import *
from pandas import DataFrame

class TradingLatino:
    # high    = []
    # low     = []
    # close   = []
    # simbolo = ''
    # klines  = DataFrame
    # ema_10  = []
    # ema_55  = []
    # adx     = []
    # squeeze = []
    
    def __init__(self, simbolo='BTCUSDT') -> None:
        self.simbolo    = simbolo
        self.obtenerKlines()
        self.btc_cant       = 0
        self.invertido   = 1000
        self.dinero_final   = self.invertido
        self.cant_vendida   = 0
        self.precio_a_vender= 0
        self.aplicarEstrategia()
        self.mostrarValoresFinales()
        

    def obtenerKlines(self):
        client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
        self.klines     = klines = client.get_historical_klines(self.simbolo, Client.KLINE_INTERVAL_4HOUR, "15 Days ago UTC")
        self.klines    = pd.DataFrame(klines,columns=['open_time','open','high','low','close','volume','close_time',
                                        'quote_asset_volum','number_of_trade','taker_buy_base','take_buy_quote','ignore'])
        self.high =     self.klines["high"].astype(float)
        self.low =      self.klines["low"].astype(float)
        self.close =    self.klines["close"].astype(float)

    def calcularIndicadores(self):
        self.ema_10  = ta.ema(self.klines.loc[:,"close"], length=10)
        self.ema_55  = ta.ema(self.klines.loc[:,"close"], length=55)
        self.high = self.klines["high"].astype(float)
        self.low = self.klines["low"].astype(float)
        self.close = self.klines["close"].astype(float)
        self.adx     = ta.adx(self.high, self.low, self.close)['ADX_14']
        self.squeeze = ta.squeeze(self.high,self.low,self.close,lazybear=True)['SQZ_20_2.0_20_1.5_LB']

    def aplicarEstrategia(self):
        # Comienza la estrategia
        # Aca comienza el metodo de validacion
        #39 es el primer objeto del adx con valor
        self.calcularIndicadores()
        for i in range(40,len(self.klines)):

            if(self.btc_cant != 0 and self.precio_a_vender <= self.close.iloc[i]):
                self.dinero_final = self.dinero_final + (self.close.iloc[i]*self.btc_cant)
                self.btc_cant = 0
                self.precio_a_vender = 0                
                self.mostrarValoresVendidos(i)

            if(self.adx.iloc[i] >= 23):
                if(self.squeeze.iloc[i] >= self.squeeze.iloc[i-1] and self.squeeze.iloc[i] >= self.squeeze.iloc[-3] and self.adx.iloc[i] >= self.adx.iloc[i-1]):
                    distancia_mayor_ema_10 = self.ema_10.iloc[i] * 1.01
                    distancia_menor_ema_10 = self.close.iloc[i] - (self.ema_10.iloc[i] * 0.01)
                    distancia_mayor_ema_55 = self.ema_55.iloc[i] * 1.03
                    distancia_menor_ema_55 = self.close.iloc[i] - (self.ema_55.iloc[i] * 0.03)
                    if(self.close.iloc[i] <= distancia_mayor_ema_55 and self.close.iloc[i] >= distancia_menor_ema_55):
                        if(self.close.iloc[i] <= distancia_mayor_ema_10 and self.close.iloc[i] >= distancia_menor_ema_10):
                            if(self.btc_cant == 0):
                                comprado_dinero =  self.dinero_final * 0.5
                                self.dinero_final = self.dinero_final - comprado_dinero
                                self.btc_cant = (comprado_dinero / self.close.iloc[i])
                                self.precio_a_vender = self.close.iloc[i] * 1.05
                                self.mostrarValoresComprados(i)
                                #self.mostrarValores(i)
                                time.sleep(1)     
                            else:
                                continue
                            
                # else :
                #     if(self.squeeze.iloc[i] >= self.squeeze.iloc[i-1] and self.squeeze.iloc[i] >= self.squeeze.iloc[-3] and self.adx.iloc[i] >= self.adx.iloc[i-1]):
                #         distancia_mayor_ema_10 = self.ema_10.iloc[i] * 1.02
                #         distancia_menor_ema_10 = self.close.iloc[i] - (self.ema_10.iloc[i] * 0.02)
                #         distancia_mayor_ema_55 = self.ema_55.iloc[i] * 1.02
                #         distancia_menor_ema_55 = self.close.iloc[i] - (self.ema_55.iloc[i] * 0.02)
                #         if(self.close.iloc[i] >= distancia_mayor_ema_55 and self.close.iloc[i] <= distancia_menor_ema_55):
                #             print("Aprueba la media de 55")
                #             if(self.close.iloc[i] >= distancia_mayor_ema_10 and self.close.iloc[i] <= distancia_menor_ema_10):
                #                 print("ACA VENDO UN POCO")
                #                 self.mostrarValores(i)
        
    def mostrarValores(self,i):
        print("*****************************************")
        print("PRECIO  : " + str(self.close.iloc[i]))
        print("EMA_10  : " + str(self.ema_10.iloc[i]))
        print("EMA_55  : " + str(self.ema_55.iloc[i]))
        print("ADX     : " + str(self.adx.iloc[i]))
        print("SQUEEZE : " + str(self.squeeze.iloc[i]))
        date = datetime.datetime.fromtimestamp(int(self.klines['close_time'].iloc[i]/1000))
        print("FECHA   : " + str(datetime.datetime.strftime(date, '%d/%m/%Y')))
        print("*****************************************")

    def mostrarValoresComprados(self,i):
        print("*****************************************")
        print("PRECIO que compre  : " + str(self.close.iloc[i]))
        print("Cantidad comprada : " + str(self.btc_cant))
        print("Cantidad Gastada USD: " + str(self.btc_cant * self.close.iloc[i]))
        print("*****************************************")

    def mostrarValoresVendidos(self,i):
        print("*****************************************")
        print("PRECIO que vendi  : " + str(self.close.iloc[i]))
        print("Cantidad ganancia USD: " + str(float(self.btc_cant * self.close.iloc[i])))
        print("*****************************************")
    
    def mostrarValoresFinales(self):
        print("*****************************************")
        print("Dinero invertido  : " + str(self.invertido))
        print("Cantidad que no vendi : " + str(self.btc_cant))
        print("Precio de lo no vendido : " + str(self.btc_cant * self.close.iloc[-1]))
        print("totales ganado : " + str(self.dinero_final - self.invertido))
        print("*****************************************")