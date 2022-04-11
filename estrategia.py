from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import config
from binance import Client
from binance.enums import *
from TradingLatino import TradingLatino
from Estocastico import Estocastico
from Rsi  import Rsi

def obtenerTickerVolumen():
    client = Client(config.API_KEY, config.API_SECRET, tld = 'com')
    top_tickers_volume = []
    tickers = client.get_ticker()
    cantidad_monedas = 5
    for tick in tickers:
        if (len(top_tickers_volume) >= cantidad_monedas):
            if (float(top_tickers_volume[cantidad_monedas-1]['volume']) <= float(tick['volume'])):
                del top_tickers_volume[cantidad_monedas-1]
                top_tickers_volume.append(tick)
                top_tickers_volume.sort(key=get_volumen, reverse=True)
        else:
            top_tickers_volume.append(tick)
            top_tickers_volume.sort(key=get_volumen, reverse=True)
    return top_tickers_volume

def get_volumen(tick):
    a = float(tick.get('volume'))
    return float(tick.get('volume'))

list_of_tickers = []
list_of_tickers = np.append(list_of_tickers, ['BTCUSDT','ETHUSDT','ADAUSDT','LTCUSDT','THETAUSDT','BNBUSDT','CAKEUSDT'])
# list_of_tickers = ['CAKEUSDT']
# list_of_tickers = obtenerTickerVolumen()
ganancias = 0
comisiones = 0
lista_ganancias = []
lista_simbolos = []
for tick in list_of_tickers:
    # trade   = TradingLatino(simbolo=tick)
    trade   = Estocastico(simbolo=tick)
    # trade   = Rsi(simbolo=tick['symbol'])
    trade   = Rsi(simbolo=tick)
    ganancias += trade.getGanancias()
    
    lista_ganancias = np.append(lista_ganancias,trade.getGanancias())
    lista_simbolos = np.append(lista_simbolos,tick)

    comisiones += trade.getComisiones()
    # pprint(tick['symbol'])    
    pprint('Simbolo: ' + str(tick))
    pprint('Se gano USD: ' + str(trade.getGanancias()))
    pprint('Comisiones USD: ' + str(trade.getComisiones()))
    # pprint('Lo que se gano USD: ' + str(ganancias))
    # pprint('Lo que se gano ARS: ' + str(ganancias*200))
    # pprint('Comisiones que gaste: '+ str(comisiones))

posicion_y = np.arange(len(lista_simbolos))
plt.barh(posicion_y, lista_ganancias, align = "center")
plt.yticks(posicion_y,lista_simbolos)
plt.xlabel('Monedas')
plt.title("Ganancias")
plt.show()