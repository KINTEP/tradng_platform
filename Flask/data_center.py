import numpy as np
import string


count = 0

def increase():
    global count
    count += 1
    return count

ASSETS = [i for i in string.ascii_uppercase]

def symbols_data(asset, arr):
    ans = {k:v for k,v in zip(asset, arr)}
    return ans


ARRAY = np.array([-2.01583472, -0.87233992, -2.51540215, -0.42291782,  2.09608945,
        1.79244301, -1.70299504, -1.88730739,  1.50308736, -2.51500462,
       -0.6841724 , -1.32218118, -1.34554154, -2.40164442, -0.0106791 ,
        1.19521254, -0.8981209 ,  2.54252265,  0.00452417,  0.44133848,
        0.00553905, -0.0060737 ,  0.03412961, -0.62689789, -3.44028861,
        0.85758475])

SYMBOLS = symbols_data(asset=ASSETS, arr=ARRAY)

time = np.load("arr_primes.npy")

ALL_PRICES = {k:np.round(600+np.cumsum(np.cos(v*time)),2) for k,v in SYMBOLS.items()}

def get_close_price(symb):
    cnt = increase()
    prices = {k:v[cnt] for k,v in ALL_PRICES.items()}
    close = prices[symb]
    open = close
    high = close
    low = close
    return {"close": close, "open": open, "high": high, "low": low, "time": str(cnt),}