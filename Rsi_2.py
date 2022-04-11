from ast import Try
import decimal
from pickletools import long4
from click import style
import numpy as np
import datetime
import time
import csv

import mplfinance as mpf

import pandas_ta as ta
import pandas as pd

import config
from binance import Client
from binance.enums import *
from pandas import DataFrame

class Rsi_2:
    
    def __init__(self, simbolo='BTCUSDT') -> None:
        self.simbolo    = simbolo
        self.obtenerKlines()
        self.acum_comisiones = 0
        self.invertido   = 500
        self.dinero_final   = self.invertido
        self.ganancia   = 0
        self.cant       = 0
        self.profit     = 0
        self.stop       = 0
        self.fechas_compras_ventas = []
        self.aplicarEstrategia()

    def leerKlinesCsv(self):
        self.klines = pd.read_csv('csv/'+str(self.simbolo) + '_' + str(Client.KLINE_INTERVAL_4HOUR)+'.csv')
        self.klines    = pd.DataFrame(self.klines,columns=['Date','open','high','low','close','volume','close_time',
                        'quote_asset_volum','number_of_trade','taker_buy_base','take_buy_quote','ignore'])

    def obtenerKlines(self):
        # No API key/secret needed for this type of call
        client = Client()

        columns = [
            'Date', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
            'ignore'
        ]
        try:
            self.leerKlinesCsv()
        except:
            self.klines = client.get_historical_klines(self.simbolo, Client.KLINE_INTERVAL_4HOUR, "1 Jan, 2021")
            with open('csv/'+ str(self.simbolo) + '_' + str(Client.KLINE_INTERVAL_4HOUR)+'.csv', 'w') as f:
                write = csv.writer(f)
                write.writerow(columns)
                write.writerows(self.klines)
            self.leerKlinesCsv()            
        
        
        self.high =     self.klines["high"].astype(float)
        self.low =      self.klines["low"].astype(float)
        self.close =    self.klines["close"].astype(float)

    def calcularIndicadores(self):
        self.rsi     = ta.rsi(self.close,length=2)
        self.ema_200  = ta.ma("sma", self.klines.loc[:,"close"], length=200)
        self.ema_5  = ta.ma("sma", self.klines.loc[:,"close"], length=5)
        # self.indice = self.ema_200[~np.isnan(self.ema_200)]
        self.high = self.klines["high"].astype(float)
        self.low = self.klines["low"].astype(float)
        self.close = self.klines["close"].astype(float)
        
    def rangoPrecio(self,i,stop_o_profit='profit'):
        if(stop_o_profit == 'profit'):
            if(self.high.iloc[i]>= self.profit and self.low.iloc[i] <= self.profit):
                return True
            else:
                return False
        else:
            if(self.high.iloc[i]>= self.stop and self.low.iloc[i] <= self.stop):
                return True
            else:
                return False

    def fechasComprasVentas(self,i,trade='long',primera_vez=False):        
        timestamp = datetime.datetime.fromtimestamp(int(str(self.klines['Date'].iloc[i])[:-3]))
        timestamp = timestamp.strftime('%d-%m-%Y %H:%M:%S')
        if(primera_vez):
            objeto = Trade(trade,timestamp,self.klines['close'].loc[i],self.profit,self.stop)
        else:
            objeto = Trade(trade,timestamp,self.klines['close'].loc[i])
        self.fechas_compras_ventas = np.append(self.fechas_compras_ventas,objeto)

    def aplicarEstrategia(self):
        # Comienza la estrategia
        # Aca comienza el metodo de validacion
        self.calcularIndicadores()
        for i in range(199,len(self.klines)):

            if(self.cant != 0 and self.cant != -1):
                if(self.ema_5.iloc[i] > self.klines['close'].iloc[i]):
                    if(self.rangoPrecio(i,'profit')):
                        self.fechasComprasVentas(i,'venta_long_gano')
                        self.dinero_final = self.cant * self.klines['close'].iloc[i]
                        self.comi = self.dinero_final/(100*0.75)
                        self.acum_comisiones += self.comi
                        self.cant = 0
                    elif(self.rangoPrecio(i,'stop')):
                        self.fechasComprasVentas(i,'venta_long_perdio')
                        self.dinero_final = self.cant * self.klines['close'].iloc[i]
                        self.comi = self.dinero_final/(100*0.75)
                        self.acum_comisiones += self.comi
                        self.cant = 0
                continue
            if(self.cant == -1):#ES UN SHORT
                if(self.ema_5.iloc[i] < self.klines['close'].iloc[i]):
                    if(self.rangoPrecio(i,'profit')):
                        self.fechasComprasVentas(i,'venta_short_gano')
                        self.dinero_final = self.cant_ganador * self.klines['close'].iloc[i]
                        self.comi = self.dinero_final/(100*0.75)
                        self.acum_comisiones += self.comi
                        self.cant = 0
                    elif(self.rangoPrecio(i,'stop')):
                        self.fechasComprasVentas(i,'venta_short_perdio')
                        self.dinero_final = self.cant_perdedor * self.klines['close'].iloc[i]
                        self.comi = self.dinero_final/(100*0.75)
                        self.acum_comisiones += self.comi
                        self.cant = 0
                continue
            
            #La ema de 200 esta por debajo, busco Long
            if(self.ema_200.iloc[i] < self.klines['close'].iloc[i]):
                if(self.rsi.iloc[i] <= 5):
                    if(self.ema_5.iloc[i] >= self.klines['close'].iloc[i]):
                        if(self.cant == 0 and self.cant != -1):                            
                            self.cant = self.dinero_final/self.klines['close'].iloc[i]
                            self.comi = self.dinero_final/(100*0.75)
                            self.acum_comisiones += self.comi
                            self.profit = self.klines['close'].iloc[i] * 1.10
                            self.stop = self.klines['close'].iloc[i] - (self.klines['close'].iloc[i] * 0.05)
                            self.fechasComprasVentas(i,'long',True)
            else:
                if(self.rsi.iloc[i] >= 95):
                    if(self.ema_5.iloc[i] <= self.klines['close'].iloc[i]):
                        if(self.cant == 0 and self.cant != -1):                                                     
                            self.profit = self.klines['close'].iloc[i] - (self.klines['close'].iloc[i] * 0.10)
                            self.stop = self.klines['close'].iloc[i] * 1.05
                            self.cant_ganador = self.dinero_final/self.profit
                            self.cant_perdedor = self.dinero_final/self.stop
                            self.cant = -1
                            self.comi = self.dinero_final/(100*0.75)
                            self.acum_comisiones += self.comi
                            self.fechasComprasVentas(i,'short',True)

    def getComisiones(self):
        return float(self.acum_comisiones)
    
    def getFechasCompra(self):
        for fecha in self.fechas_compras_ventas:
            print("Fecha operacion: " + fecha.getDate())
            print("Nombre operacion: " + fecha.getName())
            print("Precio: " + str(fecha.getPrecio()))
            print("Profit: " + str(fecha.getProfit()))
            print("Stop  : " + str(fecha.getStop()))            

    def getGanancias(self):
        ganancias = 0
        if(self.cant != 0 and self.cant != -1):
            ganancias = (self.cant * self.close.iloc[-1])
        else:
            ganancias = self.dinero_final
        return ganancias

class Trade: 
    def __init__(self, name, date,precio='',profit='',stop=''): 
        self.name = name 
        self.date = date
        self.profit = profit
        self.stop = stop
        self.precio = precio
    
    def getName(self):
        return self.name
    def getDate(self):
        return self.date
    def getProfit(self):
        return self.profit 
    def getStop(self):
        return self.stop
    def getPrecio(self):
        return self.precio