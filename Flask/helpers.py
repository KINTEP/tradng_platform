import numpy as np
import time


start = [100]

count = 0

def increase():
    global count
    count += 1
    return (count)

def get_market_data():
    #rnd = np.random.randn()
    #counter = 0
    OPEN = start[-1] + np.random.uniform(low=-0.01, high=0.03)
    CLOSE = OPEN * (1 + np.random.uniform(low=-0.02, high=0.02001))
    start.append(CLOSE)
    if CLOSE >= OPEN:
        HIGH = CLOSE *(1+np.random.uniform(low=0.00, high=0.01))
        LOW = OPEN *(1-np.random.uniform(low=0.00, high=0.01))
    if CLOSE < OPEN:
        HIGH = OPEN *(1+np.random.uniform(low=0.00, high=0.01))
        LOW = CLOSE *(1-np.random.uniform(low=0.00, high=0.01))
    data = {
        "time": str(increase()),
        "open": round(OPEN,2),
        "high": round(HIGH, 2),
        "close": round(CLOSE, 2),
        "low": round(LOW,2)
        }
    return data








"""

time = np.load("arr_primes.npy")

OPENS = np.cumsum(np.cos(-0.4198675449980002*time))
OPENS = abs(min(OPENS)) + OPENS + 10
CLOSE = 1.001*OPENS


def get_low_high(opens, close):
    H,L = [], []
    for a,b in zip(list(opens), list(close)):
        if a > b:
            h = 1.00212*b + b
            l = 0.998*a + a
        else:
            h = 1.00212*a + a
            l = 0.998*b + b
        H.append(h)
        L.append(l)
    return np.array(H), np.array(L)

def get_all_ohlc_prices(opens, close):
    H, L = get_low_high(opens, close)
    data = {
        "open": np.round(opens, 2),
        "high": np.round(H, 2),
        "low": np.round(L, 2),
        "close": np.round(close, 2)
    }
    return data


DATABASE = get_all_ohlc_prices(opens=OPENS, close=CLOSE)
"""
