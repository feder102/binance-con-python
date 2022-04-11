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

class Rsi:
    
    def __init__(self, simbolo='BTCUSDT') -> None:
        self.simbolo    = simbolo
        self.obtenerKlines()
        self.s_p_c       = [0,0,0]
        self.acum_comisiones = 0
        self.invertido   = 500
        self.dinero_final   = self.invertido
        self.ganancia   = 0
        self.porcentaje_ganancia = 0.02
        self.indice = 0
        self.aplicarEstrategia()

    
    def heikin_ashi(self,df):
        heikin_ashi_df = pd.DataFrame(index=df.index.values, columns=['open', 'high', 'low', 'close','Date'])
        heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        for i in range(len(df)):
            if i == 0:
                heikin_ashi_df.iat[0, 0] = df['open'].loc[0]
            else:
                heikin_ashi_df.iat[i, 0] = (heikin_ashi_df.iat[i-1, 0] + heikin_ashi_df.iat[i-1, 3]) / 2
        heikin_ashi_df['high'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['high']).max(axis=1)
        heikin_ashi_df['low'] = heikin_ashi_df.loc[:, ['open', 'close']].join(df['low']).min(axis=1)
        return heikin_ashi_df

    def leerKlinesCsv(self):
        self.klines = pd.read_csv(str(self.simbolo) + '_' + str(Client.KLINE_INTERVAL_4HOUR)+'.csv')
        self.klines    = pd.DataFrame(self.klines,columns=['Date','open','high','low','close','volume','close_time',
                        'quote_asset_volum','number_of_trade','taker_buy_base','take_buy_quote','ignore'])
        self.klines = self.heikin_ashi(self.klines)    

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
            with open( str(self.simbolo) + '_' + str(Client.KLINE_INTERVAL_4HOUR)+'.csv', 'w') as f:
                write = csv.writer(f)
                write.writerow(columns)
                write.writerows(self.klines)
            self.leerKlinesCsv()            
        
        
        self.high =     self.klines["high"].astype(float)
        self.low =      self.klines["low"].astype(float)
        self.close =    self.klines["close"].astype(float)

    def calcularIndicadores(self):
        self.rsi     = ta.rsi(self.close,length=2)
        self.ema_200  = ta.ema(self.klines.loc[:,"close"], length=200)
        self.ema_5  = ta.ema(self.klines.loc[:,"close"], length=5)
        # self.indice = self.ema_200[~np.isnan(self.ema_200)]
        self.high = self.klines["high"].astype(float)
        self.low = self.klines["low"].astype(float)
        self.close = self.klines["close"].astype(float)
        
    def compro_conSLPF(self,i):
        self.s_p_c = []
        stop = 99999999999999
        profit = 0
        cant = 0
        velas_atras = 6
        while(velas_atras > 0):
            if(stop > self.low.iloc[i-velas_atras]):
                stop = self.low.iloc[i-velas_atras]
            velas_atras = velas_atras - 1
        
        comprado_dinero =  self.dinero_final  
        cant = (comprado_dinero / self.close.iloc[i])        
        profit = stop + (stop * self.porcentaje_ganancia)
        self.s_p_c = np.append(self.s_p_c,[stop,profit,cant])
        #comisiones        
        self.comi = (self.s_p_c[2]*0.0075) * self.close.iloc[i]
        self.acum_comisiones =  self.acum_comisiones + self.comi
        self.dinero_final = 0
        return self.s_p_c
    
    def short_conSLPF(self,i):
        self.s_p_c = []
        stop = 0
        profit = 0
        cant = 0
        velas_atras = 6
        while(velas_atras > 0):
            if(stop <= self.high.iloc[i-velas_atras]):
                stop = self.high.iloc[i-velas_atras]
            velas_atras = velas_atras - 1
        
        #Esto es lo mismo que un long pero multiplico por -1 al resultado ya que es lo contrario
        comprado_dinero =  self.dinero_final  
        cant = (comprado_dinero / self.close.iloc[i])   
        profit = stop - (stop * self.porcentaje_ganancia)
        self.s_p_c = np.append(self.s_p_c,[stop,profit,cant])
        #comisiones        
        self.comi = (self.s_p_c[2]*0.0075) * self.close.iloc[i]
        self.acum_comisiones =  self.acum_comisiones + self.comi
        self.dinero_final = 0
        return self.s_p_c

    def vendo_long(self,i):
        #comisiones
        self.comi = (self.s_p_c[2]*0.0075) * self.close.iloc[i]
        self.acum_comisiones =  self.acum_comisiones + self.comi
        self.ganancia = self.s_p_c[2] * self.close.iloc[i]
        self.dinero_final = (self.ganancia) - self.comi
        # self.mostrarValoresVendidos(i)
        #muestro lo vendido y luego serializo
        self.s_p_c = [0,0,0]
    
    def vendo_short(self,i):
        #comisiones
        self.comi = (self.s_p_c[2]*0.0075) * self.close.iloc[i]
        self.acum_comisiones =  self.acum_comisiones + self.comi
        self.ganancia = self.s_p_c[2] * self.close.iloc[i]
        self.dinero_final = (self.ganancia) - self.comi
        # self.mostrarValoresVendidos(i)
        #muestro lo vendido y luego serializo
        self.s_p_c = [0,0,0]

    def rangoPrecio(self,i,stop_profit=1):#Por defecto verifica el profit
        if(self.high.iloc[i]>= self.s_p_c[stop_profit] and self.low.iloc[i] <= self.s_p_c[stop_profit]):
            return True
        else:
            return False

    def aplicarEstrategia(self):
        # Comienza la estrategia
        # Aca comienza el metodo de validacion
        self.calcularIndicadores()
        for i in range(199,len(self.klines)):

            if(self.s_p_c[2] != 0):
                if(self.ema_5.iloc[i] <= self.klines['close'].iloc[i]):
                    self.vendo_long(i)
                    continue
            
            #La ema de 200 esta por debajo, busco Long
            if(self.ema_200.iloc[i] < self.klines['close'].iloc[i]):
                if(self.rsi.iloc[i] <= 5):
                    if(self.ema_5.iloc[i] >= self.klines['close'].iloc[i]):
                        if(self.s_p_c[2] == 0):
                            self.s_p_c = self.compro_conSLPF(i)
            # else:
            #     if(self.rsi.iloc[i] >= 95):
            #         if(self.ema_5.iloc[i] <= self.klines['close'].iloc[i]):
            #             if(self.s_p_c[2] == 0):
            #                 self.s_p_c = self.short_conSLPF(i)
    
                
        
    def mostrarValores(self,i):
        print("*****************************************")
         #['STOCHRSId_14_14_3_3]
        print("PRECIO       : " + str(self.close.iloc[i]))
        print("RSI       : " + str(self.rsi.iloc[i]))
        date = datetime.datetime.fromtimestamp(int(self.klines['close_time'].iloc[i]/1000))
        print("FECHA   : " + str(datetime.datetime.strftime(date, '%d/%m/%Y')))
        print("*****************************************")

    def mostrarValoresComprados(self,i):
        print("*****************************************")
        print("PRECIO que compre  : " + str(self.close.iloc[i]))
        print("Cantidad comprada : " + str(self.s_p_c[2]))
        print("Cantidad Gastada USD: " + str(self.s_p_c[2] * self.close.iloc[i]))
        date = datetime.datetime.fromtimestamp(int(self.klines['close_time'].iloc[i]/1000))
        print("FECHA   COMPRA: " + str(datetime.datetime.strftime(date, '%d/%m/%Y')))
        print("*****************************************")

    def mostrarValoresVendidos(self,i):
        print("*****************************************")
        print("PRECIO que vendi  : " + str(self.close.iloc[i]))
        precio = float(self.s_p_c[2]) * float(self.close.iloc[i])
        print("Cantidad ganancia USD: " + str(precio))
        date = datetime.datetime.fromtimestamp(int(self.klines['close_time'].iloc[i]/1000))
        print("FECHA  VENDIDA : " + str(datetime.datetime.strftime(date, '%d/%m/%Y')))
        print("*****************************************")
    
    def mostrarValoresFinales(self):
        print("*****************************************")
        print("Dinero invertido  : " + str(self.invertido))
        print("Dinero comisiones  : " + str(self.acum_comisiones))
        print("Cantidad que no vendi : " + str(self.s_p_c[2]))
        print("Dinero en USD que me quedo : " + str(self.dinero_final))
        print("Precio de lo no vendido : " + str(self.s_p_c[2] * self.close.iloc[-1]))
        ganancias = 0
        if(self.s_p_c[2] != 0):
            ganancias = (self.s_p_c[2] * self.close.iloc[-1]) - self.invertido
            print("totales ganado : " + str(ganancias))
        else:
            ganancias = self.dinero_final 
            print("totales ganado : " + str(ganancias))
        print("*****************************************")        

    def getComisiones(self):
        return float(self.acum_comisiones)    

    def getGanancias(self):
        ganancias = 0
        if(self.s_p_c[2] != 0):
            ganancias = (self.s_p_c[2] * self.close.iloc[-1])  - self.invertido
        else:
            ganancias = self.dinero_final - self.invertido
        return ganancias