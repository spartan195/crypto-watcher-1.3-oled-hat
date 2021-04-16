# TODO: Uncomment the lcd_1in44 line and comment the lcd_stub one if you want to run it on the display
#from lcd_1in44 import LCD
#from lcd_stub import LCD

from PIL import Image, ImageDraw, ImageFont

from typing import List, Tuple, Dict, Callable
import SH1106
import json
import config
import time
import datetime
import pytz
import math

import requests


def fetch_ohlc(symbol: str) -> List[Tuple[float, ...]]:
    res = requests.get(
        "https://api.binance.com/api/v3/klines", params={"symbol": symbol.upper(), "interval": "1h", "limit": 25})
    res.raise_for_status()

    json_data = json.loads(res.text)

    ohlc = []
    for data_entry in json_data:
        ohlc.append(tuple([float(data_entry[i]) for i in [1, 2, 3, 4]]))

    return ohlc


def fetch_crypto_data(symbol: str) -> Tuple[float, float, List[Tuple[float, ...]]]:
    ohlc_data = fetch_ohlc(symbol)
    price_current = ohlc_data[-1][-1]
    price_day_ago = ohlc_data[0][0]
    price_diff = price_current - price_day_ago

    return price_current, price_diff, ohlc_data


def render_candlestick(ohlc: Tuple[float, ...], x: int, y_transformer: Callable[[float], int], draw: ImageDraw):
    color = (255, 55, 55, 255) if ohlc[3] < ohlc[0] else (55, 255, 55, 255)
    draw.rectangle((x, y_transformer(
        max(ohlc[0], ohlc[3])), x + 2, y_transformer(min(ohlc[0], ohlc[3]))), fill=color)
    draw.line(
        (x + 1, y_transformer(ohlc[1]), x + 1, y_transformer(ohlc[2])), fill=color)


def render_ohlc_data(ohlc: List[Tuple[float, ...]], draw: ImageDraw):
    X_START = 18
    Y_START = 54
    HEIGHT = 50

    y_min = min([d[2] for d in ohlc])
    y_max = max([d[1] for d in ohlc])

    def y_transformer(y: float) -> int:
        multiplier = HEIGHT / (y_max - y_min)
        offset = int(multiplier * (y - y_min))
        return Y_START + HEIGHT - offset

    x = X_START + 24 * 4 + 1
    for candle_data in ohlc[::-1]:
        x -= 4
        render_candlestick(candle_data, x, y_transformer, draw)


def price_to_str(price: float) -> str:
    exp10 = math.floor(math.log10(abs(price)))
    num_decimals = int(min(5, max(0, 3 - exp10)))
    return "%.*f" % (num_decimals, price)


def main():
    disp = SH1106.SH1106()

    print("\r\1.3inch OLED")
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()

    # Create blank image for drawing.
    image1 = Image.new('1', (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image1)
    font = ImageFont.truetype("OpenSans-Regular.ttf", 20)
    font_small = ImageFont.truetype("OpenSans-Regular.ttf", 16)
    font_tiny = ImageFont.truetype("OpenSans-Regular.ttf", 12)
    print("***draw line")
    draw.line([(0, 0), (127, 0)], fill=0)
    draw.line([(0, 0), (0, 63)], fill=0)
    draw.line([(0, 63), (127, 63)], fill=0)
    draw.line([(127, 0), (127, 63)], fill=0)
    print("***draw rectangle")

    print("***draw text")
    draw.text((30, 0), 'Waveshare ', font=font_small, fill=0)
    draw.text((28, 20), 'DOGE ', font=font, fill=0)
    
    # image1=image1.rotate(180)
    disp.ShowImage(disp.getbuffer(image1))
    time.sleep(2)
    
    time.sleep(50)
    

if __name__ == "__main__":
    main()
