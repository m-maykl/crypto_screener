import pandas as pd
from tradingview_ta import TA_Handler
from binance.futures import Futures
from binance.spot import Spot
client_fut = Futures(key='', secret='')
client_spot = Spot(key='', secret='')

info_csv = {}

#//////////////////////
timeframe ="1m"

#\\\\\\\\\\\\\\\\\\\\\\



def indicators(symbol):
    price = float((client_fut.klines(symbol, timeframe, limit=1)[0])[4])
    prev_price = float((client_fut.klines(symbol, timeframe, limit=2)[0])[4])
    volume = float((client_fut.klines(symbol, timeframe, limit=2)[0])[5])
    prev_volume = float((client_fut.klines(symbol, timeframe, limit=3)[0])[5])
    try:
        order_book_fut = client_fut.depth(symbol, limit=500)
        order_book_spot = client_spot.depth(symbol, limit=1000)
        big_order_fut(symbol, order_book_fut,  price)
        big_order_spot(symbol, order_book_spot, price)
    except:
        print('Except', symbol)
        return
    try:
        response = TA_Handler(symbol=symbol, screener="crypto", exchange="binance", interval=timeframe)
        analysis = response.get_analysis().indicators
    except:
        try:
            symbol = symbol + 'PERP'
            response = TA_Handler(symbol=symbol, screener="crypto", exchange="binance", interval=timeframe)
            analysis = response.get_analysis().indicators
        except:
            print('Except', symbol)
            return
    sma20 = analysis.get('SMA20')
    sma50 = analysis.get('SMA50')
    sma100 = analysis.get('SMA100')
    sma200 = analysis.get('SMA200')
    calc_trend(sma20, sma50, sma100, sma200, price, prev_price, volume, prev_volume)
    calc_price_change(symbol, price, prev_price)



def calc_price_change(symbol, price, prevPrice):
    change = round((price / prevPrice - 1) * 100, 2)
    if abs(change) > 1.5:
        info = '#price_change' + symbol + ' change ' + str(change) + '%'
        write_csv(info)

        

def calc_trend(sma20, sma50, sma100, sma200, price, prev_price, volume, prev_volume):
    if abs(((sma200 / sma20) - 1) * 100) < 2:
        if abs(((sma200 / sma50) - 1) * 100) < 2:
            if abs(((sma200 / sma100) - 1) * 100) < 2:
                if abs(((price / prev_price) - 1) * 100) > 1:
                    if (volume / prev_volume) > 2:
                        info = '#trend' + symbol
                        write_csv(info)


def big_order_fut(symbol, order_book_fut, price):
    avg_volume = 0
    max_volume = 0
    max_price = ''
    full_list = order_book_fut.get('bids') + order_book_fut.get('asks')
    for i in full_list:
        avg_volume += float(i[1])
    avg_volume = avg_volume / len(full_list)
    for i in full_list:
        if float(i[1]) > max_volume:
            max_volume = float(i[1])
            max_price = i[0]
    if max_volume / avg_volume > 100 and abs((float(max_price) / price)-1)*100 < 2:
        info = '#big_order' + str(symbol) + ' ' + str(max_price) + ' ' + str(max_volume) + ' Futures'
        write_csv(info)


def big_order_spot(symbol, order_book_spot, price):
    avg_volume = 0
    max_volume = 0
    max_price = ''
    full_list = order_book_spot.get('bids') + order_book_spot.get('asks')
    for i in full_list:
        avg_volume += float(i[1])
    avg_volume = avg_volume / len(full_list)
    for i in full_list:
        if float(i[1]) > max_volume:
            max_volume = float(i[1])
            max_price = i[0]
    if max_volume / avg_volume > 100 and abs((float(max_price) / price) - 1) * 100 < 2:
        info = '#big_order' + str(symbol) + ' ' + str(max_price) + ' ' + str(max_volume) + ' Spot'
        write_csv(info)



def write_csv(info):
    print(info)
    with open('info.csv') as f:
        key = {k: v.strip() for k, v in (line.split(':') for line in f)}
        key = key.get('key')
    if key == 'write':
        info_csv.update({'change': info, 'key': 'read'})
        pd.Series(info_csv).to_csv('info.csv', index=True, header=False, sep=':')


while True:
    for i in client_fut.exchange_info().get('symbols'):
        if i.get('quoteAsset') == 'USDT':
            symbol = i.get('symbol')
            print(symbol)
            indicators(symbol)

